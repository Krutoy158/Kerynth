# Hardware and Firmware Support

**Status:** requirements and test policy; hardware detection tools are not implemented.

## Support approach

Kerynth OS will use upstream Linux kernel drivers and separately managed firmware packages. Hardware support is determined by the exact device ID, kernel version/configuration, firmware availability, and licensing terms.

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

## Firmware policy

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
