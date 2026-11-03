# Boot core

## Kernel configuration

`kernel/kerynth-x86_64.fragment` is an initial x86_64 kernel configuration fragment, not a complete `.config`. Apply it to a reviewed upstream kernel baseline with the kernel's `scripts/kconfig/merge_config.sh` and run `olddefconfig`. Review every resulting option and build the kernel in an isolated workspace. Drivers selected as built-in (`=y`) are available before root discovery; modular drivers must be copied into the initramfs for the exact kernel release and have their dependencies loaded before the root device can be found.

## Initramfs BusyBox

`initramfs/busybox.config.fragment` lists the applets required by the current init script. BusyBox must be built statically for x86_64 and installed as `/bin/busybox` in the staging root. Do not assume a distribution-provided BusyBox has these applets or is statically linked; verify its build configuration and `busybox --list` output.

## Kernel command line

The init script supports:
- `root=/dev/<device>`
- `root=UUID=<uuid>`
- `root=LABEL=<label>`
- optional `rootfstype=<filesystem>`
- optional `rootflags=rw` (otherwise root is mounted read-only)
- optional `rootdelay=<seconds>` (bounded to 30)

UUID/LABEL discovery uses BusyBox `find` and `blkid`. The script mounts the root, moves `/dev`, `/proc`, and `/sys`, creates a temporary `/run`, and hands off to `/sbin/init` through BusyBox `switch_root`. The emergency shell is used when root discovery or handoff fails.

This is an early boot implementation, not yet proven on a real kernel. Before marking the boot core complete, test direct device, UUID, LABEL, missing-device, unsupported-filesystem, and missing-init cases in QEMU. Ensure storage controllers and filesystems needed to reach the root are built into the kernel or loaded from initramfs. The current initramfs builder rejects symlinks, so staging must not rely on applet symlinks.
