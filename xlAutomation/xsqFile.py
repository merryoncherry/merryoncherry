import argparse
import io
import json
import os
import sys
import xml.dom.minidom

def getText(pnode):
    rc = []
    for node in pnode.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def setText(pnode, txt, doc):
    for node in pnode.childNodes:
        if node.nodeType == node.TEXT_NODE:
            node.data = txt
            return
    text = doc.createTextNode(txt)
    pnode.appendChild(text)

# python xlAutomation\xsqFile.py m:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\SCTS\SimpleEffectsUnstable.xsq x.xsq
# python xlAutomation\xsqFile.py --suite M:\xL_Test_2021\2021_Aspirational M:\xL_Test_2021\2021_Stabilized

#head
#nextid

#ColorPalettes
def getColors(xnseq):
    colors = []
    for section in xnseq.childNodes:
        if section.nodeType == xml.dom.Node.ATTRIBUTE_NODE or section.nodeType == xml.dom.Node.TEXT_NODE:
            continue
        if section.tagName != 'ColorPalettes':
            continue
        for color in section.childNodes:
            if color.nodeType == xml.dom.Node.ATTRIBUTE_NODE or color.nodeType == xml.dom.Node.TEXT_NODE:
                continue
            if color.tagName != 'ColorPalette':
                continue
            colors.append(color)
    return colors

#EffectDB
def getEffects(xnseq):
    effects = []
    for section in xnseq.childNodes:
        if section.nodeType == xml.dom.Node.ATTRIBUTE_NODE or section.nodeType == xml.dom.Node.TEXT_NODE:
            continue
        if section.tagName != 'EffectDB':
            continue
        for effect in section.childNodes:
            if effect.nodeType == xml.dom.Node.ATTRIBUTE_NODE or effect.nodeType == xml.dom.Node.TEXT_NODE:
                continue
            if effect.tagName != 'Effect':
                continue
            effects.append(effect)
    return effects



#DataLayers
#DisplayElements


#ElementEffects->Element->EffectLayer->Effect

class TimingEnt:
    def __init__(self, label, startms, endms):
        self.label = label
        self.startms = startms
        self.endms = endms
        self.crc = 0
        self.models = {}

class TimingRec:
    def __init__(self, name):
        self.name = name
        self.entlist = []
        self.current = 0


def readSequenceTimingTrack(spath, ttracks):
    xseqd = xml.dom.minidom.parse(spath)
    xnseq = xseqd.documentElement
    if (xnseq.tagName != 'xsequence'):
        raise Exception('Root not "xsequence"')
    for section in xnseq.childNodes:
        if section.nodeType == xml.dom.Node.ATTRIBUTE_NODE or section.nodeType == xml.dom.Node.TEXT_NODE:
            continue
        if section.tagName != 'ElementEffects':
            continue
        for element in section.childNodes:
            if element.nodeType == xml.dom.Node.ATTRIBUTE_NODE or element.nodeType == xml.dom.Node.TEXT_NODE:
                continue
            if element.tagName != 'Element' or element.getAttribute('type') != 'timing':
                continue
            # Ahah: Timing
            for tlayer in element.childNodes:
                if tlayer.nodeType == xml.dom.Node.ATTRIBUTE_NODE or tlayer.nodeType == xml.dom.Node.TEXT_NODE:
                    continue
                if tlayer.tagName != 'EffectLayer':
                    continue
                trec = TimingRec(element.getAttribute('name'))
                ttracks.append(trec)
                for effect in tlayer.childNodes:
                    if effect.nodeType == xml.dom.Node.ATTRIBUTE_NODE or effect.nodeType == xml.dom.Node.TEXT_NODE:
                        continue
                    if effect.tagName != 'Effect':
                        continue
                    if effect.getAttribute('startTime') == effect.getAttribute('endTime'): # zero length - skip
                        continue
                    trec.entlist.append(TimingEnt(effect.getAttribute('label'), int(effect.getAttribute('startTime')), int(effect.getAttribute('endTime'))))
                break

