# Installer development

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

Supported modes are `manual` and `automatic`. Both currently prepare the same staged layout and record the selected mode. The target directory must not already exist. The tool refuses paths outside the project-local workspace and never opens block devices.

## Important limitations

This is an install-tree preparation tool, not the finished interactive installer. It does not create partitions or filesystems, mount devices, install GRUB to a disk, or write to a physical drive. The ISO's manual and automatic installer entries still display a no-write placeholder. A real installer needs an interactive layout editor, explicit target confirmation, partition/filesystem handling, bootloader recovery, and QEMU tests against disposable virtual disks before it can be enabled.
