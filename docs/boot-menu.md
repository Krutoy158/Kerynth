# Kerynth Boot Menu

## User-facing menu

The first Kerynth ISO boot screen uses the Kerynth wordmark/logo and exactly three primary choices. All visible interface text is English.

1. **Manual Installation**
2. **Automatic Installation**
3. **Live System**

The menu must be keyboard-accessible. Arrow keys move the selection, Enter activates it, and the selected item must be visibly distinguishable. A timeout must never start an installation.

## Menu behavior

### Manual Installation

Starts the installer in manual partitioning mode. The user chooses the target disk, partition layout, filesystems, mount points, bootloader target, and service profile. No disk changes occur until the installer presents a complete operation summary and the user explicitly confirms it.

### Automatic Installation

Starts the guided automatic partitioning flow. It must show the exact target disk and proposed partition layout before any destructive operation. The user must explicitly confirm the target disk and formatting action. There is no unattended or timeout-based installation.

### Live System

Boots the Kerynth live environment without starting the installer. Internal disks must not be mounted read-write automatically. The live environment must not format disks, write boot entries, or make persistent changes to internal storage. Temporary runtime changes use memory-backed storage where practical.

## Visual direction

- A distinctive Kerynth ASCII/art logo inspired by the visual presentation of Fastfetch: a recognizable custom emblem on the left, with the KERYNTH name and a compact system identity block beside it. It must be original Kerynth artwork, not a copied Fastfetch or another distribution logo.
- The identity block may show static release/build identity and detected machine details only when available locally; it must not delay boot, require network access, or transmit hardware information.
- Place the three menu choices clearly below or beside the branding, depending on the boot environment's resolution.
- Clean, restrained layout with clear spacing and readable typography.
- Glass styling may be used when the graphical boot environment supports it, but readability and accessibility take priority.
- No telemetry, network requirement, account prompt, or automatic installation step at the boot menu.

## Implementation status

This document records the approved menu design. It is not a claim that the boot menu, installer, or Live environment has been implemented. The menu becomes release-ready only after the ISO build and QEMU safety tests pass.
