# Contributing to Kerynth OS

Kerynth OS is an early-stage independent Linux distribution. Contributions should be small, testable, and documented.

## Engineering rules

- Do not build or install target files into the host root filesystem.
- Use an isolated build directory and disposable virtual machines.
- Pin upstream source versions and verify downloaded sources.
- Do not add unreviewed binary blobs.
- Preserve upstream license notices.
- Do not run untrusted package scripts as root.
- Validate archive paths and symlinks before extraction.
- Do not modify bootloader configuration without explicit user consent, a backup, and a recovery plan.
- Do not describe a feature as working until a reproducible test demonstrates it.

## Code quality

- Prefer clear interfaces and explicit error handling.
- Keep privileged operations small and auditable.
- Avoid shell command construction from untrusted input.
- Add tests for malformed input and failure paths, not only successful cases.
- Keep comments useful and avoid duplicating what the code already says.

## Changes

A change should include:
1. the problem it solves
2. the design choice
3. tests performed
4. known limitations

Large features should begin with a design document and be split into reviewable implementation steps.
