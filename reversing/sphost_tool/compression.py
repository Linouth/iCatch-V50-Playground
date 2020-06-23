import pathlib
import sys
import snappy


def decompress(f, offset: str):
    '''Decompress Snappy compressed data. 

    Parameters
    ----------
    f : BytesIO
        The data to be decompressed (Should start with b'SNAP')
    offset : int
        The offset of the data in the bytes stream

    Returns
    -------
    BytesIO
        An identical bytes stream but decompressed (still containing the header)
    '''
    f.seek(0)
    header = f.read(offset)
    data = f.read()

    if data[:4] == b'SNAP':
        data = snappy.decompress(data[4:])
    return header + data


def compress(f, offset: int):
    '''Compress data using Snappy. 

    Parameters
    ----------
    f : BytesIO
        The data to be compressed
    offset : int
        The offset of the data in the bytes stream

    Returns
    -------
    BytesIO
        An identical bytes stream but compressed (still containing the header)
    '''
    f.seek(0)
    header = f.read(offset)
    data = f.read()

    data = snappy.compress(data)
    return header + b'SNAP' + data


def compress_helper(in_dir: str, out_dir: str, dec=False):
    '''Helper function to (de)compress files in the A or B partition folders

    Parameters
    ----------
    in_dir : str
        Directory containing files to copy / (de)compress
    out_dir : str
        Directory to store the new files
    '''
    dec_fn = decompress if dec else compress 
    dec_str = 'Decompressing' if dec else 'Compressing'
    in_dir = pathlib.Path(in_dir)
    out_dir = pathlib.Path(out_dir)

    # Loop over all files in in_dir
    for path in in_dir.glob('**/*'):
        relpath = path.relative_to(in_dir)

        with open(path, 'rb') as infile:

            # If file is to be decompressed:
            if path.suffix.upper() in ['.SST', '.SFN']:
                print(f'{dec_str} {path} > {out_dir / relpath}')
                header = infile.read(12)
                magic = header[8:8+4]

                if magic == b'SPST':
                    header_len = 0x30
                elif magic == b'SPFN':
                    header_len = 0x36
    
                data = dec_fn(infile, header_len)
            else:
                print(f'Copying {path} > {out_dir / relpath}')
                data = infile.read()

        # Write new data to file
        with open(out_dir / relpath, 'wb') as outfile:
            outfile.write(data)


def compress_dir(in_dir: str, out_dir: str):
    '''Compress all (SST|SFN) files in directory'''
    compress_helper(in_dir, out_dir)


def decompress_dir(in_dir: str, out_dir: str):
    '''Decompress all (SST|SFN) files in directory'''
    compress_helper(in_dir, out_dir, True)

    
if __name__ == '__main__':
    if sys.argv[1] in ['c', 'compress']:
        compress_dir(sys.argv[2], sys.argv[3])
    elif sys.argv[1] in ['d', 'decompress']:
        decompress_dir(sys.argv[2], sys.argv[3])
