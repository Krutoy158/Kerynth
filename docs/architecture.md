# AETHER OS Architecture

## 1. Distribution model

AETHER OS is assembled from upstream source projects using its own build definitions, package metadata, repository layout, installer, and release pipeline. It must not use another distribution's root filesystem, package database, or package manager as its foundation.

The build host is only a tool provider. All target files are installed into an isolated staging root owned by the AETHER build system.

## 2. Layers

```text
Hardware
  Linux kernel + firmware
  Early userspace / initramfs
  AETHER init and service profile
  Base userspace (musl, core utilities)
  AETHER package database and package manager
  Optional services and hardware integration
  Optional desktop environment
  Installer, recovery tools, release image
```

## 3. Build pipeline

The build pipeline will have explicit, reproducible stages:

1. Fetch pinned upstream source archives.
2. Verify cryptographic checksums and signatures where upstream publishes them.
3. Build a cross-toolchain in an isolated directory.
4. Build target packages in dependency order.
5. Assemble a staging root without touching the host root.
6. Run filesystem, dependency, license, and security checks.
7. Build initramfs and kernel artifacts.
8. Boot the result in QEMU.
9. Produce signed repository metadata and release artifacts.

Build definitions must pin source versions. Floating branches are not acceptable inputs for reproducible release builds.

## 4. Target platform

The first target is x86_64. The initial libc choice is musl. Other architectures and libc profiles may be evaluated after the first reproducible boot.

The kernel is upstream Linux with an AETHER-maintained configuration. Kernel configuration must favor broad hardware support while keeping the base image reasonable. Hardware-specific modules must not be silently omitted merely to reduce image size.

## 5. Boot and service management

The boot path consists of firmware, bootloader, kernel, initramfs, root filesystem, and PID 1.

The initial design supports two service profiles:

- systemd profile
- OpenRC profile

They are build/install profiles, not a promise that an arbitrary running system can switch init implementations by replacing one package. The installer must select a profile, and migration tooling must validate dependencies, preserve service configuration, and provide recovery.

## 6. Package system

The native package format is `.aet`. Package metadata must include at least:

- package name and version
- target architecture
- package format version
- dependencies and conflicts
- installed file manifest
- payload checksums
- signing key identity and signature

Installation must verify signatures before extraction, reject path traversal and unsafe archive entries, detect file conflicts, stage changes, and record ownership in a local package database.

The `.deb` compatibility layer is a separate importer. It inspects Debian control metadata and archive contents, maps only supported metadata, and reports unsupported dependencies, scripts, triggers, and filesystem assumptions. Conversion must not execute maintainer scripts.

## 7. Hardware and firmware

Hardware support is based on upstream Linux drivers plus separately packaged firmware. AETHER tooling will collect hardware identifiers, match them to available kernel modules and firmware packages, and produce actionable diagnostics.

The system must distinguish:
- driver available and loaded
- driver available but not loaded
- firmware missing
- device unsupported by the selected kernel
- device not detected

Firmware redistribution must respect each firmware file's license and redistribution terms.

## 8. Installer safety

The installer must:
- show the selected target disk and partitions before writing
- require explicit confirmation before destructive operations
- preserve existing systems unless the user explicitly chooses otherwise
- back up bootloader configuration before any approved modification
- never silently replace another operating system's bootloader entry
- provide a recovery path and installation log

## 9. Privacy and diagnostics

No mandatory telemetry. Local logs are retained for troubleshooting and must be documented and configurable. Any optional network diagnostic upload must be opt-in, previewable, and scrubbed of sensitive information.

## 10. Desktop

A desktop is optional. KDE Plasma is a planned profile, not part of the minimal base system. The desktop profile will define its display manager, session, audio stack, network integration, portals, and hardware integration as a tested set.
