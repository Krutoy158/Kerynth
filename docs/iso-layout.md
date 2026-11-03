# ISO Staging Layout

The build pipeline assembles one explicit staging tree under `.kerynth-work/iso-root/`:

```text
iso-root/
├── boot/
│   ├── grub/
│   │   └── grub.cfg
│   ├── vmlinuz
│   └── initramfs.cpio.gz
└── live/
    └── rootfs.squashfs
```

## Boot menu

The GRUB menu contains exactly three English choices:

- Manual Installation
- Automatic Installation
- Live System

The KER ASCII logo is shown without system information, and the menu has no automatic timeout. Every entry probes the boot filesystem UUID and passes it to initramfs as `kerynth.media=UUID=...`.

## Required artifacts

- `boot/grub/grub.cfg` — the approved KER menu with media UUID handoff.
- `boot/vmlinuz` — built x86_64 Linux kernel.
- `boot/initramfs.cpio.gz` — gzip-compressed newc CPIO with executable `/init`, `/bin/busybox`, and `/lib/kerynth-boot-mode`.
- `live/rootfs.squashfs` — read-only compressed root filesystem created from the minimal Kerynth rootfs.

## Commands

Build the complete staging tree:

```sh
make iso-stage
```

Validate it:

```sh
make iso-check
```

Package the ISO:

```sh
make iso
```

Run all stages in sequence:

```sh
make build
```

The packager uses `grub-mkrescue` and `xorriso`. It writes only below `.kerynth-work/`, does not use sudo, and does not access block devices.

## Current limitations

The initramfs code now contains the explicit read-only media mount and SquashFS handoff, but the actual kernel, rootfs, initramfs, and ISO have not yet been built and boot-tested together in QEMU. The installer entries still reach a placeholder that performs no installation and does not modify disks. No release ISO should be advertised as bootable until QEMU tests verify boot, console login, read-only Live behavior, and shutdown.
