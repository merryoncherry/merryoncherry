# The purpose of this is to generate a track of a single color that captures the essence of the scene.
#  This could be used for anything that needs "just one color", like a flood light.
#  However, the intended target is more "interesting".  It is the DMX wireless wands / bracelets / etc.,
#    which do need a color, but also can only take an update a few times a second, and you also
#    may not want to run the transmitter continuously in case it causes interference.
# So the basic operation of this program is:
#  Look at the primary color / secondary color in each frame - yes, it uses the fseq file for this
#   You can look at a few models or all of them
#  Get a sense of the overall energy of the frame - when this changes, it is a good time to trigger the color
# There are some fine-tuning technical parameters:
#   Input files:
#     This needs the .fseq file, rgb_effects, and networks; that's how we tell how to read the colors
#     The model to use, or all RGB models by default
#   Transmitter control:
#     Name of the transmitter to use in the sequence
#     How long to strobe the transmitter - .075-.1 seconds works well
#     Minimum time between strobes
#     Channel data for the strobe - Ch 1 control (default 85), Ch 2 group (default 0)
#     Time advance for the strobe - in case of delay between strobe and wand action
#     Time advance for the color change before strobe - in case of delay between color and wand strobe
#   Color control:
#     Use brightness or do not use brightness?
#     Use a timing track to trigger?
#     Use the secondary color also?

import argparse
import textwrap
import sys
import zstandard

sys.path.append('../merryoncherry')
import xlAutomation.fseqFile
import xlAutomation.xsqFile

# H in the range [0, 360), and S, V in the range [0, 1].
# Will invert the gamma correction as part of calculation
def rgb_to_hsv(r, g, b, invgamma):
    r, g, b = (r / 255.0) ** invgamma, (g / 255.0) ** invgamma, (b / 255.0) ** invgamma
    M, m = max(r, g, b), min(r, g, b)
    C = M - m
    
    # Hue calculation
    if C == 0:
        H = 0
    elif M == r:
        H = (60 * ((g - b) / C) + 360) % 360
    elif M == g:
        H = (60 * ((b - r) / C) + 120) % 360
    elif M == b:
        H = (60 * ((r - g) / C) + 240) % 360

    # Saturation calculation
    if M == 0:
        S = 0
    else:
        S = C / M

    # Return
    return H, S, M

# S and V are 0-100
def hsv_to_rgb(h, s, v):
    s = s / 100.0
    v = v / 100.0

    if (s < 0.0 or s > 1.0):
        raise Exception("HSV S out of range")
    if (v < 0.0 or v > 1.0):
        raise Exception("HSV V out of range")

    if s == 0:
        r = g = b = v
    else:
        h /= 60.0  # sector 0 to 5
        i = int(h)
        f = h - i  # fractional part of h
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))
        
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:  # i == 5
            r, g, b = v, p, q

    return int(r * 255), int(g * 255), int(b * 255)


class Histogram:
    def __init__(self):
        self.minV = 1
        self.maxV = 0
        self.nNonBlack = 0
        self.nSamples = 0
        #self.HHist = [0] * 181 # Hue histogram; if it is gray it will be elsewhere (GHist)
        self.GHist = [0] * 101 # Grayscale colors (not in HHist)
        self.VHist = [0] * 101 # Brightness overall - all nonblack
        #self.SHist = [0] * 101 # Saturation histogram
        self.HSHist = [0] * (180*101) # Hue and saturation together; grayscale is not in here, see GHist

    def update(self, model, raw):
        rp = 0
        l = len(raw)
        invgamma = 1.0/model.gamma
        while rp+2 < l:
            r = raw[rp + model.r]
            g = raw[rp + model.g]
            b = raw[rp + model.b]
            rp = rp + 3
            self.nSamples = self.nSamples + 1
            h, s, v = rgb_to_hsv(r, g, b, invgamma)

            if v < self.minV:
                self.minV = v
            if v*100 > self.maxV:
                self.maxV = v * 100
            if r == 0 and g == 0 and b == 0:
                continue

            self.nNonBlack = self.nNonBlack + 1

            if (s == 0):
                self.GHist[int(v * 100)] += 1
                self.VHist[int(v * 100)] += 1
            else :
                self.VHist[int(v * 100)] += 1
                #self.HHist[int(h / 2)] += 1
                #self.SHist[int(s * 100)] += 1
                self.HSHist[int(h/2) * 101 + int(s*100)] += 1

class CChoice:
    def __init__(self):
        self.H = 0
        self.S = 0
        self.VTyp = 0
        self.popularity = 0

class FrameInfo:
    def __init__(self):
        self.choices = []
        self.nLit = 0
        self.vMax = 0
        self.ms = 0

