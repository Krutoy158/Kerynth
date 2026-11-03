# Kerynth Architecture

## 1. Distribution model

Kerynth is assembled from upstream source projects using its own build definitions, package metadata, repository layout, installer, and release pipeline. It must not use another distribution's root filesystem, package database, or package manager as its foundation.

The build host is only a tool provider. All target files are installed into an isolated staging root owned by the KERYNTH build system.

## 2. Layers

```text
Hardware
  Linux kernel + firmware
  Early userspace / initramfs
  KERYNTH init and service profile
  Base userspace (musl, core utilities)
  KERYNTH package database and package manager
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

The kernel is upstream Linux with an KERYNTH-maintained configuration. Kernel configuration must favor broad hardware support while keeping the base image reasonable. Hardware-specific modules must not be silently omitted merely to reduce image size.

## 5. Boot and service management

The boot path consists of firmware, bootloader, kernel, initramfs, root filesystem, and PID 1.

The initial design supports two service profiles:

- systemd profile
- OpenRC profile

They are build/install profiles, not a promise that an arbitrary running system can switch init implementations by replacing one package. The installer must select a profile, and migration tooling must validate dependencies, preserve service configuration, and provide recovery.

## 6. Package system

The native package format is `.ker`. Package metadata must include at least:

- package name and version
- target architecture
- package format version
- dependencies and conflicts
- installed file manifest
- payload checksums
- signing key identity and signature

Installation must verify signatures before extraction, reject path traversal and unsafe archive entries, detect file conflicts, stage changes, and record ownership in a local package database.

The `.deb` compatibility layer is required alongside `.ker`. It inspects Debian `ar` containers, control metadata, and data archives without executing package scripts. It imports only packages whose dependencies, paths, permissions, and metadata can be represented safely. Unsupported dependencies, maintainer scripts, triggers, conffile behavior, links, special files, and filesystem assumptions must be reported clearly. The first implementation is inspection and conversion preview, followed by safe conversion into `.ker`. Direct installation of arbitrary `.deb` files is not an initial goal.

## 7. Hardware and firmware

Hardware support is based on upstream Linux drivers plus separately packaged firmware. KERYNTH tooling will collect hardware identifiers, match them to available kernel modules and firmware packages, and produce actionable diagnostics.

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

Kerynth contains no telemetry, analytics, tracking identifiers, or diagnostic upload mechanism. The operating system must not send usage, hardware inventory, crash, or application data to Kerynth or third parties. Troubleshooting logs remain local and under the user's control. Network access is limited to explicitly requested operations such as package downloads and system updates.

## 11. User authority and privilege model

The interactive user is the primary owner of the system experience, personal data, files, and preferences. The root account is an administrative role for maintaining the operating system; it is not the default working identity.

The system must follow these rules:

- Create and use an unprivileged user account for normal work. Do not require routine root login.
- Do not launch desktop applications, browsers, development tools, or package build jobs as root.
- Administrative actions must be explicit, narrowly scoped, and explain what will change before authorization.
- Use the standard sudo-style privilege model for explicit administrative operations. Kerynth must not silently elevate, launch a persistent root session, or require a separate privilege broker for the initial system.
- Never silently elevate a process, modify user files as root, or change user-owned settings without consent.
- Keep user data and configuration separate from system-owned files. Package installation must not overwrite user data without an explicit decision.
- Root access remains technically powerful, so security boundaries, audit logs, and recovery procedures must assume that privileged code can affect the whole system.

The intended model is user-first administration: root maintains the system, while the user controls their own session and approves changes that affect it.

## 10. Live environment and ISO

Every testable Kerynth ISO must offer a Live mode that boots without installing to or modifying internal disks. Live mode must provide a usable console first; a graphical session is optional until the desktop profile is ready. Runtime changes should use temporary storage. Internal disks must not be auto-mounted for writing, boot entries must not be modified, and the installer must not start automatically. The user must be able to inspect hardware, network availability, boot logs, and system information, then shut down without persistent changes.

The boot menu must distinguish **Live Kerynth** from **Install Kerynth**. CI must boot the ISO in QEMU, verify that Live mode reaches a usable state, and publish the ISO, SHA-256 checksum, and boot logs as workflow artifacts. No ISO should be presented as usable before these checks pass.

## 11. Desktop

A desktop is optional. KDE Plasma is a planned profile, not part of the minimal base system. The desktop profile will define its display manager, session, audio stack, network integration, portals, and hardware integration as a tested set.
