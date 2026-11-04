import importlib.util
import os
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "kerynth-install-system-image"
SPEC = importlib.util.spec_from_loader(
    "kerynth_install_system_image_test",
    SourceFileLoader("kerynth_install_system_image_test", str(TOOL)),
)
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)

PASSWORD_HASH = "$6$testsalt$abcdefghijklmnopqrstuvwxyz0123456789"


class InstallerSystemImageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.password_file = self.root / "password-hash"
        self.password_file.write_text(PASSWORD_HASH + "\n", encoding="ascii")
        os.chmod(self.password_file, 0o600)

    def tearDown(self):
        self.temporary.cleanup()

    def test_accepts_private_regular_password_hash_file(self):
        self.assertEqual(INSTALLER.validate_password_hash_file(self.password_file), PASSWORD_HASH)

    def test_rejects_password_hash_symlink(self):
        link = self.root / "linked-hash"
        link.symlink_to(self.password_file)
        with self.assertRaises(INSTALLER.SystemInstallError):
            INSTALLER.validate_password_hash_file(link)

    def test_rejects_password_hash_file_with_broad_permissions(self):
        os.chmod(self.password_file, 0o644)
        with self.assertRaises(INSTALLER.SystemInstallError):
            INSTALLER.validate_password_hash_file(self.password_file)

    def test_rejects_non_crypt_password(self):
        self.password_file.write_text("plain-text-password\n", encoding="ascii")
        os.chmod(self.password_file, 0o600)
        with self.assertRaises(INSTALLER.SystemInstallError):
            INSTALLER.validate_password_hash_file(self.password_file)

    def test_constructs_only_loop_partition_paths(self):
        self.assertEqual(str(INSTALLER.loop_partition_path("/dev/loop12", 2)), "/dev/loop12p2")
        with self.assertRaises(INSTALLER.SystemInstallError):
            INSTALLER.loop_partition_path("/dev/sda", 2)
        with self.assertRaises(INSTALLER.SystemInstallError):
            INSTALLER.loop_partition_path("/dev/loop12", 3)


if __name__ == "__main__":
    unittest.main()
