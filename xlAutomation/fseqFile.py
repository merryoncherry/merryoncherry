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
import xlAutomation.xsqFile

# python fseqFile.py c:\users\Chuck\Documents\xlightsShows\2022_Xmas\12Days_McKenzie_FPD.fseq
# python fseqFile.py -x c:\users\chuck\documents\xlightsShows\2022_xmas c:\users\Chuck\Documents\xlightsShows\2022_Xmas\12Days_McKenzie_FPD.fseq
# python fseqFile.py -s c:\users\chuck\documents\xlightsShows\2022_xmas\12Days_McKenzie_FPD.xsq -x c:\users\chuck\documents\xlightsShows\2022_xmas c:\users\Chuck\Documents\xlightsShows\2022_Xmas\12Days_McKenzie_FPD.fseq
# python fseqFile.py "c:\users\Chuck\Documents\xlightsShows\2022_Xmas\Boogie Man.eseq"
# python fseqFile.py -x c:\users\chuck\documents\xlightsShows\2022_xmas "c:\users\Chuck\Documents\xlightsShows\2022_Xmas\Boogie Man.eseq"
# python fseqFile.py -s "c:\users\chuck\documents\xlightsShows\2022_xmas\Event_NMBCSeq.xsq" -x  c:\users\chuck\documents\xlightsShows\2022_xmas "c:\users\Chuck\Documents\xlightsShows\2022_Xmas\Boogie Man.eseq"

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
    def __init__(self, name, mtype, startch, nch):
        self.name = name
        self.startch = startch
        self.nch = nch
        self.empty = True
        self.typ = mtype
        self.crc = 0
        self.simple = False # DMX, more or less than 3 colors, not "simple"
        self.r = 0 # Offset from first channel assigned to a pixel
        self.g = 1
        self.b = 2

    def __repr__(self):
        return self.name + ":" + str(self.startch) + "," + str(self.nch)

def readControllersAndModels(xldir, controllers, ctrlbyname, models, osmodels):
    xmodels   = xml.dom.minidom.parse(xldir+'/xlights_rgbeffects.xml')
    xnetworks = xml.dom.minidom.parse(xldir+'/xlights_networks.xml')

    xnd = xnetworks.documentElement
    if (xnd.tagName != 'Networks'):
        raise Exception('Root not "Networks"')

    startch = 1
    for cn in xnd.childNodes:
        if cn.nodeType == xml.dom.Node.ATTRIBUTE_NODE or cn.nodeType == xml.dom.Node.TEXT_NODE:
            continue
        if cn.tagName != 'Controller':
            continue
        controllers.append((startch, cn.getAttribute('Name')))
        ctrlbyname[cn.getAttribute('Name')] = startch
        #if cn.hasAttribute('IP'):
        #    # TODO by address?  Universes are what exactly?
        #   ctrbyname[cn.getAttribute('IP')] = startch
        #   pass
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
            mtyp = mdl.getAttribute('DisplayAs')
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
            elif chstr[0] == '#':
                # Huh, seems to be an IP:universe:channel or universe:channel
                #(ctrladdr,univ,ch) = chstr[1:].split(':')
                # TODO we would need to find the channel for the universe or something
                #channel = ctrlbyname[ctrladdr]
                continue
            elif chstr[0] == '>':
                # Shadow model name:channel such as ">Spinner 2:1"
                continue
            else:
                raise Exception("Unknown channel string: "+chstr)
            nmrec = ModelRec(name, mtyp, channel, -1)
            if mdl.hasAttribute('StringType'):
                strtyp = mdl.getAttribute('StringType')
                if strtyp == 'RGB Nodes':
                    nmrec.r = 0
                    nmrec.g = 1
                    nmrec.b = 2
                    nmrec.simple = True
                if strtyp == 'RBG Nodes':
                    nmrec.r = 0
                    nmrec.g = 2
                    nmrec.b = 1
                    nmrec.simple = True
                if strtyp == 'GRB Nodes':
                    nmrec.r = 1
                    nmrec.g = 0
                    nmrec.b = 2
                    nmrec.simple = True
                if strtyp == 'GBR Nodes':
                    nmrec.r = 2
                    nmrec.g = 0
                    nmrec.b = 1
                    nmrec.simple = True
                if strtyp == 'BRG Nodes':
                    nmrec.r = 1
                    nmrec.g = 2
                    nmrec.b = 0
                    nmrec.simple = True
                if strtyp == 'BGR Nodes':
                    nmrec.r = 2
                    nmrec.g = 1
                    nmrec.b = 0
                    nmrec.simple = True
            for dc in mdl.childNodes:
                if dc.nodeType == xml.dom.Node.ATTRIBUTE_NODE or dc.nodeType == xml.dom.Node.TEXT_NODE:
                    continue
                if (dc.tagName != 'dimmingCurve'):
                    continue
                for ddc in dc.childNodes:
                    if ddc.nodeType == xml.dom.Node.ATTRIBUTE_NODE or ddc.nodeType == xml.dom.Node.TEXT_NODE:
                        continue
                    if (ddc.tagName != 'all'):
                        continue
                    if ddc.hasAttribute('gamma'):
                        nmrec.gamma = float(ddc.getAttribute('gamma'))
            models.append(nmrec)

    # Oh heck how to calculate channels per model
    #  Will we eventually just have to add specific logic?
    smodels = sorted(models, key = lambda m : m.startch)
    for i in range(0, len(smodels)):
        if i == len(smodels)-1 :
            continue
        smodels[i].nch = smodels[i+1].startch - smodels[i].startch
    for m in smodels:
        osmodels.append(m)