def calculateFSEQColorSummary(hjson, sfile, controllers, ctrlbyname, models, frames, srcmodels):
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

            modelcnt = xlAutomation.fseqFile.read32bit(fh)
            stepsz = xlAutomation.fseqFile.read32bit(fh)
            modelstart = xlAutomation.fseqFile.read32bit(fh)
            ccount = modelsize = xlAutomation.fseqFile.read32bit(fh)

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
            off2chdata = xlAutomation.fseqFile.read16bit(fh)
            minver = xlAutomation.fseqFile.read8bit(fh)
            majver = xlAutomation.fseqFile.read8bit(fh)

            isv1 = True if majver == 1 else False

            #print("offset to channel data: "+str(off2chdata))
            hjson['chdata_offset'] = off2chdata
            #print("Version "+str(majver)+'.'+str(minver))
            hjson['majver'] = majver
            hjson['minver'] = minver

            shdrlen = xlAutomation.fseqFile.read16bit(fh)
            ccount = xlAutomation.fseqFile.read32bit(fh)
            stepsz = int((ccount + 3) / 4) * 4
            nframes = xlAutomation.fseqFile.read32bit(fh)
            stepms = xlAutomation.fseqFile.read8bit(fh)
            reserved = xlAutomation.fseqFile.read8bit(fh)

            hjson['fixedhdr'] = shdrlen
            hjson['channels'] = ccount
            hjson['frames'] = nframes
            hjson['msperframe'] = stepms
            hjson['reserved1'] = reserved

            if (isv1):
                univcnt = xlAutomation.fseqFile.read16bit(fh)
                univsz = xlAutomation.fseqFile.read16bit(fh)
                gamma = xlAutomation.fseqFile.read8bit(fh)
                colorenc = xlAutomation.fseqFile.read8bit(fh)
                reserved = xlAutomation.fseqFile.read16bit(fh)
                hjson['univcnt'] = univcnt
                hjson['universesize'] = univsz
                hjson['gamma'] = gamma
                hjson['colorenc'] = colorenc
                hjson['reserved2'] = reserved

                # Double check this math, is it rounded up?
                compblocklist.append((0, nframes*ccnt))
            else:
                compandblks = xlAutomation.fseqFile.read8bit(fh)
                comp = compandblks & 15
                blks = (compandblks & 240) * 16
                blks += xlAutomation.fseqFile.read8bit(fh)
                #print ("blocks: "+str(blks))
                nranges = xlAutomation.fseqFile.read8bit(fh)
                reserved = xlAutomation.fseqFile.read8bit(fh)
                uuid1 = xlAutomation.fseqFile.read32bit(fh)
                uuid2 = xlAutomation.fseqFile.read32bit(fh)

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
                    framenum = xlAutomation.fseqFile.read32bit(fh)
                    blocksize = xlAutomation.fseqFile.read32bit(fh)
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
                    startnum = xlAutomation.fseqFile.read24bit(fh)
                    chcount = xlAutomation.fseqFile.read24bit(fh)
                    chrangelist.append((startnum, chcount))
                    hjson['chranges'].append({'startch':startnum, 'chcount':chcount})
            if not chrangelist:
                chrangelist.append((1, ccount))

            hjson['headers'] = {}
            vlheaders = {}
            while (fh.tell() + 4 <= off2chdata):
                #print ("At "+str(fh.tell())+" vs " + str(shdrlen))
                hlen = xlAutomation.fseqFile.read16bit(fh) - 4
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
                finfo = FrameInfo()
                hist = Histogram()
                finfo.ms = curms
                frame = raw[foffset: foffset + stepsz]

                # Go through each model and do some CRC there
                for m in models:
                    if srcmodels and len(srcmodels) and m.name not in srcmodels:
                        # Not interested in this model
                        continue
                    sch = m.startch
                    ech = m.startch + m.nch if m.nch >= 0 else ccount

                    # See if we have data for the model, considering sparse range
                    curoff = 0
                    for schrng in chrangelist:
                        (rstart, rcnt) = schrng
                        if sch >= rstart and ech <= rstart+rcnt:
                            msub = frame[curoff + sch - rstart : curoff + ech - rstart]
                            # Do color stuff for model in its entirety
                            hist.update(m, msub)
                        curoff += rcnt

                #print('Frame '+str(curframe)+' done')
                foffset += stepsz
                curframe = curframe + 1
                curms = curms + stepms
                frames.append(finfo)

                # TODO: Analyze the info we got
                for i in range(4):
                    gpop = 0
                    bg = 0
                    for v in range(0, len(hist.GHist)):
                        if hist.GHist[v] > gpop:
                            bg = v
                            gpop = hist.GHist[v]

                    bc = 0
                    bh = 0
                    bs = 0
                    for h in range(0, 180):
                        for s in range (0, 101):
                            if hist.HSHist[h*101+s] > bc:
                                bc = hist.HSHist[h*101+s]
                                bh = h
                                bs = s

                    cc = CChoice()
                    finfo.choices.append(cc)

                    if (bc == 0 and gpop == 0):
                        continue # There simply is not any color

                    if (gpop > bc):
                        # Do gray
                        for v in range(bg-5, bg+6):
                            if v > 0 and v <= 100:
                                cc.popularity += hist.GHist[v]
                                hist.GHist[v] = 0
                        cc.H = 0
                        cc.S = 0
                        cc.VTyp = bg
                    else:
                        # Do color
                        for h in range(bh-4, bh+5):
                            for s in range(bs-5, bs+6):
                                if s > 0 and s <= 100:
                                    cc.popularity += hist.HSHist[(h%180)*101+s]
                                    hist.HSHist[(h%180)*101+s] = 0
                        cc.H = bh*2
                        cc.S = bs
                        cc.VTyp = 100 # We don't have the V typical of that color; if we need it, we'd have to recompute it...
                                      # We could though.  If we aren't making it subservient to another formula anyway...

                    if cc.S > 0:
                        r, g, b = hsv_to_rgb(cc.H, cc.S, hist.maxV)
                        #r, g, b = hsv_to_rgb(cc.H, cc.S, 100)
                    else:
                        r, g, b = hsv_to_rgb(cc.H, cc.S, cc.VTyp)
                    print ("Picked["+str(i)+"] "+str(r)+","+str(g)+","+str(b)+" @"+str(cc.popularity)+"/"+str(hist.nNonBlack))

                finfo.nLit = hist.nNonBlack
                finfo.vMax = hist.maxV

            if (foffset != len(raw)):
                raise Exception("Partial frame")


        if (curframe != nframes):
            raise Exception("Frame count mismatch")

    return hjson

