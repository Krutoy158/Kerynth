# Development Roadmap

This roadmap separates design work from implemented and tested functionality. A milestone is not complete until its acceptance criteria are met.

## M0 — Foundation

- [x] Establish project identity and initial architecture.
- [x] Record driver and firmware strategy.
- [x] Record native package and Debian compatibility requirements.
- [ ] Select and publish project code and documentation licenses.
- [ ] Add contribution and security reporting policies.
- [ ] Define supported source pinning and reproducible build metadata.

**Exit criteria:** repository policy and architecture are reviewed and stable enough to implement.

## M1 — Isolated build infrastructure

- [x] Initial build configuration and workspace validation.
- [x] Source lock parser and HTTPS fetcher with SHA-256 verification.
- [ ] Signature verification and trusted source key policy.
- [ ] Pinned build recipes and dependency graph.
- [ ] Cross-toolchain bootstrap for x86_64.
- [ ] Staging-root assembly and reproducibility report.
- [ ] CI tests that never write to the runner's host root.

**Current progress:** configuration validation and checksum-verified source caching are implemented. Compilation, signature verification, and reproducible staging builds remain open.

**Exit criteria:** a minimal userspace can be built twice from pinned sources into isolated staging roots.

## M2 — Bootable core

- [ ] Build upstream Linux kernel from pinned source.
- [ ] Generate initramfs.
- [ ] Implement and test PID 1 behavior.
- [ ] Provide console login and clean shutdown/reboot.
- [ ] Boot in QEMU using a virtual disk.
- [ ] Publish boot logs and test configuration.

**Exit criteria:** QEMU reaches a usable console login and shuts down cleanly.

## M3 — Hardware enablement

- [ ] Kernel configuration for common storage, USB, input, graphics, network, and audio devices.
- [ ] Firmware package inventory and license review.
- [ ] Hardware identifier collection.
- [ ] Driver and firmware diagnostic command.
- [ ] Test matrix for selected physical devices and QEMU devices.

**Exit criteria:** tested devices are documented; missing firmware and unsupported hardware are clearly reported.

## M4 — Native package management

- [ ] Specify and version the .aet archive format.
- [ ] Implement metadata parser and package verifier.
- [ ] Implement repository metadata and signature verification.
- [ ] Implement safe extraction and path validation.
- [ ] Implement dependency/conflict solver.
- [ ] Implement staged installation, rollback, and package database.
- [ ] Add adversarial archive tests.

**Exit criteria:** signed packages can be installed and removed safely in a disposable test root.

## M5 — Debian compatibility

- [ ] Inspect .deb ar containers and control/data archives.
- [ ] Parse Debian control metadata.
- [ ] Map supported dependency expressions.
- [ ] Report unsupported maintainer scripts, triggers, dependencies, and paths.
- [ ] Implement non-executing conversion preview.
- [ ] Add explicit conversion command and tests.

**Exit criteria:** compatible test packages convert reproducibly; incompatible packages fail safely with a useful report.

## M6 — Service profiles

- [ ] Define systemd profile.
- [ ] Define OpenRC profile.
- [ ] Add service enable/disable tooling.
- [ ] Add profile-specific CI boot tests.
- [ ] Design controlled migration and recovery.

**Exit criteria:** each profile independently boots and starts required services in QEMU.

## M7 — Installer and accessibility

- [ ] Manual installation documentation and tooling.
- [ ] Graphical installer.
- [ ] Hardware compatibility summary.
- [ ] Explicit disk/partition confirmation.
- [ ] GRUB install/update opt-in with backup and recovery.
- [ ] High contrast, scalable text, keyboard navigation, and visual status messages.
- [ ] Accessibility manual setup.

**Exit criteria:** installation and recovery paths pass destructive-operation safety tests in virtual machines.

## M8 — Optional desktop

- [ ] KDE Plasma profile.
- [ ] Display manager and session integration.
- [ ] Network, audio, Bluetooth, portals, and power management.
- [ ] Optional Glass theme.
- [ ] Test with software rendering and supported GPU drivers.

**Exit criteria:** optional desktop starts from a clean installation without being required by the base system.

## M9 — ISO and releases

- [ ] Reproducible ISO generation.
- [ ] English boot menu with graphical, manual, and accessibility paths.
- [ ] QEMU boot and installer CI.
- [ ] Signed checksums and release artifacts.
- [ ] GitHub Actions release workflow.

**Exit criteria:** a published ISO boots and installs in QEMU, with checksums and test logs attached.
