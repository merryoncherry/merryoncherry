import argparse
import io
import json
import os
import sys
import xml.dom.minidom

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


