# ISO Staging Layout

The ISO assembly prototype uses one explicit staging tree:

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

## Required artifacts

- `boot/grub/grub.cfg` is the approved KER menu. It must contain exactly the Manual Installation, Automatic Installation, and Live System entries, with no automatic timeout.
- `boot/vmlinuz` is the built x86_64 Linux kernel.
- `boot/initramfs.cpio.gz` is a gzip-compressed newc CPIO archive. It must contain executable `/init`, `/bin/busybox`, and `/lib/kerynth-boot-mode`.
- `live/rootfs.squashfs` is the compressed live userspace image.

## Validation and assembly

Run the staging checks:

```sh
python3 tools/kerynth-iso check
```

Build the ISO after the required artifacts are present and validated:

```sh
python3 tools/kerynth-iso build
```

The same commands are available as `make iso-check` and `make iso`. The builder uses `grub-mkrescue` and requires the GRUB BIOS/EFI tools and `xorriso`.

The staging validator rejects symbolic links and special files, checks the exact boot menu, parses the initramfs CPIO entries, checks the required executable boot files, and verifies the SquashFS superblock magic. The output ISO is written only under `.kerynth-work/`; the tool does not use sudo, write boot entries, partition disks, or access block devices.

## Limitations

This is an ISO packaging prototype, not a claim that a bootable Kerynth ISO exists. The kernel file is checked for presence but is not built or ABI-validated by this tool. The SquashFS image is checked for its magic and minimum superblock size, not fully decompressed or cryptographically verified. Most importantly, the current initramfs still needs an ISO-media discovery and SquashFS mount path, and the target userspace still needs to dispatch the three boot modes into real installer and Live sessions. A successful ISO assembly alone does not prove that the image boots. QEMU boot and disk-safety tests remain mandatory before release.
