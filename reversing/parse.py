#!/bin/python

'''
SST and SFN files follow this format:
    magic   : RIFF
    length  : total length of file
    type    : type of file (SPST | SPFN)

    ID      : ?
    size    : length of chunk
    data    : data

    ...

    ID
    size
    data

    ID      : comp
    size    : 0x0e
    data    : S.U.N.P.L.U.S.

    ID      : dsgn
    size    : 0x0e
    data    : S.U.N.P.L.U.S.
'''

import sys
import struct
import snappy
import io


def read_data(f, offset):
    f.seek(offset)
    data = f.read()

    if data[:4] == b'SNAP':
        data = snappy.decompress(data[4:])
    return data


if len(sys.argv) < 2:
    print(f'Usage: {sys.argv[0]} <file>')
    sys.exit(1)

filename = sys.argv[1]

with open(filename, 'rb') as f:
    header = f.read(0x3f)
    magic = header[8:8+4]

    data = None
    if magic == b'SPST':
        rawdata = io.BytesIO(read_data(f, 0x30))
        length, _, _, entries = struct.unpack('<IHHH', header[0x26:0x30])
        # length = length - 6 + 0x30

        with open('out.bin', 'wb') as outf:
            while True:
                data = rawdata.read(1024)
                if data == b'':
                    break
                outf.write(data)
            rawdata.seek(0)

        print(length, entries)
        
        data = []
        while True:
            index, size = struct.unpack('<HH', rawdata.read(4))
            data.append(rawdata.read(size))
            if index == entries-1: break

        for e in data:
            print(e.decode('utf-16'))
        print(len(data))

    elif magic == b'SPFN':
        data = read_data(f, 0x36)
        length, _, _, _ = struct.unpack('<IHHH', header[0x26:0x30])
        # length = length - 6 + 0x30

        sys.stdout.buffer.write(header[:0x36])
        sys.stdout.buffer.write(data)
        sys.stdout.flush()


# 0x437b
