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
import bisect
import textwrap
import sys
import xml.dom
import xml.dom.minidom as minidom
import zstandard

sys.path.append('../merryoncherry')
import xlAutomation.fseqFile
import xlAutomation.xsqFile

# H in the range [0, 360), and S, V in the range [0, 1].
# Will invert the gamma correction as part of calculation
def rgb_to_hsv(r, g, b, invgamma, invbright):
    r, g, b = (r * invbright / 255.0) ** invgamma, (g * invbright / 255.0) ** invgamma, (b * invbright / 255.0) ** invgamma
    r = min(r, 1.0)
    g = min(g, 1.0)
    b = min(b, 1.0)

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

    def update(self, model, raw, args):
        rp = 0
        l = len(raw)
        invgamma = 1.0/model.gamma
        invbright = 1.0/model.brightness
        while rp+2 < l:
            r = raw[rp + model.r]
            g = raw[rp + model.g]
            b = raw[rp + model.b]
            rp = rp + 3
            self.nSamples = self.nSamples + 1
            h, s, v = rgb_to_hsv(r, g, b, invgamma, invbright)

            if v < self.minV:
                self.minV = v
            if v*100 > self.maxV:
                self.maxV = v * 100
            if r <= args.thresholdv and g <= args.thresholdv and b <= args.thresholdv:
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

    def setBlack(self):
        self.H = 0
        self.S = 0;
        self.VTyp = 0

    def valid(self):
        if (self.VTyp > 0):
            return True
        return False

    def invalidate(self):
        self.VTyp = 0
        self.H = 0
        self.S = 0
        self.popularity = 0

    def isDifferent(self, other, args):
        if other is None:
            return True
        hdiff = abs(self.H - other.H)
        if hdiff > args.similarityh and hdiff < 360 - args.similarityh:
            return True
        if abs(self.S - other.S) > args.similaritys:
            return True
        if abs(self.VTyp - other.VTyp) > args.similarityv:
            return True
        return False

class FrameInfo:
    def __init__(self):
        self.choices = []
        self.nLit = 0
        self.nPixels = 0
        self.pctLit = 0
        self.pctBright = 0
        self.vAvg = 0 # Among the lit ones, you can water down by pctLit to get overall
        self.vMax = 0
        self.ms = 0

    def setBlack(self):
        self.vAvg = 0
        self.vMax = 0
        self.pctLit = 0
        self.pctBright = 0
        self.nLit = 0
        for cc in self.choices:
            cc.setBlack()

