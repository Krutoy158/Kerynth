# Kerynth Welcome Guide

## Purpose

Kerynth Welcome is a small first-start guide for people who are new to Linux. It is inspired by the beginner-friendly first-steps flow in Linux Mint, but uses original Kerynth content and artwork. It is a local desktop application, not an installer screen and not a bootloader screen.

The guide starts automatically when the graphical desktop session becomes ready:
- in the Live System, after the Live desktop starts;
- in an installed Kerynth system, after the user's first graphical login and on later logins while startup display remains enabled.

It must never block login, console access, shutdown, or the desktop if the guide fails to start.

## First screen

Title: **Welcome to Kerynth**

The first screen contains a short greeting, a sentence explaining that every step is optional, and a clear **Let's get started** action. The user can also close the window immediately.

The navigation is a short list of beginner-friendly sections:

1. **Welcome** — what Kerynth is and where to find the guide again.
2. **Connect** — how to open Wi-Fi and wired network settings. No network connection is made without the user's action.
3. **Updates** — how to check for system and security updates. The guide may open the update tool, but it must not download or install anything automatically.
4. **Drivers & Hardware** — how to inspect detected hardware and check driver/firmware status. Hardware inventory stays local.
5. **Appearance** — how to change the desktop style, wallpaper, display scale, and accessibility options when those controls are installed.
6. **Apps** — how to find and install applications through the Kerynth software tool when it is available.
7. **Backups & Recovery** — explain backup and recovery options that are actually installed.
8. **Help** — open bundled offline documentation or, only after an explicit click, the online documentation.

Each section uses a simple explanation and one clear action. The action opens an existing system settings page or application. If the required component is not installed yet, the guide must show an honest **Not available yet** state instead of a dead button or a false claim that the feature works.

## Live and installed behavior

### Live System

The guide opens after the Live graphical session is ready. It explains prominently that this is a temporary session and that changes normally disappear after shutdown. It must not imply that settings, downloads, or files will be preserved.

Live startup preference is stored only below `$XDG_RUNTIME_DIR/kerynth/`. It is volatile and disappears when the Live session ends. The Live guide must explain this next to the startup checkbox: **Show this guide at startup**. Unchecking it hides the guide for the rest of the current Live session only. It must not write the preference to the USB device or internal disks. A future explicit persistent-Live feature may offer cross-reboot preference storage, but only when the user has deliberately enabled persistent storage.

The guide must include a clear explanation that internal disks are not changed by simply opening the guide. It must not mount internal disks read-write, launch the installer automatically, or perform installation actions by itself. Any installer launch must be initiated by an explicit user action and still follow installer confirmation safeguards.

### Installed system

The guide opens after the first graphical login and on later logins while **Show this guide at startup** is enabled. The checkbox is enabled by default.

When the user unchecks it and closes or completes the guide, the choice is saved persistently in the user's configuration at `$XDG_CONFIG_HOME/kerynth/welcome.json` (or `~/.config/kerynth/welcome.json` when XDG_CONFIG_HOME is not set). It applies only to that user account.

The application remains available from the application menu as **Kerynth Welcome**, so the user can reopen it at any time. A **Show at startup** preference in the guide's settings can re-enable automatic display.

## Preference state helper

`tools/kerynth-welcome-state` implements the small local preference store used by the future desktop launcher:

- `should-show --mode installed|live` prints `show` or `hidden`.
- `set --mode installed|live --hide` disables automatic display for that scope.
- `set --mode installed|live --show` re-enables automatic display.

The state file contains only a schema version and a boolean startup preference. It stores no account name, password, hardware inventory, usage data, or analytics identifiers. Writes use a temporary file, restrictive file permissions, and atomic replacement. Missing or invalid state defaults to showing the guide, so a damaged preference cannot permanently hide help from a new user.

Installed and Live preferences are deliberately stored in different locations. The helper does not require network access and contains no telemetry.

## Startup integration

The desktop package will install `desktop/autostart/kerynth-welcome.desktop`. It runs `kerynth-welcome-startup` after the graphical session is ready. The dispatcher reads `/run/kerynth/boot-mode`, accepts only `live` or `installed`, and calls the preference helper before it starts `kerynth-welcome --startup`. Unknown or missing boot-mode markers cause a quiet no-op. It must not run during early boot, on a text-only console, or before the user's desktop session exists.

The same package adds **Kerynth Welcome** to the desktop application menu. Launching it manually always opens the guide, even when automatic startup has been disabled.

The autostart integration must not create duplicate windows. If the user already has the guide open, a second startup request must focus the existing window.

## Privacy, security, and accessibility

- Entirely local operation. No telemetry, analytics, tracking identifiers, account creation, or diagnostic upload.
- No online checks are made merely to open the guide.
- Online documentation is opened only after an explicit user click.
- No passwords or other credentials are requested or stored.
- The guide never silently elevates privileges. Actions that change system configuration use the corresponding system tool and its normal authorization prompt.
- The guide does not run shell commands assembled from UI text.
- Keyboard navigation, visible focus, screen-reader labels, scalable text, high contrast, and sensible window sizing are required.
- The guide follows the user's language selected during installation or desktop setup. Missing translations fall back to English.
- Closing the guide must not close the desktop session or interrupt other startup applications.

## Acceptance tests

- First graphical login in an installed system shows the guide by default.
- Subsequent installed logins show it until the user disables startup display.
- An installed user's preference survives logout, reboot, and application updates.
- The guide can be reopened manually after startup display is disabled.
- Live mode shows the guide by default and stores its preference only in volatile runtime storage.
- A new Live boot shows the guide again unless a future, explicitly enabled persistence feature exists.
- The Live guide never writes preference state to the boot medium or internal disks.
- The guide does not open before the graphical session is ready and does not block login if it fails.
- Missing system tools are displayed as unavailable rather than exposed as broken actions.
- Tests prove the state file contains only the version and boolean preference, is private to its user, and is written atomically.
- Tests prove no credentials, hardware inventory, or telemetry are collected.

## Implementation status

The local startup-preference helper, boot-mode dispatcher, autostart desktop-entry template, and their unit tests are implemented. This document is the approved behavior specification. The graphical guide, its application-menu launcher, and integration with real settings applications are not yet implemented. They must not be marked complete until the desktop package exists and is tested in both Live and installed sessions.