# TODO: This is a ridiculous amount of work
#x Read the input file
#x Read the layout to
#x  establish target model
#?  and color order
#?  and reverse gamma
#x Read the .fseq file
#x Get the typical color from the frame - sample or all?
#?  Do this as HSV buckets
#?  Get a sense of popularity and brightness
#?  Pick out the most popular and knock it out
#?  Pick out the second to 4th most popular
#?  Get a sense of overall significance energy level
#   Pick the times to do the changes
#   Make effects
#  Save
#  Test it

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=textwrap.dedent('''\
        xLights effect generator for floods/wands/bracelets/etc.
        '''),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--showdir', type=str, required = True, help='Directory with xlights_rgbeffects.xml and xlights_networks input file')
    parser.add_argument('--fseq', type=str, required = True, help='.fseq input file')
    parser.add_argument('--outxsq', type=str, required = True, help='Generated .xsq output')
    parser.add_argument('--modelsource', type=str, required = False, help = 'Source model(s) for RGB colors')
    parser.add_argument('--targetcontrol', type=str, default = 'DmxWandsCtrl', help = 'Target model for control pulses')
    parser.add_argument('--ch1val', type=int, default=85, help = 'Control Channel 1 (ID) value')
    parser.add_argument('--ch2val', type=int, default=0, help = 'Control Channel 2 (Group) value') 
    parser.add_argument('--targetcolor', type=str, default = 'DmxWands', help = 'Target model for colors')
    parser.add_argument('--controladvance', type=int, default=50, help = 'Milliseconds to advance the timing of the control strobe')
    parser.add_argument('--coloradvance', type=int, default=50, help = 'Milliseconds to advance the timing of the color')
    parser.add_argument('--controlwidth', type=int, default=75, help = 'Milliseconds to hold the control signal')
    parser.add_argument('--controlgap', type=int, default=50, help = 'Minimum milliseconds of gap to wait between control pulses')
    # TODO:
    parser.add_argument('--inxsq', type=str, required = False, help='Input .xsq, for timing track to trigger colors')
    parser.add_argument('--timingtrack', type=str, required = False, help = 'Timing track to use as a hint for sending color') # For this you need an input sequence...
    # TODO: Color control
    #parser.add_argument('--ncolors', type=int, default=1, help='Number of colors to extract and use')
    #Some tuning of how to handle the energy level?
    #Ramp up / down?

    args = parser.parse_args()

    controllers = []
    ctrlbyname = {}
    models = []
    smodels = []
    ttrack = None

    # Get controllers, models, timing tracks
    xlAutomation.fseqFile.readControllersAndModels(args.showdir, controllers, ctrlbyname, models, smodels)
    if args.inxsq:
        ttracks = []
        xlAutomation.xsqFile.readSequenceTimingTrack(args.inxsq, ttracks)
        if args.timingtrack:
            for tt in ttracks:
                if tt.name == args.timingtrack:
                    ttrack = tt
            if not ttrack:
                raise Exception("Timing track name "+args.timingtrack+" not found")
        elif len(ttracks):
            ttrack = ttracks[0]

    # Get the source model list
    srcmodels = []
    if args.modelsource:
        srcmodels = args.modelsource.split(',')

    frames = []
    # Get the fseq file color summary
    hjson = {}
    calculateFSEQColorSummary(hjson, args.fseq, controllers, ctrlbyname, smodels, frames, srcmodels)

    # OK
