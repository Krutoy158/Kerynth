# Build System

Kerynth builds into the project-local `.kerynth-work/` directory. The build pipeline does not invoke sudo, write to the host root, partition disks, or modify boot entries.

## Requirements

- x86_64 Linux build host
- Python 3.11 or newer
- GCC, GNU Make, binutils
- bc, bison, flex, OpenSSL development headers, Perl
- xz, bzip2, gzip
- squashfs-tools (`mksquashfs`)
- GRUB BIOS/EFI utilities and xorriso for ISO creation
- Network access for the pinned upstream source archives

The repository CI checks Python syntax, configuration, GRUB syntax, Qt Welcome compilation, and unit tests. It does not currently perform the full Linux/musl source build.

## Pinned sources

The version and SHA-256 of every build input are stored in `sources.lock`:

- Linux 6.6.161
- musl 1.2.6
- BusyBox 1.38.0

The fetcher accepts HTTPS sources only, enforces size limits, checks SHA-256, and uses temporary files followed by atomic replacement. The pipeline extracts each archive into a separate workspace directory after validating paths, entry types, symlink targets, duplicate paths, and total expanded size.

SHA-256 verifies that the downloaded bytes match the repository lock file. Upstream detached-signature verification and a reviewed publisher-key policy are still open work.

## Build commands

Validate the project configuration and source lock:

```sh
make check
```

Run the unit tests:

```sh
make test
```

Build the minimal musl + static BusyBox root filesystem:

```sh
make rootfs
```

Build the x86_64 Linux kernel and install its modules into that root filesystem:

```sh
make kernel
```

Generate the initramfs from the built BusyBox and Kerynth boot scripts:

```sh
make initramfs
```

Create the ISO staging tree and SquashFS image:

```sh
make iso-stage
```

Package the prepared staging tree as an ISO:

```sh
make iso
```

Run the full pipeline:

```sh
make build
```

The full pipeline runs rootfs, kernel, initramfs, SquashFS staging, validation, and ISO packaging in sequence. It may take a substantial amount of time and disk space.

## Workspace layout

The pipeline writes generated content only below `.kerynth-work/`:

- `.kerynth-work/sources/` — checksum-verified source archives
- `.kerynth-work/sources-unpacked/` — extracted source trees
- `.kerynth-work/rootfs/` — generated minimal userspace
- `.kerynth-work/build/` — musl, BusyBox, and kernel build directories
- `.kerynth-work/kernel/` — kernel image, config, System.map, and release
- `.kerynth-work/initramfs.cpio.gz` — boot initramfs
- `.kerynth-work/iso-root/` — ISO staging tree
- `.kerynth-work/kerynth-x86_64.iso` — packaged ISO

The pipeline refuses to replace unmarked rootfs and kernel build directories. Remove only generated paths inside `.kerynth-work/` when intentionally starting over.

## Development shell

For isolated debugging only, a root shell can be enabled in a disposable VM:

```sh
python3 tools/kerynth-build-pipeline rootfs --developer-shell
```

Do not use that option for a release image. The default root and Live accounts are locked; the Live session is intended to start as the unprivileged `kerynth` user.

## Current limitations

- A complete rootfs, kernel, and ISO have not yet been built and boot-tested in QEMU.
- The kernel config fragment is a starting profile, not a complete reviewed hardware-support matrix.
- Kernel modules are built, but the firmware catalogue, module dependency loading, and broad hardware coverage remain open.
- The Live boot path and SquashFS handoff are implemented but not yet proven on real QEMU or physical media.
- The installer is still a no-write placeholder; no partitioning, filesystem creation, account creation, or bootloader installation is implemented.
- KDE Plasma is not part of the base rootfs or ISO profile yet.
- The package manager currently performs signed package operations against disposable staging roots; it is not yet installed into the Kerynth target userspace.
- Reproducibility has not been demonstrated by two clean, byte-identical full builds.
