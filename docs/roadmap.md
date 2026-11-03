# Development Roadmap

This roadmap separates design work from implemented and tested functionality. A milestone is not complete until its acceptance criteria are met.

## M0 — Foundation

- [x] Establish project identity and initial architecture.
- [x] Record driver and firmware strategy.
- [x] Record native package and Debian compatibility requirements.
- [ ] Select and publish project code and documentation licenses.
- [x] Define a user-first privilege model based on explicit sudo authorization.
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

- [ ] Build upstream Linux kernel from pinned source using the reviewed x86_64 configuration fragment.
- [x] Add deterministic `newc` CPIO + gzip initramfs archive builder and initial PID 1 handoff stub.
- [x] Add initial root device, UUID, and LABEL discovery plus switch-root handoff script (QEMU validation still required).
- [x] Validate the selected installer/Live boot mode and expose it through a volatile `/run/kerynth/boot-mode` marker.
- [ ] Generate initramfs from the selected kernel modules and firmware set.
- [ ] Complete PID 1 behavior and test it under QEMU.
- [ ] Provide console login and clean shutdown/reboot.
- [ ] Boot in QEMU using a virtual disk.
- [ ] Add a non-installing Live boot mode with temporary runtime storage.
- [ ] Verify Live mode does not write to internal disks or alter boot entries.
- [ ] Publish boot logs and test configuration.

**Exit criteria:** QEMU reaches a usable console login and shuts down cleanly.

## M3 — Hardware enablement

- [ ] Kernel configuration for common storage, USB, input, graphics, network, and audio devices.
- [ ] Test PCI/USB discovery against fixture sysfs trees and representative QEMU devices.
- [ ] Firmware package inventory and license review.
- [x] Add read-only PCI/USB hardware inventory prototype (`tools/kerynth-hw`).
- [ ] Match modaliases against modules built for the exact kernel release.
- [ ] Build a reviewed firmware catalog with redistribution-license metadata.
- [ ] Include baseline storage/network drivers and an offline driver path in the ISO.
- [ ] Hardware-aware installer driver-bundle preview and user confirmation.
- [ ] Driver and firmware diagnostic command.
- [ ] Test matrix for selected physical devices and QEMU devices.

**Exit criteria:** tested devices are documented; missing firmware and unsupported hardware are clearly reported.

## M4 — Native package management

- [ ] Specify and version the .ker archive format.
- [ ] Define the sudo-based install boundary: verify and plan as the user; apply only the validated system-file changes with explicit administrative authorization.
- [ ] Define package ownership, conflict handling, rollback, and strict separation from user home directories.
- [ ] Implement metadata parser and package verifier.
- [ ] Implement repository metadata and signature verification.
- [ ] Implement safe extraction and path validation.
- [ ] Implement dependency/conflict solver.
- [ ] Implement staged installation, rollback, and package database.
- [ ] Add adversarial archive tests.

**Exit criteria:** signed packages can be installed and removed safely in a disposable test root.

## M5 — Debian compatibility

- [ ] Inspect .deb ar containers and control/data archives without extracting to the host.
- [ ] Parse Debian control metadata.
- [ ] Map supported dependency expressions.
- [ ] Report unsupported maintainer scripts, triggers, dependencies, and paths.
- [ ] Implement non-executing conversion preview.
- [ ] Add explicit conversion command and tests.
- [ ] Keep direct installation of arbitrary `.deb` files disabled until compatibility and safety are proven.

**Exit criteria:** compatible test packages convert reproducibly; incompatible packages fail safely with a useful report.

## M6 — Service profiles

- [ ] Define systemd profile.
- [ ] Define OpenRC profile.
- [ ] Add service enable/disable tooling.
- [ ] Add profile-specific CI boot tests.
- [ ] Design controlled migration and recovery.

**Exit criteria:** each profile independently boots and starts required services in QEMU.

## M7 — Installer and accessibility

- [x] Specify beginner-friendly Quick Profile Setup for the first local user account.
- [ ] Implement local profile validation, username suggestion, and safe account creation.
- [ ] Manual installation documentation and tooling.
- [ ] Graphical installer.
- [ ] Hardware compatibility summary.
- [ ] Explicit disk/partition confirmation.
- [ ] GRUB install/update opt-in with backup and recovery.
- [ ] High contrast, scalable text, keyboard navigation, and visual status messages.
- [ ] Accessibility manual setup.

**Exit criteria:** installation and recovery paths pass destructive-operation safety tests in virtual machines.

## M8 — Optional desktop

- [x] Specify the Kerynth Welcome first-run guide for Live and installed sessions.
- [x] Implement a local per-user startup preference helper with separate persistent and volatile scopes.
- [ ] Build the graphical Kerynth Welcome application and its first-step pages.
- [ ] Add graphical-session autostart and an application-menu launcher.
- [ ] Integrate the guide with available settings, update, driver, app, backup, and help tools.
- [ ] KDE Plasma profile.
- [ ] Display manager and session integration.
- [ ] Network, audio, Bluetooth, portals, and power management.
- [ ] Optional Glass theme.
- [ ] Test with software rendering and supported GPU drivers.

**Exit criteria:** optional desktop starts from a clean installation without being required by the base system.

## M9 — ISO and releases

- [x] Add a workspace-only ISO staging validator and `grub-mkrescue` packaging prototype (bootability still unverified).
- [ ] Reproducible ISO generation from the tested staging root.
- [x] Specify the English boot menu: KER logo, **Manual Installation**, **Automatic Installation**, and **Live System**.
- [x] Add a minimal GRUB menu prototype with distinct installer/live kernel modes and no automatic timeout (GRUB/ISO integration and QEMU validation remain open).
- [ ] Live mode with no automatic internal-disk writes or installation.
- [ ] QEMU tests for Live boot, shutdown, and installer safety.
- [ ] Publish the ISO, SHA-256 checksum, and boot logs as GitHub Actions artifacts.
- [ ] Signed release checksums and release workflow.

**Exit criteria:** the ISO boots in QEMU, Live mode reaches a usable session without installing, and the installer requires explicit user action.