def calculateFSEQColorSummary(hjson, sfile, controllers, ctrlbyname, models, frames, srcmodels, args):
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
                hval = str(fh.read(hlen), 'utf-8', errors='ignore')
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
                foundModels = {}
                for m in models:
                    if srcmodels and len(srcmodels) and m.name not in srcmodels:
                        # Not interested in this model
                        continue
                    foundModels[m.name] = m
                    sch = m.startch
                    ech = m.startch + m.nch if m.nch >= 0 else ccount

                    # See if we have data for the model, considering sparse range
                    curoff = 0
                    #print("Model channel range "+str(sch)+"-"+str(ech))
                    for schrng in chrangelist:
                        (rstart, rcnt) = schrng
                        #print("Seq channel range "+str(rstart)+"-"+str(rstart+rcnt))
                        if sch >= rstart and ech <= rstart+rcnt:
                            #print("Using it... @"+str(sch-rstart))
                            msub = frame[curoff + sch - rstart : curoff + ech - rstart]
                            # Do color stuff for model in its entirety
                            #print("Starting model "+m.name)
                            hist.update(m, msub, args)
                            #print("Finished model "+m.name)
                        curoff += rcnt

                if srcmodels and len(srcmodels) != len(foundModels):
                    print("ERROR: We did not find all your models: "+",".join(srcmodels))
                    for mn in srcmodels:
                        if mn not in foundModels:
                            print("  -- "+mn+" not found")
                    exit(-1)

                #print('Frame '+str(curframe)+' done')
                foffset += stepsz
                curframe = curframe + 1

                #print ("Frame #"+str(len(frames))+"/"+str(curms)+" done")
                frames.append(finfo)
                curms = curms + stepms

                # Analyze the info we got
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
                        for h in range(bh-args.similarityh, bh+1+args.similarityh):
                            for s in range(bs-args.similaritys, bs+1+args.similaritys):
                                if s > 0 and s <= 100:
                                    cc.popularity += hist.HSHist[(h%180)*101+s]
                                    hist.HSHist[(h%180)*101+s] = 0
                        cc.H = bh*2
                        cc.S = bs
                        cc.VTyp = 100 # We don't have the V typical of that color; if we need it, we'd have to recompute it...
                                      # We could though.  If we aren't making it subservient to another formula anyway...

                    #if cc.S > 0:
                    #    r, g, b = hsv_to_rgb(cc.H, cc.S, hist.maxV)
                    #else:
                    #    r, g, b = hsv_to_rgb(cc.H, cc.S, cc.VTyp)
                    #print ("Picked["+str(i)+"] "+str(r)+","+str(g)+","+str(b)+" @"+str(cc.popularity)+"/"+str(hist.nNonBlack))

                if hist.nNonBlack:
                    vtot = 0
                    btot = 0
                    for i in range(1, len(hist.VHist)):
                        vtot += i * hist.VHist[i]
                        if i >= 50:
                            btot += hist.VHist[i]
                    finfo.pctLit = hist.nNonBlack * 100 / hist.nSamples
                    finfo.pctBright = btot * 100 / hist.nSamples
                    finfo.vAvg = vtot / hist.nNonBlack

                finfo.nLit = hist.nNonBlack
                finfo.nPixels = hist.nSamples
                finfo.vMax = hist.maxV

            if (foffset != len(raw)):
                raise Exception("Partial frame")


        if (curframe != nframes):
            raise Exception("Frame count mismatch")

    return hjson

