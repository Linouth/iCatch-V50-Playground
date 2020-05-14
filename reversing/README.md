This documents serves as a notebook for anything interesting I find during
analysis of the Akaso v50 Pro SE firmare. Most of this probably applies to 
other iCatch v50 devices but I am not sure.


## Updating the CRC checksum
The checksum is stored at offset 0x1FC of the `SPHOST.BRN` file. This checksum 
can be updated by running `sumpatch.exe (SPHOST.BRN|firmware.bin) 508`.

However, on the v50Pro SE, flashing of the firmware does not stop if the 
checksum is incorrect, so patching it is not required. 

Taken from `frm_base.ini` in the VikCam firmware.

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


## Contents of the FAT images
offset2 contains two FAT partitions, `A` starting at offset `0x120`, and `B` 
starting at `0x500120`. Linux can mount these partitions as loop devices.

The A image is a FAT16 partition. It contains most of the data used by the 
camera, such as config files, images, audio files, calibration data, etc.
Many files have a `SFN` or `SST` format. These files are compressed using 
Snappy. The `parse.py` script can parse and decompress these two file formats 
and prints the output to stdout. 

The B image is a FAT12 partition. It contains some more config files, mainly 
for wifi.

The files A\_contents.txt and B\_contents.txt list the contents of these 
partitions.


## Todo
- [ ] Update `carve.py` to also carve out the fat partitions, and the headers
- [ ] Create better tool to combine all parts into a new SPHOST file
- [ ] Create tool to compress files back into SFN and SST format
- [ ] Modify firmware so that the callibration files are loaded from the SD card
(C) instead of from image A
