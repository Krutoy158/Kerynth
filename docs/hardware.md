# Hardware and Firmware Support

**Current status:** local PCI/USB inventory and exact-kernel module matching are implemented in `tools/kerynth-hw`. Driver installation, firmware downloads, and package integration are not implemented.

## Local inventory

Run:

```sh
python3 tools/kerynth-hw --json
```

The scanner reads PCI and USB identity/modalias data from sysfs. It does not upload hardware inventory or use telemetry.

## Kernel module matching

The scanner reads the selected kernel release's `modules.alias` and `modules.dep` below `/lib/modules/<release>/`. It matches each device modalias against kernel alias patterns and reports only modules whose module file is present in the module dependency index and on disk.

Example with an alternate root or kernel build:

```sh
python3 tools/kerynth-hw \
  --sys-root /sys \
  --modules-root /lib/modules \
  --kernel-release "$(uname -r)" \
  --firmware-root /lib/firmware \
  --json
```

The report distinguishes a missing module database, a device without modalias data, no matching module, and a matching module file. A matching module is not necessarily loaded or bound to the device; those facts are reported separately from the sysfs driver link.

## Firmware inspection

When `modinfo` is available, the scanner asks it for the firmware files declared by each candidate module. Paths are checked below the selected firmware root; paths escaping that root are treated as missing. Without `modinfo`, the report says `not_checked`, not "firmware available".

Firmware files are not downloaded, installed, or copied by this tool. Firmware redistribution must respect the upstream license for each file.

## Initial device classes

| Device class | Support path |
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

## Remaining work

- Build and sign driver/firmware packages for the exact Kerynth kernel ABI.
- Review firmware source, version, checksum, redistribution rights, and dependency metadata.
- Add offline selection and installation from the ISO or user-provided media.
- Add online retrieval only after a network interface is operational and the user explicitly requests it.
- Keep a public device test matrix with chipset, kernel version, firmware package, test date, and validation result.

A module alias match alone is not proof that the hardware works. Hardware support will only be marked as tested after boot/runtime validation on the actual device or a representative QEMU/device test.
