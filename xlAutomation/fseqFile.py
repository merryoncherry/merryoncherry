#Python module to read fseq files and summarize them
# See https://github.com/FalconChristmas/fpp/blob/master/docs/FSEQ_Sequence_File_Format.txt
import argparse
import binascii
import io
import json
import os
import sys
import xml.dom.minidom
import zstandard

# python fseqFile.py c:\users\Chuck\Documents\xlightsShows\2022_Xmas\12Days_McKenzie_FPD.fseq
# python fseqFile.py -x c:\users\chuck\documents\xlightsShows\2022_xmas c:\users\Chuck\Documents\xlightsShows\2022_Xmas\12Days_McKenzie_FPD.fseq
# python fseqFile.py -x c:\users\chuck\documents\xlightsShows\2022_xmas -s  c:\users\chuck\documents\xlightsShows\2022_xmas c:\users\Chuck\Documents\xlightsShows\2022_Xmas\12Days_McKenzie_FPD.fseq
# python fseqFile.py "c:\users\Chuck\Documents\xlightsShows\2022_Xmas\Boogie Man.eseq"
# python fseqFile.py -x c:\users\chuck\documents\xlightsShows\2022_xmas "c:\users\Chuck\Documents\xlightsShows\2022_Xmas\Boogie Man.eseq"
# python fseqFile.py -x c:\users\chuck\documents\xlightsShows\2022_xmas -s  c:\users\chuck\documents\xlightsShows\2022_xmas "c:\users\Chuck\Documents\xlightsShows\2022_Xmas\Boogie Man.eseq"

def read8bit(f):
    arr = f.read(1)
    return int(arr[0])

def read16bit(f):
    arr = f.read(2)
    return int(arr[0]) + int(arr[1])*256

def read24bit(f):
    arr = f.read(3)
    return int(arr[0]) + int(arr[1])*256 + int(arr[2])*65536

def read32bit(f):
    arr = f.read(4)
    return int(arr[0]) + int(arr[1])*256 + int(arr[2])*65536 + int(arr[3])*65536*256

def allzero(d):
    for b in d:
        if b != 0:
            return False
    return True

class ModelRec:
    def __init__(self, name, startch, nch):
        self.name = name
        self.startch = startch
        self.nch = nch
        self.empty = True
        self.crc = 0

    def __repr__(self):
        return self.name + ":" + str(self.startch) + "," + str(self.nch)

