# AETHER OS

**AETHER OS** is an independent Linux distribution built from upstream source code. It is not based on Arch Linux, Debian, Ubuntu, Fedora, Gentoo, or another Linux distribution.

The project is in its early foundation stage. The repository currently defines the architecture and development direction; it is not yet a bootable operating system.

## Project goals

- Build a minimal x86_64 Linux system from upstream sources in an isolated build environment.
- Keep the base installation small and avoid installing a graphical desktop by default.
- Let users choose a desktop environment, service manager, and system components.
- Provide a native package format, `.aet`, with signed metadata and transactional installation.
- Provide a carefully constrained Debian package compatibility layer for `.deb` packages.
- Detect hardware and report missing drivers or firmware clearly.
- Support common graphics, network, audio, Bluetooth, storage, USB, and laptop devices through the Linux kernel and documented firmware packages.
- Offer graphical and manual installation paths, including accessibility-focused options.
- Avoid mandatory telemetry and make local system logging transparent and configurable.

## Important compatibility policy

A Debian package is not automatically compatible with AETHER OS. Packages may depend on Debian-specific paths, libraries, maintainer scripts, service managers, or package assumptions. AETHER's `.deb` support will inspect metadata and dependencies, report incompatibilities, and never execute untrusted maintainer scripts as root during conversion.

The planned command-line interface is:

```sh
sudo aether install package.aet
aether deb inspect package.deb
sudo aether reverse -C package.deb
```

An optional `reverse` wrapper may be provided if it does not conflict with an existing system command.

## Hardware support

AETHER OS uses the upstream Linux kernel driver ecosystem and a separately managed firmware collection. Hardware support depends on the exact device, kernel configuration, firmware availability, and licensing. The installer and diagnostic tools must identify missing firmware and unsupported devices instead of silently claiming support.

No distribution can promise that every device works. AETHER will publish tested hardware and known limitations.

## Initial technical direction

- Architecture: x86_64 first.
- Kernel: upstream Linux.
- C library: musl for the initial minimal system.
- Bootstrap: temporary upstream build tools and BusyBox where useful; not a permanent dependency on another distribution's root filesystem or package database.
- Filesystem: ext4 initially; Btrfs can be evaluated later.
- Bootloader: GRUB, installed or modified only after explicit user consent.
- Init/service profiles: systemd and OpenRC are planned as separate build profiles. Switching a live installation between them will require a controlled migration.
- Desktop: optional; KDE Plasma is a planned supported desktop profile.

These are initial engineering decisions and may change through documented design proposals.

## Development status

| Component | Status |
|---|---|
| Project architecture | Initial draft |
| Isolated build system | Not implemented |
| Kernel build and boot | Not implemented |
| Hardware detection and firmware tooling | Not implemented |
| Native `.aet` package manager | Not implemented |
| Debian package compatibility | Not implemented |
| systemd/OpenRC profiles | Not implemented |
| Installer | Not implemented |
| Desktop integration | Not implemented |
| Bootable ISO | Not implemented |

## Safety and development rules

1. Build artifacts in a dedicated workspace; never modify the developer's host system.
2. Test boot and installation flows in QEMU before testing physical hardware.
3. Never run package maintainer scripts as root during `.deb` inspection or conversion.
4. Verify package signatures and checksums before installation.
5. Reject archive paths that escape the installation root, including absolute paths and traversal components.
6. Stage package transactions and provide rollback on failure.
7. Never overwrite an existing bootloader configuration without explicit consent and a recoverable backup.
8. Keep third-party licenses and notices intact.
9. Do not claim a feature works until it has a reproducible test.

## Contributing

Design decisions, implementation notes, test results, and known limitations should be documented in the repository. Small, reviewable changes are preferred over large untested changes.

## License

Licensing for project-owned code and documentation will be finalized in dedicated license files. Upstream components retain their original licenses; AETHER OS does not relicense the Linux kernel or bundled third-party software.
