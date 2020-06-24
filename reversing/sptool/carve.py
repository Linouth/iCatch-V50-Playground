#!/bin/python3

'''
This script carves the different parts from a SPHOST.BRN file. It splits the
fat partitions into separate files which can be mounted as a linux loop device.
'''

import os
import struct
import sys


SPHOST_FAT_INDEX = 2
SPHOST_FAT_HEADER = 0x120

DEFAULT_FILES = ['SPHOST.header', 'offset0', 'offset1', 'offset2.header',
        'offset2.A', 'offset2.B', 'offset3', 'offset5', 'offset6']


class Struct(object):
    '''
    A class to unpack a binary into a structure like container
    '''
    data = {}
    __getitem__ = data.get

    def __init__(self, fields, data, endianness='<'):
        '''
        E.g.:
        header = Struct([
            ('magic', '8s'),
            ('filesize', 'I'),
            ('items', [
                (0, 'I'),
                (1, 'I')
            ])
        ], data, endianness='>')

        Parameters
        ----------
        fields : list(tuple)
            The fields list has to contain entries like
            ('name', 'struct_format') or ('name', value). Value can be another
            list of tuples to build a tree.
        in_data : bytearray
            The data to parse
        endianness : chr
            '<' for little-endian, '>' for big-endian

        '''
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
    '''Carve block of bytes from infile and save into outfile

    Parameters
    ----------
    infile : BytesIO
        File to carve from
    outfile : BytesIO
        File to save to
    size : int
        Number of bytes to carve
    offset : int
        The offset to start at
    '''
    print(f'{infile} > {outfile} @0x{offset:02x} 0x{size:02x}')
    with open(infile, 'rb') as infile, open(outfile, 'wb') as outfile:
        infile.seek(offset)
        data = infile.read(size)
        outfile.write(data)


def carve_firmware(FILENAME='SPHOST.BRN'):
    '''Carve all chunks from a SPHOST.BRN firmware file

    This also saves the A and B fat partitions in separate files

    Parameters
    ----------
    FILENAME : str
        The filename of the SPHOST.BRN(-like) firmware file
    '''

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


def combine_firmware(outfile='SPHOST.BRN', files=None, directory='./'):
    '''Combine carved out chunks into a single firmware file

    Parameters
    ----------
    outfile : str
        File to save the firmware file to
    files : list(str)
        List of chunks to copy into firmware file. NOTE: The order is very
        important. 
    directory : str
        Directory where the chunks are located
    '''
    if not files:
        files = DEFAULT_FILES

    # Do nothing if directory or outfile are not valid
    if not os.path.isdir(directory):
        return

    # Open firmware file to read to 
    with open(outfile, 'wb') as f:

        # Loop over files to combine
        for filename in files:
            filename = os.path.join(directory, filename)
            print(f'Concatting {filename} into {outfile}')

            try:

                # Copy file contents to firmware file
                with open(filename, 'rb') as infile:
                    data = infile.read()
                    f.write(data)
            except FileNotFoundError:
                print(f'File {filename} not found.')
                break


def clean(files=None):
    f'''Delete all carved out files

    Parameters
    ----------
    files : list(str)
        List of files to delete. Defaults to {DEFAULT_FILES}
    '''
    if not files:
        files = DEFAULT_FILES

    for f in files:
        try:
            os.remove(f)
            print(f'Removing {f}.')
        except FileNotFoundError:
            print(f'{f} already gone')
            pass
    print('Done.')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} (carve|combine) file [file2 file3 ...]')
        print('Default files for combining: ')
        for f in DEFAULT_FILES:
            print(f'{f} ' , end='')
        sys.exit(1)
    else:
        FILENAME = sys.argv[2] if len(sys.argv) > 2 else 'SPHOST.BRN'

    if not os.path.isfile(FILENAME):
        print(f'Error: File {FILENAME} not found.')
        sys.exit(1)

    if sys.argv[1] == 'carve':
        carve_firmware(FILENAME)
    elif sys.argv[1] == 'combine':
        combine_firmware('SPHOST.BRN.new', sys.argv[2:])