if __name__ == '__main__':
    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-x', '--xlights',  help="Path to xlights_rgbeffects.xml and xlights_networks.xml")
    parser.add_argument('-s', '--sequence', help="Path to effect sequence .xsq files")
    parser.add_argument('flist', nargs='*', help='sequence binary files')

    args = parser.parse_args()

    controllers = []
    ctrlbyname = {}
    models = []
    if args.xlights:
        xmodels   = xml.dom.minidom.parse(args.xlights+'/xlights_rgbeffects.xml')
        xnetworks = xml.dom.minidom.parse(args.xlights+'/xlights_networks.xml')

        xnd = xnetworks.documentElement
        if (xnd.tagName != 'Networks'):
            raise Exception('Root not "Networks"')
        #for attrName, attrValue in n.attributes.items():
        #    raise Exception('Root "xrgb" unexpected attribute "'+attrName+'"')
        startch = 1
        for cn in xnd.childNodes:
            if cn.nodeType == xml.dom.Node.ATTRIBUTE_NODE or cn.nodeType == xml.dom.Node.TEXT_NODE:
                continue
            if cn.tagName != 'Controller':
                continue
            controllers.append((startch, cn.getAttribute('Name')))
            ctrlbyname[cn.getAttribute('Name')] = startch
            for net in cn.childNodes:
                if net.nodeType == xml.dom.Node.ATTRIBUTE_NODE or net.nodeType == xml.dom.Node.TEXT_NODE:
                    continue
                if (net.tagName != 'network'):
                    continue
                startch += int(net.getAttribute('MaxChannels'))

        xnd = xmodels.documentElement
        if (xnd.tagName != 'xrgb'):
            raise Exception('Root not "xrgb"')
        for grp in xnd.childNodes:
            if grp.nodeType == xml.dom.Node.ATTRIBUTE_NODE or grp.nodeType == xml.dom.Node.TEXT_NODE:
                continue
            if grp.tagName != 'models':
                continue
            for mdl in grp.childNodes:
                if mdl.nodeType == xml.dom.Node.ATTRIBUTE_NODE or mdl.nodeType == xml.dom.Node.TEXT_NODE:
                    continue
                if (mdl.tagName != 'model'):
                    continue
                name = mdl.getAttribute('name')
                chstr = mdl.getAttribute('StartChannel')
                channel = -1
                if (chstr[0] >= '0' and chstr[0] <= '9') :
                    channel = int(chstr)
                elif chstr[0] == '@':
                    continue
                elif chstr[0] == '!':
                    # TODO Look up controller
                    (ctrlnm,offset) = chstr[1:].split(':')
                    channel = ctrlbyname[ctrlnm]+int(offset)-1
                else:
                    raise Exception("Unknown channel string: "+chstr)
                models.append(ModelRec(name, channel, -1))

        # Oh heck how to calculate channels per model
        #  Will we eventually just have to add specific logic?
        smodels = sorted(models, key = lambda m : m.startch)
        for i in range(0, len(smodels)):
            if i == len(smodels)-1 :
                continue
            smodels[i].nch = smodels[i+1].startch - smodels[i].startch

    hjson = {}
    with open(args.flist[0], 'rb') as fh:
        hdr = fh.read(4)
        shdr = str(hdr, 'utf-8')
        #print(shdr)
        isEseq = True if (shdr == 'ESEQ') else False
        if (shdr != 'PSEQ' and shdr != 'ESEQ' and shdr != 'FSEQ'):
            raise Exception("Not a PSEQ file")
        hjson['hdr4'] = shdr

        # Things we will need to read the frames
        nframes = 0 # Number of frames
        stepsz = 0 # Size of uncompressed frame
        compblocklist = [] # Bit about reading the file and decompressing
        comp = 0
        ccount = 0

        if (isEseq):
            off2chdata = 20
            minver = 0
            majver = 2

            modelcnt = read32bit(fh)
            stepsz = read32bit(fh)
            modelstart = read32bit(fh)
            ccount = modelsize = read32bit(fh)

            hjson["modelcount"] = modelcnt
            hjson["stepsize"] = stepsz
            hjson["modelstart"] = modelstart
            hjson["modelsize"] = modelsize

            #Noting the lack of # of frames, frame timing, or any compression.  This format sucks.
            fh.seek(0, os.SEEK_END)
            nframes = int((fh.tell() - off2chdata) / stepsz)
            compblocklist.append((0, nframes * stepsz))
            fh.seek(off2chdata, os.SEEK_SET)

        else:
            off2chdata = read16bit(fh)
            minver = read8bit(fh)
            majver = read8bit(fh)

            isv1 = True if majver == 1 else False

            #print("offset to channel data: "+str(off2chdata))
            hjson['chdata_offset']=off2chdata
            #print("Version "+str(majver)+'.'+str(minver))
            hjson['majver'] = majver
            hjson['minver'] = minver

            shdrlen = read16bit(fh)
            ccount = read32bit(fh)
            stepsz = int((ccount + 3) / 4) * 4
            nframes = read32bit(fh)
            stepms = read8bit(fh)
            reserved = read8bit(fh)

            hjson['fixedhdr'] = shdrlen
            hjson['channels'] = ccount
            hjson['frames'] = nframes
            hjson['msperframe'] = stepms
            hjson['reserved1'] = reserved

            if (isv1):
                univcnt = read16bit(fh)
                univsz = read16bit(fh)
                gamma = read8bit(fh)
                colorenc = read8bit(fh)
                reserved = read16bit(fh)
                hjson['univcnt'] = univcnt
                hjson['universesize'] = univsz
                hjson['gamma'] = gamma
                hjson['colorenc'] = colorenc
                hjson['reserved2'] = reserved

                # Double check this math, is it rounded up?
                compblocklist.append((0, nframes*ccnt))
            else:
                compandblks = read8bit(fh)
                comp = compandblks & 15
                blks = compandblks & 240 * 16
                blks += read8bit(fh)
                nranges = read8bit(fh)
                reserved = read8bit(fh)
                uuid1 = read32bit(fh)
                uuid2 = read32bit(fh)

                hjson['compression'] = comp
                hjson['compblks'] = blks
                hjson['nsparseranges'] = nranges
                hjson['reserved2'] = reserved
                hjson['uuid1'] = uuid1
                hjson['uuid2'] = uuid2

                # Compression blocks
                # Compress block index: 4 frame num, 4 length
                hjson['compblocklist'] = []
                for i in range(0, blks):
                    framenum = read32bit(fh)
                    blocksize = read32bit(fh)
                    compblocklist.append((framenum, blocksize))
                    hjson['compblocklist'].append({'framenum':framenum, 'blocksize':blocksize})

                # Sparse range map
                # Sparse ranges: 3 ch num, 3 num ch
                hjson['chranges'] = []
                chrangelist = []
                for i in range(0, nranges):
                    startnum = read24bit(fh)
                    chcount = read24bit(fh)
                    chrangelist.append((startnum, chcount))
                    hjson['chranges'].append({'startch':startnum, 'chcount':chcount})

            hjson['headers'] = {}
            vlheaders = {}
            while (fh.tell() + 4 <= off2chdata):
                #print ("At "+str(fh.tell())+" vs " + str(shdrlen))
                hlen = read16bit(fh) - 4
                hname = str(fh.read(2), 'utf-8')
                #print ("Header "+hname+": "+str(hlen))
                hval = str(fh.read(hlen), 'utf-8')
                vlheaders[hname] = hval
                hjson['headers'][hname] = hval

            fh.seek(off2chdata)

        #print("Decode "+str(nframes)+" frames")
        curframe = 0
        globalcrc = 0

        hjson['framecrcs']=[]

        for blk in compblocklist:
            (sframe, dsz) = blk
            if (sframe != curframe):
                raise Exception("Unexpected start frame "+str(sframe)+" vs "+str(curframe))
            raw = fh.read(dsz)
            #print("Read of " + str(dsz) + " got "+str(len(raw)))
            if (comp == 1):
                raw = zstandard.ZstdDecompressor().decompress(raw, max_output_size=nframes*stepsz) # This is conservative, covers WHOLE sequence
            if (comp == 2):
                raise ("Need to implement zlib")

            foffset = 0
            #print("Raw len: "+str(len(raw))+"; step size "+str(stepsz))
            while (foffset < len(raw)) :
                frame = raw[foffset: foffset + stepsz]
                if (not allzero(frame)):
                    crc32 = (binascii.crc32(frame) & 0xFFFFFFFF)
                    hjson['framecrcs'].append({'frame': curframe, 'crc': crc32})

                # Go through each model and do some CRC there
                for m in smodels:
                    sch = m.startch
                    ech = m.startch + m.nch if m.nch > 0 else ccount

                    # This is in error for sparse ranges
                    msub = frame[sch : ech]
                    m.crc = binascii.crc32(msub, m.crc)
                    if not allzero(msub) :
                        m.empty = False

                globalcrc = binascii.crc32(frame, globalcrc)
                foffset += stepsz
                curframe = curframe + 1

            if (foffset != len(raw)):
                raise Exception("Partial frame")

        if (curframe != nframes):
            raise Exception("Frame count mismatch")

        hjson['globalcrc'] =  globalcrc & 0xFFFFFFFF

        # Add model CRCs
        hjson['modelcrcs'] = []
        mbyname = sorted(models, key = lambda m : m.name)
        for m in mbyname:
            if m.empty:
                continue
            hjson['modelcrcs'].append({'name':m.name, 'crc':m.crc & 0xFFFFFFFF})

        print(json.dumps(hjson, indent=2))
        #print(str(controllers))
        #print(str(smodels))
