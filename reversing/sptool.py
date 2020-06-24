#!/bin/python3

import sptool.carve
import sptool.compression

import argparse
import sys


class SPTool(object):

    def __init__(self):

        # Build list of available commands, with their help text
        commands = {}
        for command in filter(lambda x: '__' not in x, dir(self)):
            commands[command] = getattr(self, command).help 

        parser = argparse.ArgumentParser(
                description='SunPlus firmware utility',
                formatter_class=argparse.RawTextHelpFormatter)

        # Add 'command' entry and print list of command and help texts
        parser.add_argument(
                'command',
                metavar='command',
                choices=commands.keys(),
                help='Available commands are:\n' + 
                     '\n'.join([f'{k:12}\t{v}' for k,v in commands.items()]))

        args = parser.parse_args(sys.argv[1:2])

        # Run command function
        getattr(self, args.command)()

    def carve(self):
        parser = argparse.ArgumentParser(description=self.carve.help)

        parser.add_argument('file', help='Firmware file',
                default='SUNPLUS.BRN')

        args = parser.parse_args(sys.argv[2:])
        sptool.carve.carve_firmware(args.file)
        return
    carve.help = 'Carve firmware file into separate chunks ' \
                 'and extract A and B partitions.'

    def combine(self):
        parser = argparse.ArgumentParser(description=self.combine.help)

        parser.add_argument('-f', '--filenames', required=True,
                help='Filenames of chunks to combine, in the correct order. '
                f'Default: {sptool.carve.DEFAULT_FILES}',
                default=None)
        parser.add_argument('-d', '--dir', required=True,
                help='Directory where chunks are located', default=None)
        parser.add_argument('-o', '--outfile', required=True,
                help='File to write firmware to', default=None)

        args = parser.parse_args(sys.argv[2:])
        sptool.carve.combine_firmware(args.outfile, args.files, args.dir)
        return
    combine.help = 'Combine carved chunks back into a firmware file.'

    def compress(self):
        parser = argparse.ArgumentParser(description=self.compress.help)

        parser.add_argument('indir',
                help='Directory with SST and SFN files to compress')
        parser.add_argument('outdir',
                help='Directory to save newly compressed files')

        args = parser.parse_args(sys.argv[2:])
        sptool.compression.compress_dir(args.indir, args.outdir)
        return
    compress.help = 'Compress all SST and SFN files in a specified folder. '\
                   'Also copies any other file to the new directory.'

    def decompress(self):
        parser = argparse.ArgumentParser(description=self.decompress.help)

        parser.add_argument('indir',
                help='Directory with SST and SFN files to decompress')
        parser.add_argument('outdir',
                help='Directory to save newly decompressed files')

        args = parser.parse_args(sys.argv[2:])
        sptool.compression.decompress_dir(args.indir, args.outdir)
        return
    decompress.help = 'Decompress all SST and SFN files in the specified '\
        'folder. Also copies any other file to the new directory.'

    def clean(self):
        parser = argparse.ArgumentParser(description=self.clean.help)

        parser.add_argument('-f' '--files', help=f'List of files to delete. '\
                        'Defaults to {sptool.carve.DEFAULT_FILES}',
                        nargs='*', default=None)

        args = parser.parse_args(sys.argv[2:])
        sptool.carve.clean()
        return
    clean.help = 'Delete all carved files (or the files in --files)'


if __name__ == '__main__':
    tool = SPTool()