class SequenceGenerator:
    def __init__(self, framems, nframes):
        self.framems = framems

        self.xdoc = minidom.Document()
        self.xsq = self.emptyChild('xsequence')
        self.xsq.setAttribute('BaseChannel', '0')
        self.xsq.setAttribute('ChanCtrlBasic', '0')
        self.xsq.setAttribute('ChanCtrlColor', '0')
        self.xsq.setAttribute('FixedPointTiming', '1')
        self.xsq.setAttribute('ModelBlending', 'true')
        self.xdoc.appendChild(self.xsq)

        self.head = self.emptyChild('head')
        self.head.appendChild(self.emptyChild('author'))
        self.head.appendChild(self.emptyChild('author-email'))
        self.head.appendChild(self.emptyChild('author-website'))
        self.head.appendChild(self.emptyChild('song'))
        self.head.appendChild(self.emptyChild('artist'))
        self.head.appendChild(self.emptyChild('album'))
        self.head.appendChild(self.emptyChild('MusicURL'))
        self.head.appendChild(self.emptyChild('comment'))
        stiming = self.emptyChild('sequenceTiming')
        self.setText(stiming, str(framems)+' ms')
        self.head.appendChild(stiming)
        stype = self.emptyChild('sequenceType')
        self.setText(stype, 'Animation')
        self.head.appendChild(stype)
        self.head.appendChild(self.emptyChild('mediaFile'))
        dur = self.emptyChild('sequenceDuration')
        self.setText(dur, str(framems *  nframes / 1000.0))
        self.head.appendChild(dur)
        self.head.appendChild(self.emptyChild('imageDir'))
        self.xsq.appendChild(self.head)

        self.nextid = self.emptyChild('nextid')
        self.xsq.appendChild(self.head)
        
        self.jukebox = self.emptyChild('Jukebox')
        self.xsq.appendChild(self.jukebox)

        self.palettes = self.emptyChild('ColorPalettes')
        self.xsq.appendChild(self.palettes)

        self.effectdb = self.emptyChild('EffectDB')
        self.xsq.appendChild(self.effectdb)

        self.dlayers = self.emptyChild('DataLayers')
        self.xsq.appendChild(self.dlayers)

        #<Element collapsed="0" type="model" name="1_All Display" visible="1"/>
        self.delements = self.emptyChild('DisplayElements')
        self.xsq.appendChild(self.delements)

        self.eeffects = self.emptyChild('ElementEffects')
        self.xsq.appendChild(self.eeffects)
        # <Element type="model" name="1_All Display">
        #      <EffectLayer>
        #          <Effect ref="0" name="Ripple" startTime="165950" endTime="167450" palette="0"/>

        self.lastView = self.emptyChild('LastView')
        self.setText(self.lastView, "1")
        self.xsq.appendChild(self.lastView)

        self.lastView = self.emptyChild('TimingTags')
        self.xsq.appendChild(self.lastView)

        # Cache parts of the generated sequence
        self.origColors = {}
        self.xfColorToId = {}
        self.xfColorById = []
        self.origEffects = {}
        self.xfEffectToId = {}
        self.xfEffectById = []

    def emptyChild(self, tagName):
        new_child = self.xdoc.createElement(tagName)
        return new_child

    def setText(self, pnode, txt):
        for node in pnode.childNodes:
            if node.nodeType == node.TEXT_NODE:
                node.data = txt
            return
        text = self.xdoc.createTextNode(txt)
        pnode.appendChild(text)

    def createDisplayElement(self, name):
        new_child = self.xdoc.createElement('Element')
        new_child.setAttribute('collapsed', '0')
        new_child.setAttribute('type', 'model')
        new_child.setAttribute('name', name)
        new_child.setAttribute('visible', '1')
        self.delements.appendChild(new_child)

    def createEffectElementLayer(self, mname):
        newEE = self.emptyChild('Element')
        newEE.setAttribute('type', 'model')
        newEE.setAttribute('name', mname)
        self.eeffects.appendChild(newEE)
        newEL = self.emptyChild('EffectLayer')
        newEE.appendChild(newEL)
        return newEL

    def createEffect(self, ename, stime, etime, effectdata, palettedata):
        new_doc = self.xdoc
        new_eff = new_doc.createElement('Effect')
        new_eff.setAttribute('name', ename)
        new_eff.setAttribute('startTime', str(stime))
        new_eff.setAttribute('endTime', str(etime))
        neffid = -1
        if effectdata in self.xfEffectToId:
            neffid = self.xfEffectToId[effectdata]
        else:
            neffid = len(self.xfEffectById)
            self.xfEffectById.append(effectdata)
            self.xfEffectToId[effectdata] = neffid
        new_eff.setAttribute('ref', str(neffid))
        palid = -1
        if palettedata in self.xfColorToId:
            palid = self.xfColorToId[palettedata]
        else :
            palid = len(self.xfColorById)
            self.xfColorById.append(palettedata)
            self.xfColorToId[palettedata] = palid
        new_eff.setAttribute('palette', str(palid))
        return new_eff

    def createOnEffect(self, stime, etime, r, g, b):
        pdata = "C_BUTTON_Palette1=#"+'{:02X}{:02X}{:02X}'.format(r, g, b)+",C_BUTTON_Palette2=#000000,C_BUTTON_Palette3=#000000,C_BUTTON_Palette4=#000000,C_BUTTON_Palette5=#000000,C_BUTTON_Palette6=#000000,C_BUTTON_Palette7=#000000,C_BUTTON_Palette8=#000000,C_CHECKBOX_Palette1=1"
        edata = "E_TEXTCTRL_Eff_On_Start=100,E_TEXTCTRL_Eff_On_End=100,E_TEXTCTRL_On_Cycles=1"
        return self.createEffect("On", stime, etime, edata, pdata)

    def createDmxEffect(self, stime, etime, ch1, ch2):
        pdata = "C_BUTTON_Palette1=#000000,C_BUTTON_Palette2=#000000,C_BUTTON_Palette3=#000000,C_BUTTON_Palette4=#000000,C_BUTTON_Palette5=#000000,C_BUTTON_Palette6=#000000,C_BUTTON_Palette7=#000000,C_BUTTON_Palette8=#000000,C_CHECKBOX_Palette1=1"
        edata = "E_CHECKBOX_INVDMX1=0,E_CHECKBOX_INVDMX2=0,E_NOTEBOOK1=Channels 1-10,E_SLIDER_DMX1="+str(ch1)+",E_SLIDER_DMX2="+str(ch2)
        return self.createEffect("DMX", stime, etime, edata, pdata)        

    def generateSequence(self):
        # Emit the parts of the doc that have been saved up
        new_doc = self.xdoc
        i = 0
        while i < len(self.xfColorById):
            new_clr = new_doc.createElement('ColorPalette')
            self.setText(new_clr, self.xfColorById[i])
            self.palettes.appendChild(new_clr)
            i = i + 1
        i = 0
        while i < len(self.xfEffectById):
            new_eff = new_doc.createElement('Effect')
            self.setText(new_eff, self.xfEffectById[i])
            self.effectdb.appendChild(new_eff)
            i = i + 1

