# Hardware and Firmware Support

**Status:** local PCI/USB inventory prototype exists; driver/firmware catalog, selection, and kernel integration are not implemented.

## Local hardware inventory\n\n`tools/kerynth-hw` reads PCI and USB device attributes from sysfs and reports IDs, modaliases, bound drivers, and kernel modules. It is read-only, supports a fixture sysfs root for tests, emits JSON with `--json`, and does not transmit inventory. It does not install drivers, load modules, identify every device class, or prove compatibility.\n\nThe installer must run discovery locally before choosing an install bundle. It should map device modaliases and IDs against the exact selected kernel's module metadata and a reviewed firmware catalog. It must distinguish a module being available from a driver actually being bound.\n\n## Support approach

Kerynth will use upstream Linux kernel drivers and separately managed firmware packages. Hardware support is determined by the exact device ID, kernel version/configuration, firmware availability, and licensing terms.

The project will not claim universal hardware compatibility.

## Initial device classes

| Device class | Planned support path |
|---|---|
| Intel and AMD graphics | Upstream kernel drivers and Mesa userspace |
| NVIDIA graphics | Nouveau where supported; proprietary driver option only where licensing and kernel compatibility allow |
| Wi-Fi | Upstream kernel drivers plus required firmware |
| Bluetooth | Kernel Bluetooth stack and userspace integration |
| Audio | ALSA kernel interfaces and optional PipeWire userspace |
| Storage | Kernel storage drivers, NVMe, SATA, USB storage |
| Input | Kernel input stack, touchpad and keyboard support |
| Printers | Optional CUPS profile |
| Laptop power | Kernel ACPI/platform drivers and userspace power management |

## Installer driver selection\n\n- Include a baseline of common storage, USB, and network drivers plus legally redistributable firmware in the installation image.\n- Detect hardware before installation and present a recommended driver/firmware set with a manual review option.\n- Keep kernel modules tied to the exact kernel release/ABI; never download an arbitrary module for a different kernel.\n- Keep firmware packages separate from kernel modules.\n- Support an offline path using firmware and modules already present on the ISO or supplied from user-selected removable media.\n- Do not promise network downloads until a working network interface is available.\n- Verify package signatures and checksums before staging driver components.\n- Do not send hardware inventory to a remote service.\n\n## Firmware policy

- Keep firmware separate from kernel modules.
- Track source, version, checksum, and redistribution terms for each firmware item.
- Do not redistribute firmware unless its license permits it.
- Provide a clear diagnostic when firmware is absent.
- Allow users to add legally obtained firmware through documented tooling.

## Diagnostic states

The future `kerynth-hw` tool should distinguish:

- device detected and driver loaded
- device detected and driver available but not loaded
- firmware required but missing
- no matching driver in the selected kernel
- device not detected by the kernel

Diagnostics should include hardware identifiers and suggested package names where known. They must not claim that installing a random driver will solve the issue.

## Validation

Maintain a public test matrix containing device model or chipset, kernel version, firmware package, test date, and result. Never list a device as tested based only on a vendor compatibility claim.