def disableUnstableEffects(spath, dpath):
    xseqd = xml.dom.minidom.parse(spath)
    xnseq = xseqd.documentElement

    colors = getColors(xnseq)

    # Should we just get rid of sparkles?  Or turn off their effects?

    effectsdb = getEffects(xnseq)

    if (xnseq.tagName != 'xsequence'):
        raise Exception('Root not "xsequence"')
    for section in xnseq.childNodes:
        if section.nodeType == xml.dom.Node.ATTRIBUTE_NODE or section.nodeType == xml.dom.Node.TEXT_NODE:
            continue
        if section.tagName != 'ElementEffects':
            continue
        for element in section.childNodes:
            if element.nodeType == xml.dom.Node.ATTRIBUTE_NODE or element.nodeType == xml.dom.Node.TEXT_NODE:
                continue
            if element.tagName != 'Element' or element.getAttribute('type') != 'model': # Only model, not timing
                continue
            # Ahah: Model
            for elayer in element.childNodes:
                if elayer.nodeType == xml.dom.Node.ATTRIBUTE_NODE or elayer.nodeType == xml.dom.Node.TEXT_NODE:
                    continue
                if elayer.tagName != 'EffectLayer' and elayer.tagName != 'SubModelEffectLayer':
                    continue
                for effect in elayer.childNodes:
                    if effect.nodeType == xml.dom.Node.ATTRIBUTE_NODE or effect.nodeType == xml.dom.Node.TEXT_NODE:
                        continue
                    if effect.tagName != 'Effect':
                        continue
                    disableEffect = False
                    ename = effect.getAttribute('name')
                    if ename in ['Kaleidoscope', 'Lightning']:
                        disableEffect = True
                    if ename in ['Shape', 'Shimmer', 'Snowflakes', 'Strobe', 'Tendril', 'Warp', 'Ripple']:
                        disableEffect = True
                    if effect.hasAttribute('palette') and getText(colors[int(effect.getAttribute('palette'))]).find('Type=Random') >= 0: # Weird color gradient blend mode
                        disableEffect = True
                    if not args.dev:
                        if ename in ['Candle', 'Circles', 'Faces', 'Fire', 'Fireworks', 'Life', 'Lines', 'Liquid', 'Meteors', 'Snowstorm']:
                            disableEffect = True
                        if ename in ['Meteors', 'Twinkle']:
                            # These are sorta stable except on large parallel renders
                            disableEffect = True
                        if effect.hasAttribute('palette') and getText(colors[int(effect.getAttribute('palette'))]).find('C_SLIDER_SparkleFrequency=') >= 0:
                            # Sorry, we either change color or disable all effects that use the effect with the sparkle in color
                            disableEffect = True
                        if effect.hasAttribute('palette') and getText(colors[int(effect.getAttribute('palette'))]).find('C_CHECKBOX_MusicSparkles=') >= 0:
                            disableEffect = True
                        if effect.hasAttribute('palette') and getText(colors[int(effect.getAttribute('palette'))]).find('C_VALUECURVE_SparkleFrequency=Active=TRUE') >= 0:
                            disableEffect = True
                    en = int(effect.getAttribute('ref'))
                    txt = getText(effectsdb[en])
                    if txt.find('E_CHECKBOX_Spirals_3D=1')>=0:
                        disableEffect = True
                    if ename == 'VU Meter':
                        if txt.find('Random') >= 0:
                            disableEffect = True
                    if disableEffect:
                        if txt.find('X_Effect_RenderDisabled=True') < 0:
                            #raise Exception('Check it '+str(en)+":"+txt)
                            if txt:
                                txt = txt + ',X_Effect_RenderDisabled=True'
                            else:
                                txt = 'X_Effect_RenderDisabled=True'
                            setText(effectsdb[en], txt, xseqd)
                            #print (getText(effectsDB[en]))

    with open(dpath,"w") as file_handle:
        #xseqd.writexml(file_handle, indent='', addindent='  ', newl='\n', encoding=None, standalone=None)
        xseqd.writexml(file_handle, encoding='utf-8', standalone=None)
        file_handle.close()

if __name__ == '__main__':
    # Get the args, run the above function

    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('flist', nargs=2, help='sequence binary files')
    parser.add_argument('-S', '--suite', action='store_true', help='If set, process a directory')
    parser.add_argument('-V', '--dev', action='store_true', help='Use dev branch, assumes more things are fixed')

    args = parser.parse_args()

    if args.suite:
        os.makedirs(args.flist[1], mode = 0o777, exist_ok = True)
        xlist = os.listdir(args.flist[0])
        slist = []
        for x in xlist:
            if x.endswith('.xsq'):
                slist.append(x)
        for x in slist:
            print(x)
            disableUnstableEffects(os.path.join(args.flist[0], x), os.path.join(args.flist[1], x))
    else:
         disableUnstableEffects(args.flist[0], args.flist[1])
