This documents serves as a notebook for anything interesting I find during
analysis of the Akaso v50 Pro SE firmare. Most of this probably applies to 
other iCatch v50 devices but I am not sure.


## Updating the CRC checksum
The checksum is stored at offset 0x1FC of the `SPHOST.BRN` file. This checksum 
can be updated by running `sumpatch.exe (SPHOST.BRN|firmware.bin) 508`.

However, on the v50Pro SE, flashing of the firmware does not stop if the 
checksum is incorrect, so patching it is not required. 

## Carving
The script `carve.py` accepts any SPHOST.BRN file and carves out the different 
parts defined by the header. The script names these parts as `offsetX`, and I 
refer to them as such. The file contains the following parts:

- offset0: Bootloader (spca6500isp.bin)
- offset1: Unknown?
- offset2: Data. This seciton contains a FAT16 image (A) and a FAT12 image (B)
- offset3: Firmare
- offset4: Unknown/Unused?
- offset5: Pixel calibration data
- offset6: drampara-ddr.prm

Thanks to [nutsey](https://www.goprawn.com/forum/sunplus-cams/10333-icatch-sunplus-firmware-hacks?p=17034#post17034) 
and the VikCam firmware for most of this information. 


## Memory mapping
- offset0, the bootloader, is mapped to `0x40040000`
- offset3, the firmware, is mapped to `0x40000000`
- offset6, drampara-ddr.prm, is mapped to `0x47ff0000`


## Ghidra
`offset3.gzf` contains my current progress at reversing the main firmware.
Functions with a `?` are not 100% certain, and functions with a `!` can be
interesting and need more thorough look.


## The FAT images
offset2 contains two FAT partitions, `A` starting at offset `0x120`, and `B` 
starting at `0x500120`. Linux can mount these partitions as loop devices.

### Contents
The A image is a FAT16 partition. It contains most of the data used by the 
camera, such as config files, images, audio files, calibration data, etc.
Many files have a `SFN` or `SST` format. These files are compressed using 
Snappy. The `parse.py` script can parse and decompress these two file formats 
and prints the output to stdout. 

The B image is a FAT12 partition. It contains some more config files, mainly 
for wifi.

The files A\_contents.txt and B\_contents.txt list the contents of these 
partitions.

### Modifying the partitions
Changing the FAT partitions is fairly easy. Just follow these steps:
1. Carve the firmware using `carve.py SPHOST.BRN`
2. Mount the FAT image with `mount -o loop,rw offset2.A <dir>`
3. You can now access and modify the image.
4. Unmount the image: `umount <dir>`
5. build a new SPHOST.BRN file using `combine.sh`

That should work.

I have been able to change system icons, boot images and sounds. There are also
plenty of configuration and callibration files which I am not sure of what they
do. They might be very interesting to play with. Any help with working this out
is highly appreciated. 


## Todo
- [x] Update `carve.py` to also carve out the fat partitions, and the headers
- [ ] Create better tool to combine all parts into a new SPHOST file
- [ ] Create tool to compress files back into SFN and SST format
- [ ] Modify firmware so that the callibration files are loaded from the SD card
(C) instead of image A
- [ ] Modify firmware to intercept received messages so I can analyse them
