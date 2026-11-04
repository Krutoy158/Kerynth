import importlib.util
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import call, patch
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



    def test_cleanup_unmounts_in_reverse_order_before_detaching_loop(self):
        mounted = [Path("/mnt/root"), Path("/mnt/root/boot/efi")]
        results = [SimpleNamespace(returncode=0, stderr="")] * 3
        with patch.object(INSTALLER, "run_command", side_effect=results) as command:
            INSTALLER.cleanup_mounts_and_loop(mounted, "/dev/loop12")
        self.assertEqual(
            command.call_args_list,
            [
                call(["umount", "/mnt/root/boot/efi"], check=False),
                call(["umount", "/mnt/root"], check=False),
                call(["losetup", "--detach", "/dev/loop12"], check=False),
            ],
        )

    def test_cleanup_uses_lazy_unmount_fallback(self):
        mounted = [Path("/mnt/root")]
        results = [
            SimpleNamespace(returncode=1, stderr="busy"),
            SimpleNamespace(returncode=0, stderr=""),
            SimpleNamespace(returncode=0, stderr=""),
        ]
        with patch.object(INSTALLER, "run_command", side_effect=results) as command:
            INSTALLER.cleanup_mounts_and_loop(mounted, "/dev/loop12")
        self.assertEqual(command.call_count, 3)
        self.assertEqual(command.call_args_list[1], call(["umount", "--lazy", "/mnt/root"], check=False))

    def test_cleanup_reports_mount_and_loop_failures(self):
        mounted = [Path("/mnt/root")]
        results = [
            SimpleNamespace(returncode=1, stderr="busy"),
            SimpleNamespace(returncode=1, stderr="still busy"),
            SimpleNamespace(returncode=1, stderr="device busy"),
        ]
        with patch.object(INSTALLER, "run_command", side_effect=results):
            with self.assertRaisesRegex(INSTALLER.SystemInstallError, "installer cleanup failed"):
                INSTALLER.cleanup_mounts_and_loop(mounted, "/dev/loop12")

if __name__ == "__main__":
    unittest.main()