class SeqEnt:
    def __init__(self, frame):
        self.frame = frame
        self.ms = frame.ms
        self.event = False # If there was a trigger event vs just a fill - we want a color change here
        self.colorFidelity = False # Hint that we ought to take popular color, not just change
        self.tn = 0 # Time number

class SparseSeq:
    def __init__(self):
        self.times = []
        self.frames = {}

    def insert(self, frame):
        if frame.ms not in self.frames:
            bisect.insort(self.times, frame.ms)
        self.frames[frame.ms] = frame

    def insertIfSpaced(self, frame, gap):
        (l, r) = self.closest(frame.ms)
        if l and frame.ms - l.ms < gap:
            return
        if r and r.ms - frame.ms < gap:
            return
        self.insert(frame)

    def isSpaced(self, ms, gap):
        (l, r) = self.closest(ms)
        if l and ms - l.ms < gap:
            return False
        if r and r.ms - ms < gap:
            return False
        return True

    def closest(self, time):
        idx = bisect.bisect_left(self.times, time)

        left = self.times[idx - 1] if idx - 1 >= 0 else None
        right = self.times[idx] if idx < len(self.times) else None

        lframe = None
        rframe = None
        if left:
            lframe = self.frames[left]
        if right:
            rframe = self.frames[right]

        return (lframe, rframe)


