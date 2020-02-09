# iCatch V50 playground
This repo is used to as a playground for reversing the iCatch V50 chipset, or SPCA6500. I will dump all useful and interesting info I can find about this chipset in this repo.

Any contribution on reversing this system is greatly appreciated.


### Interesting links:
* [Info about SPHOST.BRN file](https://www.goprawn.com/forum/sunplus-cams/10333-icatch-sunplus-firmware-hacks)
* [FRM Program](https://www.goprawn.com/forum/sunplus-cams/748-hack-mod-eken-h9-firmware-using-frm)
* [Some reversing of this chipset (mainly the linux part)](https://github.com/mheistermann/spca-fun)
* [Official firmware download, from akaso](http://akaso.net/firmware/AKASO_V50_Pro_20180802_V4.rar)
* [Unofficial firmware repo (Thanks to Petesimon on GoPrawn)](https://my.pcloud.com/publink/show?code=GDkrtalK)


### Unbricking
[*Thanks to DrekiTech on GoPrawn*](https://www.goprawn.com/forum/sunplus-cams/5859-sunplus-v50-soc?p=9886#post9886)
*This does not work on the Akaso V50 Pro. It doesn't go into 'debug mode' with these steps.*

```
In order to enter debug mode, the following steps must be performed:

- Press and hold shutter button (do not release it)
- Plug camera in by USB
- Click power button
- Release shutter button

After that it'll show up in the device manager as Icatch(X) KX Series Bulk Camera Device and Icatch(X) KX Series Null Device and then you can use the FRM.exe to flash the firmware.
```
