#!/bin/python

import snappy
import sys


if len(sys.argv) < 4:
    print(f'Usage: {sys.argv[0]} <infile> <offset> <outfile>')
    sys.exit(1)


with open(sys.argv[1], 'rb') as infile:
    infile.seek(int(sys.argv[2]))
    data = infile.read()
    dec = snappy.decompress(data)

    with open(sys.argv[3], 'wb') as outfile:
        size = outfile.write(dec)
        print(f'Written {size} bytes')
