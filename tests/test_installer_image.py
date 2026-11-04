import importlib.util
import os
import shutil
import stat
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
LAYOUT_PATH = ROOT / "tools" / "kerynth-install-layout"
IMAGE_PATH = ROOT / "tools" / "kerynth-install-image"

LAYOUT_SPEC = importlib.util.spec_from_loader(
    "kerynth_install_layout_for_image_test",
    SourceFileLoader("kerynth_install_layout_for_image_test", str(LAYOUT_PATH)),
)
LAYOUT = importlib.util.module_from_spec(LAYOUT_SPEC)
LAYOUT_SPEC.loader.exec_module(LAYOUT)

IMAGE_SPEC = importlib.util.spec_from_loader(
    "kerynth_install_image_test",
    SourceFileLoader("kerynth_install_image_test", str(IMAGE_PATH)),
)
IMAGE = importlib.util.module_from_spec(IMAGE_SPEC)
IMAGE_SPEC.loader.exec_module(IMAGE)


class InstallerImageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.image = self.root / "test-disk.img"
        self.disk_bytes = 4 * LAYOUT.GIB
        with self.image.open("wb") as stream:
            stream.truncate(self.disk_bytes)
        self.plan = LAYOUT.build_plan(self.disk_bytes, 512, "automatic")

    def tearDown(self):
        self.temporary.cleanup()

    def test_regular_disk_image_is_accepted(self):
        result = IMAGE.validate_image(self.image, self.disk_bytes)
        self.assertEqual(result, self.image.resolve())

    def test_block_device_is_rejected(self):
        device = Path("/dev/null")
        if not device.exists():
            self.skipTest("/dev/null is unavailable")
        with self.assertRaises(IMAGE.ImageInstallError):
            IMAGE.validate_image(device, self.disk_bytes)

    def test_symlink_is_rejected(self):
        link = self.root / "linked.img"
        link.symlink_to(self.image)
        with self.assertRaises(IMAGE.ImageInstallError):
            IMAGE.validate_image(link, self.disk_bytes)

    def test_hard_link_is_rejected(self):
        link = self.root / "linked-hard.img"
        os.link(self.image, link)
        with self.assertRaises(IMAGE.ImageInstallError):
            IMAGE.validate_image(self.image, self.disk_bytes)

    def test_wrong_extension_is_rejected(self):
        other = self.root / "test-disk.qcow2"
        other.write_bytes(b"\0" * 512)
        with self.assertRaises(IMAGE.ImageInstallError):
            IMAGE.validate_image(other, 512)

    def test_wrong_image_size_is_rejected(self):
        with self.assertRaises(IMAGE.ImageInstallError):
            IMAGE.validate_image(self.image, self.disk_bytes + 512)

    def test_unconfirmed_image_write_is_rejected_before_sfdisk(self):
        with patch.object(IMAGE, "run_sfdisk") as run:
            with self.assertRaises(IMAGE.ImageInstallError):
                IMAGE.apply_plan_to_image(self.image, self.plan)
            run.assert_not_called()

    def test_invalid_plan_is_rejected_before_sfdisk(self):
        with patch.object(IMAGE, "run_sfdisk") as run:
            with self.assertRaises(IMAGE.ImageInstallError):
                IMAGE.apply_plan_to_image(
                    self.image,
                    {"writes_performed": True},
                    confirm=True,
                )
            run.assert_not_called()

    def test_modified_sfdisk_script_is_rejected_before_sfdisk(self):
        plan = dict(self.plan)
        plan["sfdisk_script"] = "label: dos\\n"
        with patch.object(IMAGE, "run_sfdisk") as run:
            with self.assertRaises(IMAGE.ImageInstallError):
                IMAGE.apply_plan_to_image(self.image, plan, confirm=True)
            run.assert_not_called()

    def test_modified_partition_size_is_rejected_before_sfdisk(self):
        plan = dict(self.plan)
        plan["partitions"] = [dict(item) for item in self.plan["partitions"]]
        plan["partitions"][0]["size_sectors"] += 2048
        with patch.object(IMAGE, "run_sfdisk") as run:
            with self.assertRaises(IMAGE.ImageInstallError):
                IMAGE.apply_plan_to_image(self.image, plan, confirm=True)
            run.assert_not_called()

    def test_extra_plan_field_is_rejected_before_sfdisk(self):
        plan = dict(self.plan)
        plan["extra"] = "unexpected"
        with patch.object(IMAGE, "run_sfdisk") as run:
            with self.assertRaises(IMAGE.ImageInstallError):
                IMAGE.apply_plan_to_image(self.image, plan, confirm=True)
            run.assert_not_called()

    def test_inconsistent_geometry_is_rejected_before_sfdisk(self):
        plan = dict(self.plan)
        plan["geometry"] = dict(self.plan["geometry"])
        plan["geometry"]["last_usable_sector"] -= 1
        with patch.object(IMAGE, "run_sfdisk") as run:
            with self.assertRaises(IMAGE.ImageInstallError):
                IMAGE.apply_plan_to_image(self.image, plan, confirm=True)
            run.assert_not_called()

    @unittest.skipUnless(shutil.which("sfdisk"), "sfdisk is required for disk image integration")
    def test_writes_and_verifies_gpt_only_in_temporary_image(self):
        result = IMAGE.apply_plan_to_image(
            self.image,
            self.plan,
            shutil.which("sfdisk"),
            confirm=True,
        )
        self.assertEqual(result["target_type"], "regular_file")
        self.assertEqual(result["label"], "gpt")
        self.assertEqual(result["partition_count"], 2)
        self.assertTrue(result["writes_performed"])
        self.assertTrue(result["verified"])
        self.assertEqual(self.image.stat().st_size, self.disk_bytes)


if __name__ == "__main__":
    unittest.main()
