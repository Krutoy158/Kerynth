# Initramfs staging layout

The initramfs builder creates a deterministic gzip-compressed `newc` CPIO archive from a prepared staging directory.

Required staging files:
- `init`: executable PID 1 handoff script.
- `bin/busybox`: executable BusyBox binary containing the mount and shell applets.
- `lib/kerynth-boot-mode`: executable parser for the required `kerynth.mode` kernel argument.

The staging root may also contain kernel modules under `lib/modules/<kernel-release>/` and firmware under `lib/firmware/`. Include only modules and firmware selected for the exact target kernel and hardware profile. Firmware redistribution licenses must be reviewed separately.

Build:

```sh
python3 tools/kerynth-initramfs --root .kerynth-work/initramfs-root --output .kerynth-work/initramfs.cpio.gz
```

The builder rejects symlinks, special files, and missing required executables. It does not compile BusyBox, build the kernel, discover hardware, or prove that the image boots. The PID 1 script validates the selected boot mode, mounts the selected root read-only by default, creates a memory-backed `/run`, writes the validated mode to `/run/kerynth/boot-mode`, and hands off to `/sbin/init`. The target init system still needs mode-specific integration, and the Live ISO root-mount path remains to be implemented and tested.
