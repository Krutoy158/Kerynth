import importlib.util
import json
import subprocess
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "kerynth-install-layout"
SPEC = importlib.util.spec_from_loader(
    "kerynth_install_layout",
    SourceFileLoader("kerynth_install_layout", str(TOOL_PATH)),
)
LAYOUT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAYOUT)


class InstallerLayoutTests(unittest.TestCase):
    def setUp(self):
        self.disk_bytes = 8 * LAYOUT.GIB

    def test_automatic_layout_uses_aligned_gpt_efi_and_root(self):
        plan = LAYOUT.build_plan(self.disk_bytes, 512, "automatic")
        self.assertEqual(plan["partition_table"], "gpt")
        self.assertFalse(plan["writes_performed"])
        self.assertEqual(len(plan["partitions"]), 2)
        efi, root = plan["partitions"]
        self.assertEqual(efi["role"], "efi")
        self.assertEqual(efi["filesystem"], "vfat")
        self.assertEqual(efi["mountpoint"], "/boot/efi")
        self.assertEqual(efi["size_sectors"], 512 * LAYOUT.MIB // 512)
        self.assertEqual(root["role"], "root")
        self.assertEqual(root["filesystem"], "ext4")
        self.assertEqual(root["mountpoint"], "/")
        self.assertEqual(efi["end_sector"] + 1, root["start_sector"])
        self.assertEqual(efi["start_sector"] % plan["geometry"]["alignment_sectors"], 0)
        self.assertEqual(root["start_sector"] % plan["geometry"]["alignment_sectors"], 0)

    def test_automatic_layout_supports_4k_logical_sectors(self):
        plan = LAYOUT.build_plan(self.disk_bytes, 4096, "automatic")
        self.assertEqual(plan["geometry"]["sector_size"], 4096)
        for item in plan["partitions"]:
            self.assertEqual(item["start_sector"] % 256, 0)
            self.assertEqual(item["size_sectors"] % 256, 0)

    def test_automatic_layout_rejects_small_disks(self):
        with self.assertRaises(LAYOUT.LayoutError):
            LAYOUT.build_plan(2 * LAYOUT.GIB, 512, "automatic")

    def test_automatic_layout_rejects_manual_input(self):
        with self.assertRaises(LAYOUT.LayoutError):
            LAYOUT.build_plan(
                self.disk_bytes,
                512,
                "automatic",
                {"partitions": []},
            )

    def test_manual_layout_accepts_valid_efi_and_root_partitions(self):
        plan = LAYOUT.build_plan(
            self.disk_bytes,
            512,
            "manual",
            {"partitions": [
                {"role": "root", "start_mib": 513, "size_mib": 7000},
                {"role": "efi", "start_mib": 1, "size_mib": 512},
            ]},
        )
        self.assertEqual([item["role"] for item in plan["partitions"]], ["efi", "root"])
        self.assertEqual(plan["partitions"][0]["type_guid"], LAYOUT.EFI_GUID)
        self.assertEqual(plan["partitions"][1]["type_guid"], LAYOUT.LINUX_GUID)
        self.assertIn("label: gpt", plan["sfdisk_script"])
        self.assertIn("unit: sectors", plan["sfdisk_script"])
        self.assertFalse(plan["writes_performed"])

    def test_manual_layout_rejects_overlapping_partitions(self):
        with self.assertRaises(LAYOUT.LayoutError):
            LAYOUT.build_plan(
                self.disk_bytes,
                512,
                "manual",
                {"partitions": [
                    {"role": "efi", "start_mib": 1, "size_mib": 512},
                    {"role": "root", "start_mib": 500, "size_mib": 7000},
                ]},
            )

    def test_manual_layout_rejects_duplicate_roles(self):
        with self.assertRaises(LAYOUT.LayoutError):
            LAYOUT.build_plan(
                self.disk_bytes,
                512,
                "manual",
                {"partitions": [
                    {"role": "efi", "start_mib": 1, "size_mib": 512},
                    {"role": "efi", "start_mib": 513, "size_mib": 512},
                ]},
            )

    def test_manual_layout_rejects_invalid_efi_size(self):
        with self.assertRaises(LAYOUT.LayoutError):
            LAYOUT.build_plan(
                self.disk_bytes,
                512,
                "manual",
                {"partitions": [
                    {"role": "efi", "start_mib": 1, "size_mib": 64},
                    {"role": "root", "start_mib": 65, "size_mib": 7000},
                ]},
            )

    def test_manual_layout_rejects_small_root_size(self):
        with self.assertRaises(LAYOUT.LayoutError):
            LAYOUT.build_plan(
                self.disk_bytes,
                512,
                "manual",
                {"partitions": [
                    {"role": "efi", "start_mib": 1, "size_mib": 512},
                    {"role": "root", "start_mib": 513, "size_mib": 1024},
                ]},
            )

    def test_manual_layout_rejects_out_of_bounds_partition(self):
        with self.assertRaises(LAYOUT.LayoutError):
            LAYOUT.build_plan(
                self.disk_bytes,
                512,
                "manual",
                {"partitions": [
                    {"role": "efi", "start_mib": 1, "size_mib": 512},
                    {"role": "root", "start_mib": 513, "size_mib": 8000},
                ]},
            )

    def test_manual_layout_rejects_fractional_mib_boundaries(self):
        with self.assertRaises(LAYOUT.LayoutError):
            LAYOUT.build_plan(
                self.disk_bytes,
                512,
                "manual",
                {"partitions": [
                    {"role": "efi", "start_mib": 1, "size_mib": 512},
                    {"role": "root", "start_mib": 512.5, "size_mib": 7000},
                ]},
            )

    def test_manual_layout_rejects_partitions_before_efi(self):
        with self.assertRaises(LAYOUT.LayoutError):
            LAYOUT.build_plan(
                self.disk_bytes,
                512,
                "manual",
                {"partitions": [
                    {"role": "root", "start_mib": 1, "size_mib": 7000},
                    {"role": "efi", "start_mib": 7001, "size_mib": 512},
                ]},
            )

    def test_manual_layout_rejects_non_object_partitions(self):
        for partitions in ([None, {}], ["efi", "root"], [1, 2]):
            with self.subTest(partitions=partitions):
                with self.assertRaises(LAYOUT.LayoutError):
                    LAYOUT.build_plan(
                        self.disk_bytes,
                        512,
                        "manual",
                        {"partitions": partitions},
                    )

    def test_manual_layout_rejects_missing_and_unknown_fields(self):
        invalid = [
            [
                {"role": "efi", "size_mib": 512},
                {"role": "root", "start_mib": 513, "size_mib": 7000},
            ],
            [
                {"role": "efi", "start_mib": 1, "size_mib": 512, "filesystem": "vfat"},
                {"role": "root", "start_mib": 513, "size_mib": 7000},
            ],
        ]
        for partitions in invalid:
            with self.subTest(partitions=partitions):
                with self.assertRaises(LAYOUT.LayoutError):
                    LAYOUT.build_plan(
                        self.disk_bytes,
                        512,
                        "manual",
                        {"partitions": partitions},
                    )

    def test_manual_layout_rejects_non_integer_boundaries(self):
        for value in (True, 1.5, "513", None):
            with self.subTest(value=value):
                with self.assertRaises(LAYOUT.LayoutError):
                    LAYOUT.build_plan(
                        self.disk_bytes,
                        512,
                        "manual",
                        {"partitions": [
                            {"role": "efi", "start_mib": 1, "size_mib": 512},
                            {"role": "root", "start_mib": value, "size_mib": 7000},
                        ]},
                    )

    def test_manual_layout_rejects_invalid_top_level_data(self):
        invalid = (None, [], {}, {"partitions": None}, {"partitions": []}, {"partitions": [], "disk": "/dev/sda"})
        for layout in invalid:
            with self.subTest(layout=layout):
                with self.assertRaises(LAYOUT.LayoutError):
                    LAYOUT.build_plan(self.disk_bytes, 512, "manual", layout)

    def test_cli_outputs_plan_without_writing_devices(self):
        result = subprocess.run(
            [
                "python3",
                str(TOOL_PATH),
                "--disk-bytes",
                str(self.disk_bytes),
                "--sector-size",
                "512",
                "--mode",
                "automatic",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertFalse(plan["writes_performed"])
        self.assertEqual(plan["mode"], "automatic")


if __name__ == "__main__":
    unittest.main()
