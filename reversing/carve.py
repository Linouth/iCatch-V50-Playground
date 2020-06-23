#!/bin/python3

'''
This script carves the different parts from a SPHOST.BRN file. It splits the
fat partitions into separate files which can be mounted as a linux loop device.
'''

import os
import struct
import sys

if len(sys.argv) > 1:
    FILENAME = sys.argv[1]
else:
    FILENAME = 'SPHOST.BRN'

if not os.path.isfile(FILENAME):
    print(f'Error: File {FILENAME} not found.')
    print(f'Usage: {sys.argv[0]} <SPHOST.BRN file>')
    sys.exit(1)

SPHOST_FAT_INDEX = 2
SPHOST_FAT_HEADER = 0x120

class Struct(object):
    data = {}
    __getitem__ = data.get

    def __init__(self, fields, data, endianness='<'):
        self._unpack(fields, data, endianness)

    def _unpack(self, fields, in_data, endianness):
        def up(fields, in_data, root, offset):
            for name, f in fields:
                if name == None:
                    offset += struct.calcsize(f)
                    continue
                if type(f) == list:
                    root[name] = {}
                    offset = up(f, in_data, self.data[name], offset)
                elif type(f) == str:
                    root[name] = struct.unpack_from(endianness+f,in_data,
                            offset)[0]
                    offset += struct.calcsize(f)
                else:
                    root[name] = f
            return offset
        up(fields, in_data, self.data, 0)


def carve(infile, outfile, size, offset=0):
    print(f'{infile} > {outfile} @0x{offset:02x} 0x{size:02x}')
    with open(infile, 'rb') as infile, open(outfile, 'wb') as outfile:
        infile.seek(offset)
        data = infile.read(size)
        outfile.write(data)


def carve_firmware(FILENAME):

    # Read and parse SPHOST.BRN header
    with open(FILENAME, 'rb') as f:
        header = Struct([
            ('magic', '16s'),
            ('filesize', 'I'),
            ('offset', [
                (0, 0x200),
                (1, 'I'),
                (2, 'I'),
                (3, 'I'),
                (4, 'I'),
                (5, 'I'),
                (6, 'I')
                ]),
            ('crc', 'I')
            ], f.read(0x200))

    # Carve header to later reconstruct the SPHOST.BRN file
    carve(FILENAME, 'SPHOST.header', 0x200, 0)

    for index,offset in header['offset'].items():

        # Skip empty offset and the fat offset as this needs to be carved
        # differently
        if offset > 0 and index != SPHOST_FAT_INDEX:

            # Read offset from header and determine block size
            try:
                i = index
                while True:
                    i += 1
                    to_read = header['offset'][i];
                    if to_read != 0: break
                to_read -= offset
            except:
                to_read = header['filesize'] - offset

            # Write blocks to separate files
            print(f'{index}, 0x{offset:02x}: {to_read}')
            carve(FILENAME, f'offset{index}', to_read, offset)


    # Carve AB Fat part header to later reconstruct a modified A or B partition
    carve(FILENAME, f'offset{SPHOST_FAT_INDEX}.header', SPHOST_FAT_HEADER,
            header['offset'][SPHOST_FAT_INDEX])

    with open(FILENAME, 'rb') as f:
        # Read and carve FAT16 (A) partition
        offset = header['offset'][SPHOST_FAT_INDEX] + SPHOST_FAT_HEADER
        f.seek(offset)
        fat16hdr = Struct([
            (None, '3B'),
            ('oem', '8s'),
            ('bytes_per_sector', 'H'),
            (None, '6B'),
            ('sectors', 'H')
            ], f.read(0x40))
        fat16size = fat16hdr['bytes_per_sector'] * fat16hdr['sectors']
        carve(FILENAME, f'offset{SPHOST_FAT_INDEX}.A', fat16size, offset)

        # Read and carve FAT12 (B) partition
        offset = header['offset'][SPHOST_FAT_INDEX] + fat16size + SPHOST_FAT_HEADER
        f.seek(offset)
        fat12hdr = Struct([
            (None, '3B'),
            ('oem', '8s'),
            ('bytes_per_sector', 'H'),
            (None, '6B'),
            ('sectors', 'H')
            ], f.read(0x40))
        fat12size = fat12hdr['bytes_per_sector'] * fat12hdr['sectors']
        carve(FILENAME, f'offset{SPHOST_FAT_INDEX}.B', fat12size, offset)


carve_firmware(FILENAME)
