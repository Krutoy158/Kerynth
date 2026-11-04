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

The generated plan contains `writes_performed: false`. The tool does not discover block devices, create partition tables, format filesystems, mount targets, or install a bootloader.

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
