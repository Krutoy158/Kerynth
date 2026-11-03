import importlib.util
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

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

    def test_reads_pci_and_usb_ids_without_host_access(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pci = root / "bus/pci/devices/0000:00:02.0"
            self.write(pci / "vendor", "0x8086")
            self.write(pci / "device", "0x1234")
            self.write(pci / "class", "0x030000")
            self.write(pci / "modalias", "pci:v00008086d00001234")
            usb = root / "bus/usb/devices/1-1"
            self.write(usb / "idVendor", "abcd")
            self.write(usb / "idProduct", "0001")
            self.write(usb / "bDeviceClass", "00")
            result = HARDWARE.scan(root)
            self.assertEqual(len(result["devices"]), 2)
            self.assertEqual(result["devices"][0]["bus"], "pci")
            self.assertEqual(result["devices"][0]["vendor_id"], "8086")
            self.assertEqual(result["devices"][1]["bus"], "usb")
            self.assertFalse(result["telemetry"])

    def test_ignores_invalid_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pci = root / "bus/pci/devices/0000:00:01.0"
            self.write(pci / "vendor", "not-an-id")
            self.write(pci / "device", "1234")
            self.assertEqual(HARDWARE.scan(root)["devices"], [])

if __name__ == "__main__":
    unittest.main()
