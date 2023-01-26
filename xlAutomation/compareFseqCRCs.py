# Module to compare two fseq summaries made by fseqFile.py

import argparse
import io
import json
import os
import sys
import xml.dom.minidom

if __name__ == '__main__':
    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--channels', action='store_true',  help="Compare channels")
    parser.add_argument('-f', '--frames', action='store_true',  help="Compare frames")
    parser.add_argument('-g', '--globalcrc', action='store_true',  help="Compare global crc")
    #parser.add_argument('-s', '--sequence', help="Path to effect sequence .xsq file")
    #parser.add_argument('-o', '--output',   help="Path to output file")
    parser.add_argument('file1', nargs=1, help='base sequence crc summary json file')
    parser.add_argument('file2', nargs=1, help='diff sequence crc summary json file')
    #parser.add_argument('files', metavar='file', nargs=2, help='diff sequence crc summary json files')

    args = parser.parse_args()

    with open(args.file1[0]) as fh:
        v1 = json.load(fh)
    with open(args.file2[0]) as fh:
        v2 = json.load(fh)

    xlv1 = v1['headers']['sp'] if 'sp' in v1['headers'] else '<unknown>'
    xlv2 = v2['headers']['sp'] if 'sp' in v2['headers'] else '<unknown>'

    # OK compare them
    diff = False
    if args.channels:
        if v1['hdr4'] != v2['hdr4']:
            diff = True
            print("Header 4 differs: "+v1['hdr4']+" vs "+v2['hdr4'])
        if v1['majver'] != v2['majver']:
            diff = True
            print("Major version differs: "+str(v1['majver'])+" vs "+str(v2['majver']))
        if v1['minver'] != v2['minver']:
            diff = True
            print("Minor version differs: "+str(v1['minver'])+" vs "+str(v2['minver']))
        if v1['channels'] != v2['channels']:
            diff = True
            print("Channel count differs: "+str(v1['channels'])+" vs "+str(v2['channels']))
        if v1['frames'] != v2['frames']:
            diff = True
            print("Frame count differs: "+str(v1['frames'])+" vs "+str(v2['frames']))
        if v1['msperframe'] != v2['msperframe']:
            diff = True
            print("Framerate differs: "+str(v1['msperframe'])+" vs "+str(v2['msperframe']))
        if v1['nsparseranges'] != v2['nsparseranges']:
            diff = True
            print("Sparse range count differs: "+str(v1['nsparseranges'])+" vs "+str(v2['nsparseranges']))

        # TODO: Compare sparse ranges if asked; might be nice to know, but if it works, it works
        # Comp blocks can easily be noisy, I presume, and no such thing as correctness.

    if args.globalcrc:
        if v1['globalcrc'] != v2['globalcrc']:
            diff = True
            print("Global CRC differs: "+v1['globalcrc']+" vs "+v2['globalcrc'])

    if args.frames:
        v1fs = {}
        for f in v1['framecrcs']:
            v1fs[f['frame']] = f
        for f in v2['framecrcs']:
            if f['frame'] not in v1fs:
                diff = True
                print("Frame "+str(f['frame'])+" is black in file1 but present in file2")
            else:
                if not (f['crc'] == v1fs[f['frame']]['crc']):
                    diff = True
                    print("Frame "+str(f['frame'])+" crc differs")
                del  v1fs[f['frame']]
        for f in v1fs.values():
            diff = True
            print ("Frame "+str(f['frame'])+" is black in file2 but present in file1")

    if diff:
        print("Differences found.  Note file1 from "+xlv1+" and file2 from "+xlv2)

    sys.exit(1 if diff else 0)