# TODO:
#x Read the input file
#x Read the layout to
#x  establish target model
#x  and color order
#x  and reverse gamma
#x Read the .fseq file
#x Get the typical color from the frame - sample or all?
#x  Do this as HSV buckets
#x  Get a sense of popularity and brightness
#x  Pick out the most popular and knock it out
#x  Pick out the second to 4th most popular
#x  Get a sense of overall significance energy level
#   Pick the times to do the changes
#x   Make effects
#x Save
#x Test it

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
    parser.add_argument('--controladvance', type=int, default=0, help = 'Milliseconds to advance the timing of the control strobe')
    parser.add_argument('--coloradvance', type=int, default=0, help = 'Milliseconds to advance the timing of the color')
    parser.add_argument('--controlwidth', type=int, default=75, help = 'Milliseconds to hold the control signal')
    parser.add_argument('--controlgap', type=int, default=50, help = 'Minimum milliseconds of gap to wait between control pulses')
    parser.add_argument('--inxsq', type=str, required = False, help='Input .xsq, for timing track to trigger colors')
    parser.add_argument('--timingtrack', type=str, required = False, help = 'Timing track to use as a hint for sending color') # For this you need an input sequence...
    parser.add_argument('--ttracklast', type=int, default = 1, help = 'Timing track applied last, after other detection')
    parser.add_argument('--minpopularity', type=int, default = 10, help = 'Minimum popularity of a color (in tenths of a percent) for it to be considered')
    parser.add_argument('--ncolors', type=int, default = 1, help = "Number of colors to cycle between as the beats progress")
    parser.add_argument('--changecolor', type=int, default = 0, help = "Try to change color when there is an event")

    # Jump control
    parser.add_argument('--brightjumpamt', type=int, default = 50, help = "Brightness Jump Event: If brightness jumps by this amount, count it as an event")
    parser.add_argument('--brightjumparea', type=int, default = 50, help = 'Brightness Jump Event: To count as a brightness jump, at least this much must be lit')

    # Some tuning of how to handle the energy level?
    parser.add_argument('--brightdropamt', type=int, default = 50, help = "Brightness Drop Event: If brightness jumps by this amount, count it as an event")
    parser.add_argument('--brightdroparea', type=int, default = 50, help = 'Brightness Drop Event: To count as a brightness jump, at least this much must have been lit')

    # Turn off if value drops a lot from when it was turned on
    parser.add_argument('--offondrop', type=int, default = 50, help = 'Turn off when brightness drops by this percent')

    # Color control - color change event
    parser.add_argument('--colorjumpamt', type=int, default = 25, help = "Color proportion jump event: If a color becomes most popular and jumps by this amount, count it as an event")
    parser.add_argument('--colorjumparea', type=int, default = 50, help = "Color proportion jump event: If a color becomes more popular and covers this much area, count it as an event")

    parser.add_argument('--similarityh', type=int, default = 6, help = "Hue similarity")
    parser.add_argument('--similaritys', type=int, default = 10, help = "Saturation similarity")
    parser.add_argument('--similarityv', type=int, default = 20, help = "Value similarity")
    parser.add_argument('--thresholdv', type=int, default = 5, help = "Value threshold - below this it is too dark for color fidelity")

    # TODO: Just fill in with the popular color - that mode is a bit tricky

    args = parser.parse_args()

    controllers = []
    ctrlbyname = {}
    models = []
    smodels = []
    ttrack = None

    # Get controllers, models, timing tracks
    xlAutomation.fseqFile.readControllersAndModels(args.showdir, controllers, ctrlbyname, models, smodels)
    if args.inxsq and args.timingtrack:
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
    calculateFSEQColorSummary(hjson, args.fseq, controllers, ctrlbyname, smodels, frames, srcmodels, args)

    # OK - Start generating a sequence
    framems = hjson['msperframe']
    nframes = hjson['frames']
    resseq = SequenceGenerator(framems, hjson['frames'])

    # Add the two display elements
    resseq.createDisplayElement(args.targetcontrol)
    resseq.createDisplayElement(args.targetcolor)

    ctrlLayer = resseq.createEffectElementLayer(args.targetcontrol)
    clrLayer = resseq.createEffectElementLayer(args.targetcolor)

    # So, the overall plan:
    # Make a list of the change points we want, with data about the change
    # x Start with the timing marks, if given
    #   Look for high-energy transitions that need precise timing
    #   Should we consider energy drops?  Or following the value profile in some way?
    #   Look for fillers - sufficient change to warrant an update
    #   Do the emission:
    # x  Select a color (change colors if desired)
    # ?  If it is the same, suppress
    # x  Write out the event with the appropriate shifts
    # x We should make the thing go dark at the end, right?

    # Prune out the unpopular colors
    for f in frames:
        for i in range(0, len(f.choices)):
            if i == 0:
                pass
                #continue
            if f.choices[i].popularity * 1000 < f.nLit * args.minpopularity:
                #print("Invalidate choice: "+str(i))
                f.choices[i].invalidate()

    reqgap = int(args.controlwidth) + int(args.controlgap)
    ss = SparseSeq()

    if ttrack and not args.ttracklast:
        for te in ttrack.entlist:
            # We will create two, if there's another timing it will just overwrite it
            sfn = int(te.startms / framems)
            efn = int(te.endms / framems)
            if sfn >= len(frames) or efn >= len(frames):
                continue
            if efn == sfn:
                continue
            bn = 0
            try:
                bn = int(te.label)
            except:
                pass
            se = SeqEnt(frames[sfn])
            se.event = True
            se.tn = bn
            ss.insert(se)
            ee = SeqEnt(frames[efn])
            ss.insert(ee)

    # Black at the end
    seqend = framems * nframes
    ee = SeqEnt(frames[nframes-1])
    frames[nframes-1].setBlack()
    ss.insert(ee)
    ncolors = int(args.ncolors)

    # Look for brightness triggers
    for i in range(1, len(frames)):
        cf = frames[i]
        pf = frames[i-1]
        if args.brightjumpamt > 0 and cf.pctLit >= args.brightjumparea and cf.vAvg - (pf.vAvg * pf.pctLit / cf.pctLit) >= args.brightjumpamt:
            es = SeqEnt(cf)
            es.event = True
            es.colorFidelity = True
            ss.insertIfSpaced(es, reqgap)
        if args.brightdropamt > 0 and pf.pctLit >= args.brightdroparea and pf.vAvg - (cf.vAvg * cf.pctLit / pf.pctLit) >= args.brightdropamt:
            es = SeqEnt(cf)
            es.event = True
            ss.insertIfSpaced(es, reqgap)

        if args.colorjumpamt > 0:
            amtpopular = 100 * cf.choices[0].popularity / cf.nPixels
            if amtpopular > args.colorjumparea:
                pctpopular = 100 * cf.choices[0].popularity / cf.nLit
                prevpop = 0
                for c in pf.choices:
                    if not c.isDifferent(cf.choices[0], args) and c.popularity > 0:
                        prevpop = 100 * c.popularity / pf.nLit
                if pctpopular - prevpop >= args.colorjumpamt:
                    es = SeqEnt(cf)
                    es.event = True
                    es.colorFidelity = True
                    ss.insertIfSpaced(es, reqgap)

    if ttrack and args.ttracklast:
        for te in ttrack.entlist:
            # We will create two, if there's another timing it will just overwrite it
            sfn = int(te.startms / framems)
            efn = int(te.endms / framems)
            if sfn >= len(frames) or efn >= len(frames):
                continue
            if efn == sfn:
                continue
            bn = 0
            try:
                bn = int(te.label)
            except:
                pass
            se = SeqEnt(frames[sfn])
            se.event = True
            se.tn = bn
            ss.insertIfSpaced(se, reqgap)

    if args.offondrop:
        lastevt = None
        curms = 0
        for i in range(0, len(frames)):
            curms = i * framems
            if curms in ss.frames:
                lastevt = ss.frames[curms]
                continue
            if not lastevt:
                continue
            if lastevt.frame.vMax == 0:
                continue
            #print ("curms: "+str(curms)+" drop "+str(100 - (100 * frames[i].vMax / lastevt.frame.vMax)))
            if 100 - (100 * frames[i].vMax / lastevt.frame.vMax) > args.offondrop:
                if ss.isSpaced(curms, reqgap):
                    frames[i].setBlack()
                    se = SeqEnt(frames[i])
                    ss.insertIfSpaced(se, reqgap)
                    lastevt = se

    # Generate effects...
    ctime = 0
    i = 0
    lastChoice = None

    while i < len(ss.times):
        stime = ss.times[i]
        while 1:
            i = i+1
            etime = ss.times[i] if i < len(ss.times) else seqend
            if etime - stime >= reqgap or i >= len(ss.times):
                break

        cframe = ss.frames[stime]
        chosen = 0
        cc = cframe.frame.choices[chosen]

        if cframe.event:
            if ncolors > 1:
                chosen = ((cframe.tn-1) % ncolors) % 4
            cc = cframe.frame.choices[chosen]

            if args.changecolor and not cframe.colorFidelity:
                for ccc in range(0, 4):
                    if cframe.frame.choices[(chosen + ccc) % 4].isDifferent(lastChoice, args):
                        cc = cframe.frame.choices[(chosen + ccc) % 4]
                        #print ("Changed by: "+str(ccc))
                        break

        #print("Event: "+str(i)+" cframe ms "+str(cframe.frame.ms) + " time " + str(stime))

        if cc.S > 0:
            r, g, b = hsv_to_rgb(cc.H, cc.S, cframe.frame.vMax)
            #r, g, b = hsv_to_rgb(cc.H, cc.S, 100)
        else:
            r, g, b = hsv_to_rgb(cc.H, cc.S, cc.VTyp)

        lastChoice = cc

        ctrlstime = max(stime - int(args.controladvance), 0)
        ctrletime = max(stime - int(args.controladvance) + int(args.controlwidth), 0)
        clrstime = max(stime - int(args.coloradvance), 0)
        clretime = max(etime - int(args.coloradvance), 0)

        clrLayer.appendChild(resseq.createOnEffect(clrstime, clretime, r, g, b))
        ctrlLayer.appendChild(resseq.createDmxEffect(ctrlstime, ctrletime, int(args.ch1val), int(args.ch2val)))

    # Do the write-out
    resseq.generateSequence()
    with open(args.outxsq, "w") as f:
        f.write(resseq.xdoc.toprettyxml(indent="  "))
