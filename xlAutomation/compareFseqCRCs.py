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
        # Comp blocks can easily be noisy, I presume




    sys.exit(1 if diff else 0)
