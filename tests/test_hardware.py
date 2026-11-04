import importlib.util
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "kerynth-hw"
SPEC = importlib.util.spec_from_loader(
    "kerynth_hw",
    SourceFileLoader("kerynth_hw", str(TOOL_PATH)),
)
HARDWARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HARDWARE)


class HardwareInventoryTests(unittest.TestCase):
    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")

    def make_pci_device(self, root, modalias="pci:v00008086d00001234sv00000000sd00000000bc03sc00i00"):
        device = root / "bus/pci/devices/0000:00:02.0"
        self.write(device / "vendor", "0x8086")
        self.write(device / "device", "0x1234")
        self.write(device / "class", "0x030000")
        self.write(device / "modalias", modalias)
        return device

    def make_module_database(self, root, release="test-release", present=True):
        modules = root / "lib/modules" / release
        relative = "kernel/drivers/gpu/fake-gpu.ko"
        self.write(modules / "modules.alias", "alias pci:v00008086d00001234* fake_gpu\n")
        self.write(modules / "modules.dep", relative + ":\n")
        if present:
            self.write(modules / relative, "module placeholder")
        return modules

    def test_reads_pci_and_usb_ids_without_host_access(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pci = self.make_pci_device(root)
            usb = root / "bus/usb/devices/1-1"
            self.write(usb / "idVendor", "abcd")
            self.write(usb / "idProduct", "0001")
            self.write(usb / "bDeviceClass", "00")
            result = HARDWARE.scan(root, kernel_release="test-release", modinfo_binary="")
            self.assertEqual(len(result["devices"]), 2)
            self.assertEqual(result["devices"][0]["bus"], "pci")
            self.assertEqual(result["devices"][0]["vendor_id"], "8086")
            self.assertEqual(result["devices"][1]["bus"], "usb")
            self.assertFalse(result["telemetry"])
            self.assertEqual(result["schema_version"], 2)

    def test_ignores_invalid_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pci = root / "bus/pci/devices/0000:00:01.0"
            self.write(pci / "vendor", "not-an-id")
            self.write(pci / "device", "1234")
            self.assertEqual(HARDWARE.scan(root)["devices"], [])

    def test_matches_modalias_to_existing_module_for_kernel_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_pci_device(root)
            modules = self.make_module_database(root)
            result = HARDWARE.scan(
                root,
                modules_root=root / "lib/modules",
                kernel_release="test-release",
                firmware_root=root / "firmware",
                modinfo_binary="",
            )
            device = result["devices"][0]
            self.assertEqual(result["module_database_status"], "available")
            self.assertEqual(device["kernel_module_status"], "available")
            self.assertEqual(device["driver_candidates"][0]["module"], "fake_gpu")
            self.assertEqual(
                device["driver_candidates"][0]["path"],
                "kernel/drivers/gpu/fake-gpu.ko",
            )
            self.assertEqual(device["firmware_status"], "not_checked")

    def test_rejects_matching_alias_when_module_file_is_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_pci_device(root)
            self.make_module_database(root, present=False)
            result = HARDWARE.scan(
                root,
                modules_root=root / "lib/modules",
                kernel_release="test-release",
                firmware_root=root / "firmware",
                modinfo_binary="",
            )
            self.assertEqual(result["devices"][0]["kernel_module_status"], "no_match")
            self.assertEqual(result["devices"][0]["driver_candidates"], [])

    def test_reports_missing_module_database_as_not_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_pci_device(root)
            result = HARDWARE.scan(
                root,
                modules_root=root / "missing-modules",
                kernel_release="test-release",
                firmware_root=root / "firmware",
                modinfo_binary="",
            )
            self.assertEqual(result["module_database_status"], "not_found")
            self.assertEqual(result["devices"][0]["kernel_module_status"], "not_checked")

    def test_firmware_report_checks_only_paths_inside_firmware_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            firmware = root / "firmware"
            self.write(firmware / "vendor/gpu.bin", "firmware")
            module = root / "fake.ko"
            self.write(module, "module")
            completed = SimpleNamespace(returncode=0, stdout="vendor/gpu.bin\n", stderr="")
            with patch.object(HARDWARE.subprocess, "run", return_value=completed):
                result = HARDWARE.query_module_firmware(module, firmware, "/usr/sbin/modinfo")
            self.assertEqual(result["status"], "available")
            self.assertEqual(result["required"], ["vendor/gpu.bin"])

            completed.stdout = "../outside.bin\n"
            with patch.object(HARDWARE.subprocess, "run", return_value=completed):
                result = HARDWARE.query_module_firmware(module, firmware, "/usr/sbin/modinfo")
            self.assertEqual(result["status"], "missing")
            self.assertEqual(result["missing"], ["../outside.bin"])

    def test_firmware_is_not_claimed_checked_without_modinfo(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = HARDWARE.query_module_firmware(root / "fake.ko", root / "firmware", "")
            self.assertEqual(result, {"status": "not_checked", "required": []})


if __name__ == "__main__":
    unittest.main()
