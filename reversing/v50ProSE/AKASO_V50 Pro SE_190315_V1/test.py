'''
Beginning of a better script to carve and unpack firmware
'''


import struct
from collections import namedtuple
import pprint

f = open('SPHOST.BRN', 'rb')

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
                    root[name] = struct.unpack_from(endianness+f, in_data, offset)[0]
                    offset += struct.calcsize(f)
                else:
                    root[name] = f
            return offset
        up(fields, in_data, self.data, 0)

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

f.seek(header['offset'][2] + 0x120)
fat16hdr = Struct([
    (None, '3B'),
    ('oem', '8s'),
    ('bytes_per_sector', 'H'),
    (None, '6B'),
    ('sectors', 'H')
    ], f.read(0x160-0x120))

print(fat16hdr['bytes_per_sector'])
print(fat16hdr['sectors'])

pprint.pprint(header['offset'])

