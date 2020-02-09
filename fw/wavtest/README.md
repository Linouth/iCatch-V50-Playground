## Modified firmware for Akaso V50 Pro
**Not tested yet!**

This (the `SPHOST_new.BRN` file) is a modified version of the V4 firmware from Akaso. The only thing I have changed is replace the startup sound with a reversed version.

This was done by extracting the fat16 img at offset2 from the original firmware, mounting and modifying it, and then combining everything again. The V4 version of the original firmware does not have a CRC checksum, so I assume it is not required.

Again, this image has not been tested yet. If you want to test it, feel free to do so. **However, I am not responsible for a bricked camera**.
