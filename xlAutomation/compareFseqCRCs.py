# Module to compare two fseq summaries made by fseqFile.py

import argparse
import io
import json
import os
import sys
import xml.dom.minidom

# If you don't use the command line below, this is the args you need
class Args:
    def __init__(self):
        self.channels = False
        self.frames = False
        self.globalcrc = False
        self.models = False
        self.timings = False
        self.timing_models = False

def compareSummaries(v1, v2, args, fh):
    xlv1 = v1['headers']['sp'] if 'sp' in v1['headers'] else '<unknown>'
    xlv2 = v2['headers']['sp'] if 'sp' in v2['headers'] else '<unknown>'

    # OK compare them
    diff = False
    if args.channels:
        if v1['hdr4'] != v2['hdr4']:
            diff = True
            print("Header 4 differs: "+v1['hdr4']+" vs "+v2['hdr4'], file=fh)
        if v1['majver'] != v2['majver']:
            diff = True
            print("Major version differs: "+str(v1['majver'])+" vs "+str(v2['majver']), file=fh)
        if v1['minver'] != v2['minver']:
            diff = True
            print("Minor version differs: "+str(v1['minver'])+" vs "+str(v2['minver']), file=fh)
        if v1['channels'] != v2['channels']:
            diff = True
            print("Channel count differs: "+str(v1['channels'])+" vs "+str(v2['channels']), file=fh)
        if v1['frames'] != v2['frames']:
            diff = True
            print("Frame count differs: "+str(v1['frames'])+" vs "+str(v2['frames']), file=fh)
        if v1['msperframe'] != v2['msperframe']:
            diff = True
            print("Framerate differs: "+str(v1['msperframe'])+" vs "+str(v2['msperframe']), file=fh)
        if v1['nsparseranges'] != v2['nsparseranges']:
            diff = True
            print("Sparse range count differs: "+str(v1['nsparseranges'])+" vs "+str(v2['nsparseranges']), file=fh)

        # TODO: Compare sparse ranges if asked; might be nice to know, but if it works, it works
        # Comp blocks can easily be noisy, I presume, and no such thing as correctness.

    if args.globalcrc:
        if v1['globalcrc'] != v2['globalcrc']:
            diff = True
            print("Global CRC differs: "+str(v1['globalcrc'])+" vs "+str(v2['globalcrc']), file=fh)

    if args.frames:
        v1fs = {}
        for f in v1['framecrcs']:
            v1fs[f['frame']] = f
        for f in v2['framecrcs']:
            if f['frame'] not in v1fs:
                diff = True
                print("Frame "+str(f['frame'])+" is black in file1 but present in file2", file=fh)
            else:
                if not (f['crc'] == v1fs[f['frame']]['crc']):
                    diff = True
                    print("Frame "+str(f['frame'])+" crc differs", file=fh)
                del  v1fs[f['frame']]
        for f in v1fs.values():
            diff = True
            print ("Frame "+str(f['frame'])+" is black in file2 but present in file1", file=fh)

    affectedmt = {}
    if args.models:
        v1ms = {}
        for m in v1['modelcrcs']:
            v1ms[m['name']] = m
        for m in v2['modelcrcs']:
            if m['name'] not in v1ms:
                diff = True
                print("Model "+str(m['name'])+" is not in file1 but present in file2", file=fh)
            else:
                if not (m['crc'] == v1ms[m['name']]['crc']):
                    diff = True
                    print("Model "+str(m['name'])+" crc differs", file=fh)
                    affectedmt[m['type']] = True
                del  v1ms[m['name']]
        for m in v1ms.values():
            diff = True
            print ("Model "+str(m['name'])+" is not in file2 but present in file1", file=fh)

    # TODO: It would be nice to have the effects/effect types in this timing region
    if args.timings:
        v1ts = {}
        for tn in v1['ttracks'].keys():
            for t in v1['ttracks'][tn]:
                if t['start'] == t['end']: # Empty from before upstream bug was fixed
                    continue
                v1ts[(tn,t['start'])] = t
        for tn in v2['ttracks'].keys():
            for t in v2['ttracks'][tn]:
                if t['start'] == t['end']: # Empty from before upstream bug was fixed
                    continue
                if (tn,t['start']) not in v1ts:
                    diff = True
                    print("Timing "+tn+":"+t['label']+"@"+str(t['start'])+"ms is not in file1 but present in file2", file=fh)
                else:
                    if not (t['crc'] == v1ts[(tn,t['start'])]['crc']):
                        diff = True
                        print("Timing "+tn+":"+t['label']+"@"+str(t['start'])+"ms crc differs", file=fh)

                        # Print out which models caused it
                        if args.timing_models and 'models' in t:
                            tm1 = t['models']
                            tm2 =  v1ts[(tn,t['start'])]['models']
                            v1ms = {}
                            for m in tm1:
                                v1ms[m['name']] = m
                            for m in tm2:
                                if m['name'] not in v1ms:
                                    diff = True
                                    print("    Model "+str(m['name'])+" is not in file1 but present in file2 in "+t['label']+"@"+str(t['start'])+"ms", file=fh)
                                else:
                                    if not (m['crc'] == v1ms[m['name']]['crc']):
                                        diff = True
                                        print("    Model "+str(m['name'])+" crc differs in "+t['label']+"@"+str(t['start'])+"ms", file=fh)
                                    del  v1ms[m['name']]
                            for m in v1ms.values():
                                diff = True
                                print ("    Model "+str(m['name'])+" is not in file2 but present in file1 in "+t['label']+"@"+str(t['start'])+"ms", file=fh)
                    del  v1ts[(tn,t['start'])]

        for tk in v1ts.keys():
            diff = True
            (tn, ts) = tk
            t = v1ts[tk]
            print("Timing "+tn+":"+t['label']+"@"+str(t['start'])+"ms is not in file2 but present in file1", file=fh)

    if diff:
        print("Differences found.  Affected model types: "+(", ".join(affectedmt.keys())), file=fh)
        print("Differences found.  Note file1 from "+xlv1+" and file2 from "+xlv2, file=fh)

    return diff

if __name__ == '__main__':
    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--channels', action='store_true',  help="Compare channels")
    parser.add_argument('-f', '--frames', action='store_true',  help="Compare frames")
    parser.add_argument('-g', '--globalcrc', action='store_true',  help="Compare global crc")
    parser.add_argument('-m', '--models', action='store_true', help='Compare model crcs')
    parser.add_argument('-t', '--timings', action='store_true', help='Compare timing section crcs')
    parser.add_argument('-l', '--timing_models', action='store_true', help='Compare model CRCs per timing section')
    #parser.add_argument('-o', '--output',   help="Path to output file")
    parser.add_argument('file1', nargs=1, help='base sequence crc summary json file')
    parser.add_argument('file2', nargs=1, help='diff sequence crc summary json file')
    #parser.add_argument('files', metavar='file', nargs=2, help='diff sequence crc summary json files')

    args = parser.parse_args()

    with open(args.file1[0]) as fh:
        v1 = json.load(fh)
    with open(args.file2[0]) as fh:
        v2 = json.load(fh)

    diff = compareSummaries(v1, v2, args, sys.stdout)

    sys.exit(1 if diff else 0)
