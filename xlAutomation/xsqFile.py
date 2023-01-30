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

def setText(pnode, txt):
    for node in pnode.childNodes:
        if node.nodeType == node.TEXT_NODE:
            node.data = txt
            return
    raise Exception("No text child found")

# python xlAutomation\xsqFile.py m:\Users\Chuck\Source\Repos\merryoncherry\xLTS\ShowFolders\SCTS\SimpleEffectsUnstable.xsq x.xsq

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
            for tlayer in element.childNodes:
                if tlayer.nodeType == xml.dom.Node.ATTRIBUTE_NODE or tlayer.nodeType == xml.dom.Node.TEXT_NODE:
                    continue
                if tlayer.tagName != 'EffectLayer':
                    continue
                for effect in tlayer.childNodes:
                    if effect.nodeType == xml.dom.Node.ATTRIBUTE_NODE or effect.nodeType == xml.dom.Node.TEXT_NODE:
                        continue
                    if effect.tagName != 'Effect':
                        continue
                    disableEffect = False
                    if effect.getAttribute('name') in ['Candle', 'Circles', 'Fire', 'Fireworks', 'Life', 'Lightning', 'Lines', 'Liquid', 'Meteors']:
                        disableEffect = True
                    if effect.getAttribute('name') in ['Shape', 'Shimmer', 'Snowflake', 'Snowstorm', 'Strobe', 'Tendril', 'Twinkle']:
                        disableEffect = True
                    if (getText(colors[int(effect.getAttribute('palette'))]).find('C_SLIDER_SparkleFrequency=80')):
                        # Sorry, we either change color or disable all effects that use the effect with the sparkle in color
                        disableEffect = True
                    if disableEffect:
                        en = int(effect.getAttribute('ref'))
                        txt = getText(effectsdb[en])
                        if not (txt.find('X_Effect_RenderDisabled=True')):
                            setText(effectsdb[en]. txt + ',X_Effect_RenderDisabled=True')
                break

    with open(dpath,"w") as file_handle:
        #xseqd.writexml(file_handle, indent='', addindent='  ', newl='\n', encoding=None, standalone=None)
        xseqd.writexml(file_handle, encoding=None, standalone=None)
        file_handle.close()

if __name__ == '__main__':
    # Get the args, run the above function

    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('flist', nargs=2, help='sequence binary files')

    args = parser.parse_args()

    disableUnstableEffects(args.flist[0], args.flist[1])
