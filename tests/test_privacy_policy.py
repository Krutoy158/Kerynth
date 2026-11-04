import ast
import importlib.util
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARDWARE_PATH = ROOT / "tools" / "kerynth-hw"
SPEC = importlib.util.spec_from_loader(
    "kerynth_privacy_hardware",
    SourceFileLoader("kerynth_privacy_hardware", str(HARDWARE_PATH)),
)
HARDWARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HARDWARE)

NETWORK_MODULES = {
    "socket",
    "urllib",
    "http",
    "requests",
    "httpx",
    "aiohttp",
    "smtplib",
    "ftplib",
}


class PrivacyPolicyTests(unittest.TestCase):
    def test_hardware_inventory_has_no_network_client_imports(self):
        tree = ast.parse(HARDWARE_PATH.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
        self.assertTrue(NETWORK_MODULES.isdisjoint(imported))

    def test_hardware_inventory_declares_telemetry_disabled(self):
        with tempfile.TemporaryDirectory() as directory:
            result = HARDWARE.scan(
                directory,
                modules_root=Path(directory) / "modules",
                kernel_release="test",
                firmware_root=Path(directory) / "firmware",
                modinfo_binary="",
            )
        self.assertIs(result["telemetry"], False)
        self.assertEqual(result["devices"], [])


if __name__ == "__main__":
    unittest.main()
