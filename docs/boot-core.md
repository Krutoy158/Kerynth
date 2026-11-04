# Boot core

## Kernel configuration

`kernel/kerynth-x86_64.fragment` is an initial x86_64 kernel configuration fragment, not a complete `.config`. The build pipeline applies it to an upstream x86_64 baseline and runs `olddefconfig`. Storage and filesystem options required for the initial boot path are intended to be built in, so root discovery does not depend on modules from the media being discovered.

The current profile includes virtio block, SATA/AHCI, USB mass storage/UAS, optical SCSI, ISO9660, ext4, loop devices, SquashFS with XZ, and a serial console. This is not yet a complete device-support or firmware catalogue.

## Initramfs BusyBox

BusyBox is built statically for x86_64 and installed as `/bin/busybox` in the initramfs staging tree. Required applets are checked after building. The initramfs includes executable `/init`, `/bin/busybox`, and `/lib/kerynth-boot-mode`.

## Kernel command line

The initramfs requires exactly one `kerynth.mode` parameter. Accepted values are `installer-manual`, `installer-automatic`, `live`, and `installed`. The installed system uses `installed` in its own boot entry; it is not a fourth ISO menu choice. Missing, duplicate, or unknown modes are rejected.

### ISO boot

Each ISO GRUB entry probes the UUID of the filesystem containing the Kerynth bootloader and passes it as `kerynth.media=UUID=...`.

For `live`, `installer-manual`, and `installer-automatic`, initramfs requires exactly one media UUID and rejects a separate `root=` argument. It first resolves that UUID and attempts a read-only ISO9660 mount. If the minimal BusyBox `blkid` cannot identify the ISO UUID, it falls back only to block devices marked removable by sysfs; each candidate is mounted as ISO9660 read-only and accepted only when `live/rootfs.squashfs` exists. Fixed internal disks are not searched by this fallback, and no block device is written. The medium mount is moved into `/run/kerynth-media` inside the selected root so the Live session can still access it.

The selected mode is written to the memory-backed `/run/kerynth/boot-mode` marker. The rootfs startup dispatcher reads that marker and selects an unprivileged Live shell or the current no-write installer placeholder. The `/run` tmpfs is created by initramfs and must not be remounted by the target startup scripts, or the marker and media mount would be hidden.

### Installed boot

For `installed`, initramfs supports `root=/dev/<device>`, `root=UUID=<uuid>`, and `root=LABEL=<label>`. The root is mounted read-only by default; an installed boot entry must explicitly pass `rootflags=rw` to enable writes. Optional `rootfstype` is validated and `rootdelay` is bounded to 30 seconds.

The initramfs mounts `proc`, `sysfs`, and `devtmpfs`, creates the volatile `/run`, moves the virtual filesystems into the selected root, writes the boot-mode marker, and hands off to `/sbin/init` using BusyBox `switch_root`.

## Validation state

The init script has shell-syntax and unit-test coverage, and the GRUB/ISO validator checks the media UUID handoff. This does not prove that the image boots. GRUB UUID detection, ISO9660 UUID resolution by BusyBox `blkid`, loop-backed SquashFS mounting, QEMU console startup, Live disk non-write behavior, and clean shutdown still need end-to-end QEMU testing.
