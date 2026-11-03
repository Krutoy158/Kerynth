# Initramfs staging layout

The initramfs builder creates a deterministic gzip-compressed `newc` CPIO archive from a prepared staging directory.

Required staging files:
- `init`: executable PID 1 handoff script.
- `bin/busybox`: executable BusyBox binary containing the mount and shell applets.

The staging root may also contain kernel modules under `lib/modules/<kernel-release>/` and firmware under `lib/firmware/`. Include only modules and firmware selected for the exact target kernel and hardware profile. Firmware redistribution licenses must be reviewed separately.

Build:

```sh
python3 tools/kerynth-initramfs --root .kerynth-work/initramfs-root --output .kerynth-work/initramfs.cpio.gz
```

The builder rejects symlinks, special files, and missing required executables. It does not compile BusyBox, build the kernel, discover hardware, or prove that the image boots. The current init script mounts early virtual filesystems and hands off to `/sbin/init` on the real root; a complete boot flow still needs a tested initramfs root-discovery and switch-root implementation.
