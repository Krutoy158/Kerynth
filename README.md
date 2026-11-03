# AETHER OS

AETHER OS is an independent Linux distribution project. The system is intended to be built from upstream source projects with its own build definitions, package format, installer, and release process. It does not use another distribution's root filesystem or package database.

The project is at an early stage. The repository contains the initial design and the first build-system tools; there is no bootable image yet.

## Current state

| Part | State |
|---|---|
| Architecture and development notes | Initial draft |
| Build configuration and source fetcher | First implementation |
| Kernel, initramfs and boot | Not implemented |
| Hardware and firmware tooling | Not implemented |
| Native `.aet` packages | Design draft |
| Debian `.deb` import | Design draft |
| Installer and desktop profiles | Planned |
| ISO image | Not available |

## Technical direction

- x86_64 first; upstream Linux kernel.
- musl is the current choice for the initial minimal userspace.
- No desktop is installed by default. KDE Plasma is one planned optional profile.
- systemd and OpenRC are being considered as separate installation profiles.
- The native package format is planned as `.aet`.
- Debian `.deb` files will be inspected and imported only when their dependencies and behavior can be represented safely. Conversion will not run maintainer scripts.
- Hardware support will use upstream kernel drivers and separately tracked firmware. Unsupported devices and missing firmware must be reported clearly.

The current build tool verifies source archives against SHA-256 digests before placing them in the local cache. The source lock file is intentionally empty until exact upstream versions and checksums have been reviewed.

## Development

See [the architecture](docs/architecture.md), [the roadmap](docs/roadmap.md), and [the build setup](docs/build-system.md).

Run the build tool checks with Python 3.11 or newer:

```sh
python3 tools/aether-build check
python3 -m unittest discover -s tests -v
```

Downloaded files and build output are kept in the configured workspace. The tool does not install packages or modify the host system.

## Hardware notes

Hardware support depends on the exact device, kernel configuration, firmware availability, and licensing. AETHER OS cannot promise support for every device. The project will publish tested hardware and known limitations as testing becomes available.

## Safety

- Build in a dedicated workspace, not in the host root filesystem.
- Verify source checksums before using downloaded archives.
- Test boot and installation in QEMU before physical hardware.
- Never overwrite an existing bootloader configuration without explicit consent and a recoverable backup.
- Preserve the licenses and notices of upstream components.

## License

Licensing for project-owned code and documentation is being finalized. Upstream components retain their original licenses.
