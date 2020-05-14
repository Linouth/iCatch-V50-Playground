#!/bin/python

'''
Carve offsets from SUNP BURN files.
'''

import struct
import sys
import pprint

if len(sys.argv) > 1:
    FILENAME = sys.argv[1]
else:
    FILENAME = 'SPHOST.BRN'

head = b''
try:
    with open(FILENAME, 'rb') as f:
        head = f.read(0x200)
except FileNotFoundError:
    print(f'File {FILENAME} not found.')
    print(f'Usage: {sys.argv[0]} [<SPHOST.BRN file>]')
    sys.exit(1)


header = {
        'magic': head[0:0x10],
        'filesize': struct.unpack_from('<I', head, 0x10)[0],
        'offsets': {
            'offset0': 0x200,  # ISP Bootloader?
            'offset1': struct.unpack_from('<I', head, 0x14)[0],  # BIMG Fat16
            'offset2': struct.unpack_from('<I', head, 0x18)[0],  # BIMG Fat12
            'offset3': struct.unpack_from('<I', head, 0x1c)[0],  # CIMG or firmware bin file ?
            # 'offset4': struct.unpack_from('<I', head, 0x20)[0],  # Not in use?
            'offset5': struct.unpack_from('<I', head, 0x24)[0],  # Bad pixel calibration info
            'offset6': struct.unpack_from('<I', head, 0x28)[0],  # DRAM settings
        },
        'CRC': struct.unpack_from('<I', head, 0x1fc)[0]
}
pprint.pprint(header)


offsets = header['offsets']
with open(FILENAME, 'rb') as in_file:
    keylist = sorted(offsets.keys())
    for i,k in enumerate(keylist):
        try:
            count = offsets[keylist[i+1]] - offsets[k]
        except:
            count = header['filesize'] - offsets[k]

        print(f'{k}, 0x{offsets[k]:02x}: {count}')
        with open(k, 'wb') as out_file:
            in_file.seek(offsets[k])
            data = in_file.read(count)
            out_file.write(data)
