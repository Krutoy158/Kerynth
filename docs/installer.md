# Kerynth installer development

## GPT partition layout planner

`tools/kerynth-install-layout` generates and validates GPT partition plans. It is deliberately separate from disk-writing operations.

The automatic plan creates a 512 MiB EFI System Partition followed by an ext4 root partition using the remaining usable capacity. The manual plan accepts exactly one EFI partition and one root partition, with start and size expressed in whole MiB.

Both modes support 512-byte and 4096-byte logical sectors. The planner checks GPT usable-sector bounds, 1 MiB alignment, duplicate partition roles, minimum sizes, partition order, and overlap. It produces JSON or an `sfdisk` script for review.

### Automatic example

For an 8 GiB virtual disk with 512-byte sectors:

```sh
python3 tools/kerynth-install-layout \
  --disk-bytes 8589934592 \
  --sector-size 512 \
  --mode automatic
```

To print only the partition-table script:

```sh
python3 tools/kerynth-install-layout \
  --disk-bytes 8589934592 \
  --sector-size 512 \
  --mode automatic \
  --format sfdisk
```

### Manual example

Create a JSON file describing the two partitions:

```json
{
  "partitions": [
    {
      "role": "efi",
      "start_mib": 1,
      "size_mib": 512
    },
    {
      "role": "root",
      "start_mib": 513,
      "size_mib": 7000
    }
  ]
}
```

Then validate it:

```sh
python3 tools/kerynth-install-layout \
  --disk-bytes 8589934592 \
  --sector-size 512 \
  --mode manual \
  --layout-json ./layout.json
```

The generated plan contains `writes_performed: false`. The planner does not discover block devices, create partition tables, format filesystems, mount targets, or install a bootloader.

## Disk-image partition writer

`tools/kerynth-install-image` is a separate developer/test utility. It applies a generated GPT plan only to an existing regular file ending in `.img` or `.raw`. It refuses block devices, symbolic links, hard-linked files, and images whose size does not exactly match the plan. The command requires the explicit `--confirm-overwrite-image` option and reads the resulting GPT table back with `sfdisk --json` to verify partition starts, sizes, names, and type GUIDs.

It does not accept `/dev/sda`, NVMe device nodes, or any other block device. It writes only to the selected image file. The content of that image file is changed, so use a disposable test image.

Example for a 4 GiB test image:

```sh
truncate -s 4294967296 ./kerynth-test.img
python3 tools/kerynth-install-image \
  --image ./kerynth-test.img \
  --disk-bytes 4294967296 \
  --sector-size 512 \
  --mode automatic \
  --confirm-overwrite-image
```

This is not yet the physical-disk installer. It only writes and verifies a partition table in a regular image file; it does not create filesystems, mount partitions, copy the OS, create user accounts, or install a bootloader.

## Staged installation tree

`tools/kerynth-install-tree` prepares an installed Kerynth filesystem tree for development and testing. It reads only the generated `.kerynth-work/rootfs/`, kernel image, and initramfs, then writes a new target directory below `.kerynth-work/targets/`.

The helper:

- Copies the base root filesystem while rejecting escaping symbolic links and special files.
- Replaces the default Live account with the requested first local user and a supplied crypt password hash.
- Sets the hostname and creates a host table.
- Writes an ext4 root entry in `/etc/fstab`.
- Copies the kernel and initramfs into `/boot`.
- Writes a GRUB configuration using the selected root filesystem UUID and `kerynth.mode=installed`.
- Records the selected installation mode and explicitly records that no partition table or bootloader was modified.

Example invocation:

```sh
python3 tools/kerynth-install-tree \
  --target test-install \
  --mode manual \
  --root-uuid 12345678-1234-1234-1234-123456789abc \
  --username kerynth \
  --hostname kerynth-test \
  --password-hash '<sha-512-crypt-or-yescrypt-hash>'
```

This command stages files only; it does not consume the GPT plan above or install to a disk.

## Important limitations

The installer is not yet a finished interactive disk installer. The ISO's manual and automatic installer entries still display a no-write placeholder. No command in this development flow writes to a block device.

Still required before enabling real installation:

- Discover disks and show device model, size, transport, and current partition layout.
- Require the user to select a target and show an explicit destructive-operation summary.
- Add a separately reviewed disk execution layer that can only run on an explicitly selected target.
- Create and validate filesystems, mount the target, install the operating system and bootloader, and support recovery after interruption.
- Verify the complete installed boot flow against disposable QEMU virtual disks, including both UEFI and BIOS paths where supported.

A successful layout-plan test is not proof of a working installer. Real disk-writing must remain disabled until the virtual-disk tests validate the entire install and reboot sequence.


## Complete installation into a disposable disk image (UEFI test path)

The next installer execution layer is **tools/kerynth-install-system-image**. Unlike the layout planner and GPT-only image writer, it performs the filesystem installation sequence, but its target is still restricted to an existing regular .img or .raw file. It refuses block devices through the image validator and requires root only so Linux can attach a loop device, create filesystems, mount them, and run GRUB.

The tool writes and verifies the GPT plan, attaches the image with losetup --partscan, creates a FAT32 EFI System Partition and an ext4 root filesystem, stages the Kerynth root filesystem with the selected account and host configuration, copies the staged tree into the mounted root, installs the GRUB x86_64 UEFI removable-media loader, and records the resulting filesystem UUIDs and installation state. The EFI filesystem is also added to /etc/fstab.

The password hash is read from a separate file with permissions 0600 or stricter; it is not accepted as a command-line value. The hash file must contain a SHA-256, SHA-512, or yescrypt crypt hash.

Example for a disposable 4 GiB image after the rootfs, kernel, and initramfs have been built:

    truncate -s 4294967296 ./kerynth-test.img
    umask 077
    openssl passwd -6 > ./kerynth-password-hash
    sudo python3 tools/kerynth-install-system-image \
      --image ./kerynth-test.img \
      --disk-bytes 4294967296 \
      --sector-size 512 \
      --mode automatic \
      --workspace .kerynth-work \
      --password-hash-file ./kerynth-password-hash \
      --confirm-overwrite-image
    rm -f ./kerynth-password-hash

This is a developer and CI test path, not permission to point the tool at a physical disk. It deliberately accepts only regular image files. Do not convert physical devices to image paths or bypass its target checks.

The **tools/kerynth-qemu-installed-smoke** test creates a disposable image, runs the installation sequence, and boots it with OVMF in QEMU. It passes only when the installed kernel and initramfs mount the new root filesystem and /sbin/init reaches the KERYNTH BASE SYSTEM READY marker on the serial console. This validates one UEFI/QEMU path; it does not yet validate BIOS installation, real laptop hardware, graphical desktop startup, networking, or upgrades.
