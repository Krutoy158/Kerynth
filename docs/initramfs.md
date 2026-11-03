# Initramfs staging layout

The initramfs builder creates a deterministic gzip-compressed `newc` CPIO archive from a prepared staging directory.

Required staging files:
- `init`: executable PID 1 handoff script.
- `bin/busybox`: statically linked x86_64 BusyBox binary containing the required mount, shell, device, and session applets.
- `lib/kerynth-boot-mode`: executable parser for the required `kerynth.mode` kernel argument.

Build the rootfs and kernel first, then generate the initramfs from the built BusyBox:

```sh
make rootfs
make kernel
make initramfs
```

The generated archive is written below `.kerynth-work/`. It rejects symlinks, special files, and missing required executables.

## ISO boot modes

For `live`, `installer-manual`, and `installer-automatic`, the initramfs expects one `kerynth.media=UUID=...` argument. It resolves only that filesystem UUID, mounts the boot medium read-only, finds `live/rootfs.squashfs`, and mounts that SquashFS image read-only with loop support.

For `installed`, the initramfs expects one `root=` argument supporting a device path, UUID, or LABEL. The installed root is mounted read-only unless `rootflags=rw` is explicitly supplied.

After selecting the root, the script moves `/dev`, `/proc`, and `/sys`, creates a memory-backed `/run`, stores the selected mode in `/run/kerynth/boot-mode`, and hands off to `/sbin/init` using BusyBox `switch_root`. The ISO media mount is preserved below `/run/kerynth-media`.

The target rootfs startup scripts must not remount `/run`: doing so hides the volatile boot-mode marker and the preserved Live media mount.

## Limitations

The initramfs code and its static/unit-test checks are present, but it has not yet been booted with the generated kernel in QEMU. Module loading, firmware staging, storage retry policy, encrypted/LVM/RAID roots, and physical USB/optical boot testing remain open.
