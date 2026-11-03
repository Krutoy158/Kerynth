# Development Roadmap

This roadmap distinguishes source code, prototypes, verified builds, and tested boot behavior. A source file or a passing unit test does not mark a bootable operating system complete.

## M0 — Foundation

- [x] Establish project identity and initial architecture.
- [x] Record driver and firmware strategy.
- [x] Record native package and Debian compatibility requirements.
- [x] Define a user-first privilege model based on explicit sudo authorization.
- [x] Pin initial Linux, musl, and BusyBox source archives with SHA-256 digests.
- [ ] Select and publish project code and documentation licenses.
- [ ] Add contribution and security reporting policies.
- [ ] Add upstream detached-signature verification and a trusted publisher-key policy.

## M1 — Isolated build infrastructure

- [x] Validate configuration and source-lock metadata.
- [x] Fetch pinned source archives over HTTPS and check SHA-256.
- [x] Extract source archives with path, link, entry-type, duplicate, and expansion-size checks.
- [x] Add isolated build orchestration for musl, static BusyBox, Linux, initramfs, SquashFS, and ISO packaging.
- [x] Add Makefile targets for each build stage.
- [ ] Run a complete source build on a supported build host.
- [ ] Build twice from clean workspaces and compare outputs.
- [ ] Add a sandbox for source build steps and a reviewed dependency graph.
- [ ] Publish reproducible build metadata.

**Current state:** the pipeline and pinned inputs are in the repository and its Python/unit-test checks run in CI. A complete musl/BusyBox/kernel/ISO build has not yet been performed successfully, so the minimal userspace build and reproducibility criteria are still open.

## M2 — Bootable core

- [x] Add deterministic `newc` CPIO + gzip initramfs generation.
- [x] Add boot-mode parsing and a volatile `/run/kerynth/boot-mode` marker.
- [x] Add root device, UUID, and LABEL discovery for installed-mode boot.
- [x] Add ISO media UUID handoff from GRUB.
- [x] Add read-only ISO media and SquashFS mount logic for Live and installer modes.
- [x] Add a console session dispatcher and an unprivileged Live account to the rootfs generator.
- [ ] Build the configured Linux kernel from the pinned source.
- [ ] Generate and verify the boot initramfs from actual built artifacts.
- [ ] Boot in QEMU to a usable console login.
- [ ] Verify Live mode does not write to internal disks or installed boot entries.
- [ ] Verify clean shutdown/reboot and publish QEMU logs.

**Current state:** the boot scripts, GRUB handoff, and rootfs session definitions are implemented and covered by static/unit tests. The kernel and rootfs have not yet been built together or boot-tested; the Live path remains unverified end-to-end.

## M3 — Hardware enablement

- [x] Add read-only PCI/USB hardware inventory prototype (`tools/kerynth-hw`).
- [x] Add initial built-in kernel configuration for virtio, SATA/AHCI, USB storage, optical media, ISO9660, SquashFS, and serial console.
- [ ] Complete the kernel configuration for common storage, input, graphics, network, and audio devices.
- [ ] Match hardware modaliases against modules built for the exact kernel release.
- [ ] Build a reviewed firmware catalogue with redistribution-license metadata.
- [ ] Include baseline storage/network drivers and an offline driver path in the ISO.
- [ ] Add hardware compatibility tests for QEMU and selected physical systems.

## M4 — Native package management

- [x] Specify experimental `.ker` format version 1.
- [x] Implement canonical manifest parsing and Ed25519 package verification.
- [x] Implement signed package creation with SHA-256 payload binding.
- [x] Implement safe payload path and file-type validation.
- [x] Implement package install/remove/list against disposable staging roots only.
- [x] Record package ownership and installed file hashes.
- [x] Add exact-version dependency checks, conflict checks, and protection against removing modified files or required dependencies.
- [ ] Add upgrade/downgrade transactions and repository metadata.
- [ ] Add key rotation/revocation and signed repository indexes.
- [ ] Integrate the package manager into the Kerynth userspace with explicit sudo authorization.
- [ ] Add adversarial archive tests beyond the initial unit-test suite.

**Current state:** package operations are a tested development prototype restricted to `.kerynth-work/targets/`. They cannot install into the host system or a live Kerynth installation. The Python tool is not yet part of the minimal OS image.

## M5 — Debian compatibility

- [ ] Inspect `.deb` ar containers and control/data archives without extracting to the host.
- [ ] Parse Debian control metadata.
- [ ] Map supported dependency expressions.
- [ ] Report unsupported maintainer scripts, triggers, dependencies, and paths.
- [ ] Implement a non-executing conversion preview and explicit conversion command.
- [ ] Keep direct installation of arbitrary `.deb` files disabled until compatibility and safety are proven.

## M6 — Service profiles

- [ ] Define systemd profile.
- [ ] Define OpenRC profile.
- [ ] Add service enable/disable tooling.
- [ ] Add profile-specific CI boot tests.
- [ ] Design controlled migration and recovery.

## M7 — Installer and accessibility

- [x] Specify beginner-friendly Quick Profile Setup for the first local user account.
- [ ] Implement local profile validation, password hashing, and safe account creation.
- [x] Add a staging-only install-tree builder with first-user, fstab, and installed GRUB configuration generation.\n- [ ] Implement the manual installer workflow.
- [ ] Implement the automatic installer workflow with explicit disk confirmation.
- [ ] Add a graphical installer.
- [ ] Add a hardware compatibility summary.
- [ ] Add partitioning, filesystem, bootloader backup, and recovery with VM safety tests.
- [ ] Add accessibility options and keyboard navigation.

**Current state:** a tested staging helper prepares an installed root tree only below `.kerynth-work/targets/`. It does not partition, format, mount, or modify block devices, and it does not install a bootloader. The ISO menu still dispatches to a no-write placeholder; a real interactive installer remains open.

## M8 — Optional desktop

- [x] Specify the Kerynth Welcome first-run guide for Live and installed sessions.
- [x] Implement the local per-user startup preference helper and session dispatcher.
- [x] Add the Qt 6 graphical Welcome prototype and application launcher.
- [ ] Add graphical-session autostart and integrate it in the desktop profile.
- [ ] Build and package KDE Plasma and its runtime dependencies.
- [ ] Add display manager, session, network, audio, Bluetooth, portals, and power management.
- [ ] Add the Kerynth Glass theme and branded wallpaper/logo assets.
- [ ] Test with software rendering and supported GPU drivers.

## M9 — ISO and releases

- [x] Add a workspace-only ISO staging validator and GRUB ISO packager.
- [x] Add the KER-only boot menu with Manual Installation, Automatic Installation, and Live System.
- [x] Add no-timeout menu behavior and distinct boot modes.
- [x] Add the initial media UUID and read-only SquashFS handoff code.
- [ ] Build the ISO from the generated kernel and rootfs.
- [ ] Verify BIOS and UEFI boot in QEMU.
- [ ] Verify Live boot, shutdown, and installer no-write behavior.
- [ ] Publish a tested ISO, SHA-256 checksum, and boot logs.
- [ ] Add signed release checksums and release workflow.

## Release gate

Kerynth is not ready to be called a usable distribution until a generated ISO boots in QEMU, reaches a working Live console/session, preserves internal disks in Live mode, and its manual installation path passes destructive-operation safety tests in disposable virtual machines.
