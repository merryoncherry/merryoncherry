#Python module to read fseq files and summarize them
import argparse
import binascii
import io
import json
import os
import sys

def CRC32_from_file(filename):
    buf = open(filename,'rb').read()
    buf = (binascii.crc32(buf) & 0xFFFFFFFF)
    return "%08X" % buf

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

if __name__ == '__main__':
    hjson = {}
    with open(sys.argv[1], 'rb') as fh:
        hdr = fh.read(4)
        shdr = str(hdr, 'utf-8')
        #print(shdr)
        if (shdr != 'PSEQ' and shdr != 'ESEQ'):
            raise Exception("Not a PSEQ file")
        hjson['hdr4']=shdr
        off2chdata = read16bit(fh)
        #print("offset to channel data: "+str(off2chdata))
        hjson['chdata_offset']=off2chdata
    print(json.dumps(hjson))