def calculateFSEQSummary(sfile, controllers, ctrlbyname, models, smodels, ttracks, keepmodelspertiming):
    hjson = {}
    with open(sfile, 'rb') as fh:
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
        chrangelist = []
        comp = 0
        ccount = 0
        stepms = 50

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
            chrangelist.append((modelstart, modelsize))

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
                blks = (compandblks & 240) * 16
                blks += read8bit(fh)
                #print ("blocks: "+str(blks))
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
                seenEmpty = False
                hjson['compblocklist'] = []
                for i in range(0, blks):
                    framenum = read32bit(fh)
                    blocksize = read32bit(fh)
                    if not blocksize:
                        seenEmpty = True
                        if framenum:
                            raise Exception("Empty block ("+str(i)+") with frame number ("+str(framenum)+") assigned")
                        continue
                    if seenEmpty:
                        raise Exception("Empty blocks followed by nonempty blocks "+str(i))
                    compblocklist.append((framenum, blocksize))
                    hjson['compblocklist'].append({'framenum':framenum, 'blocksize':blocksize})

                # Sparse range map
                # Sparse ranges: 3 ch num, 3 num ch
                hjson['chranges'] = []
                for i in range(0, nranges):
                    startnum = read24bit(fh)
                    chcount = read24bit(fh)
                    chrangelist.append((startnum, chcount))
                    hjson['chranges'].append({'startch':startnum, 'chcount':chcount})
            if not chrangelist:
                chrangelist.append((1, ccount))

            hjson['headers'] = {}
            vlheaders = {}
            while (fh.tell() + 4 <= off2chdata):
                #print ("At "+str(fh.tell())+" vs " + str(shdrlen))
                hlen = read16bit(fh) - 4
                hname = str(fh.read(2), 'utf-8')
                #print ("Header "+hname+": "+str(hlen))
                hval = str(fh.read(hlen), 'utf-8')
                vlheaders[hname] = hval
                hjson['headers'][hname] = hval[:-1]

            fh.seek(off2chdata)

        #print("Decode "+str(nframes)+" frames")
        curframe = 0
        curms = 0
        globalcrc = 0

        hjson['framecrcs']=[]

        for blk in compblocklist:
            (sframe, dsz) = blk
            if (sframe != curframe):
                raise Exception("Unexpected start frame "+str(sframe)+" vs "+str(curframe)+" ; " + str(dsz) + " / "+str(len(compblocklist)))
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

                # Advance to current frame and adjust CRC
                for tt in ttracks:
                    if tt.current >= len(tt.entlist):
                        continue
                    while curms >= tt.entlist[tt.current].endms:
                        tt.current += 1
                        if tt.current >= len(tt.entlist):
                            break
                    if tt.current >= len(tt.entlist):
                        continue
                    if curms >= tt.entlist[tt.current].startms:
                        tt.entlist[tt.current].crc = binascii.crc32(frame, tt.entlist[tt.current].crc)

                # Go through each model and do some CRC there
                for m in smodels:
                    sch = m.startch
                    ech = m.startch + m.nch if m.nch > 0 else ccount

                    # See if we have data for the model, considering sparse range
                    curoff = 0
                    for schrng in chrangelist:
                        (rstart, rcnt) = schrng
                        if sch >= rstart and ech <= rstart+rcnt:
                            msub = frame[curoff + sch - rstart : curoff + ech - rstart]
                            # CRC for model in its entirety
                            m.crc = binascii.crc32(msub, m.crc)
                            allz = allzero(msub)
                            if not allz :
                                m.empty = False
                            if keepmodelspertiming:
                                # CRC for model in each timing section
                                for tt in ttracks:
                                    if tt.current >= len(tt.entlist):
                                        continue
                                    mmm = tt.entlist[tt.current].models
                                    if m.name not in mmm:
                                        mmm[m.name] = ModelRec(m.name, m.typ, m.startch, m.nch)
                                    mmm[m.name].crc = binascii.crc32(msub, mmm[m.name].crc)
                                    if not allz:
                                        mmm[m.name].empty = False

                        curoff += rcnt


                globalcrc = binascii.crc32(frame, globalcrc)
                foffset += stepsz
                curframe = curframe + 1
                curms = curms + stepms

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
            hjson['modelcrcs'].append({'name':m.name,  'type':m.typ, 'crc':m.crc & 0xFFFFFFFF})

        # Add CRCs by time
        hjson['ttracks'] = {}
        for tt in ttracks:
            hjson['ttracks'][tt.name] = []
            for ent in tt.entlist:
                o =  {"label": ent.label, "start":ent.startms, "end":ent.endms, 'crc':ent.crc & 0xFFFFFFFF, "models":[]}
                hjson['ttracks'][tt.name].append(o)
                o = o["models"]
                for mn in ent.models.keys():
                    m = ent.models[mn]
                    if (m.empty):
                        continue;
                    o.append({"name": m.name, 'type':m.typ, "crc": m.crc&0xFFFFFFFF})
    return hjson

if __name__ == '__main__':
    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-x', '--xlights',  help="Path to xlights_rgbeffects.xml and xlights_networks.xml")
    parser.add_argument('-s', '--sequence', help="Path to effect sequence .xsq file")
    parser.add_argument('-o', '--output',   help="Path to output file")
    parser.add_argument('flist', nargs=1, help='sequence binary files')

    args = parser.parse_args()

    controllers = []
    ctrlbyname = {}
    models = []
    smodels = []
    ttracks = []

    if args.xlights:
        readControllersAndModels(args.xlights, controllers, ctrlbyname, models, smodels)

    if args.sequence:
        xlAutomation.xsqFile.readSequenceTimingTrack(args.sequence, ttracks)

    hjson = calculateFSEQSummary(args.flist[0], controllers, ctrlbyname, models, smodels, ttracks, True)

    if (args.output) :
        with open(args.output, 'w') as fh:
            fh.write(json.dumps(hjson, indent=2))
    else:
        print(json.dumps(hjson, indent=2))

    #print(str(controllers))
    #print(str(smodels))
