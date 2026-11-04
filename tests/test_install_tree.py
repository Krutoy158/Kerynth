import importlib.util
import json
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "kerynth-install-tree"
SPEC = importlib.util.spec_from_loader("kerynth_install_tree", SourceFileLoader("kerynth_install_tree", str(TOOL)))
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)

PASSWORD_HASH = "$6$salt$abcdefghijklmnopqrstuvwxyz0123456789"


class InstallTreeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary.name) / ".kerynth-work"
        root = self.workspace / "rootfs"
        (root / "etc").mkdir(parents=True)
        (root / "home/kerynth").mkdir(parents=True)
        (root / "var/lib/kerynth").mkdir(parents=True)
        (root / "boot").mkdir()
        (root / "etc/passwd").write_text(
            "root:x:0:0:root:/root:/bin/sh\nkerynth:x:1000:1000:Kerynth Live:/home/kerynth:/bin/sh\n",
            encoding="utf-8",
        )
        (root / "etc/group").write_text("root:x:0:\nusers:x:1000:kerynth\n", encoding="utf-8")
        (root / "etc/shadow").write_text(
            "root:!:19000:0:99999:7:::\nkerynth:!:19000:0:99999:7:::\n",
            encoding="utf-8",
        )
        (root / "etc/hostname").write_text("kerynth\n", encoding="utf-8")
        (root / "etc/fstab").write_text("", encoding="utf-8")
        (root / ".kerynth-rootfs.json").write_text('{"format":1}\n', encoding="utf-8")
        self.kernel = self.workspace / "kernel"
        self.kernel.mkdir()
        (self.kernel / "vmlinuz").write_bytes(b"kernel-image")
        (self.workspace / "initramfs.cpio.gz").write_bytes(b"initramfs-image")

    def tearDown(self):
        self.temporary.cleanup()

    def install(self, **overrides):
        args = {
            "target_name": "test-install",
            "mode": "manual",
            "root_uuid": "12345678-1234-1234-1234-123456789abc",
            "efi_uuid": "87654321-4321-4321-4321-cba987654321",
            "username": "tema",
            "hostname": "kerynth-test",
            "password_hash": PASSWORD_HASH,
        }
        args.update(overrides)
        return INSTALLER.prepare_install(self.workspace, **args)

    def test_prepares_installed_root_tree(self):
        target = self.install()
        self.assertEqual((target / "etc/hostname").read_text(), "kerynth-test\n")
        self.assertIn("UUID=12345678-1234-1234-1234-123456789abc / ext4", (target / "etc/fstab").read_text())
        self.assertIn("UUID=87654321-4321-4321-4321-cba987654321 /boot/efi vfat", (target / "etc/fstab").read_text())
        self.assertIn("set timeout=5", (target / "boot/grub/grub.cfg").read_text())
        self.assertTrue((target / "boot/vmlinuz").is_file())
        self.assertTrue((target / "boot/initramfs.cpio.gz").is_file())
        self.assertIn("root=UUID=12345678-1234-1234-1234-123456789abc", (target / "boot/grub/grub.cfg").read_text())
        self.assertIn("tema:x:1000:1000:tema:/home/tema:/bin/sh", (target / "etc/passwd").read_text())
        self.assertIn("tema:" + PASSWORD_HASH, (target / "etc/shadow").read_text())
        state = json.loads((target / "var/lib/kerynth/installation.json").read_text())
        self.assertFalse(state["bootloader_installed"])
        self.assertFalse(state["partition_table_modified"])
        self.assertTrue((target / "home/tema").is_dir())
        self.assertFalse((target / "home/kerynth").exists())

    def test_refuses_to_overwrite_existing_target(self):
        target = self.install()
        with self.assertRaises(INSTALLER.InstallError):
            self.install()
        self.assertTrue((target / "etc/passwd").is_file())

    def test_refuses_invalid_uuid(self):
        with self.assertRaises(INSTALLER.InstallError):
            self.install(root_uuid="not-a-uuid")

    def test_refuses_invalid_efi_uuid(self):
        with self.assertRaises(INSTALLER.InstallError):
            self.install(efi_uuid="invalid")

    def test_refuses_invalid_account_name(self):
        with self.assertRaises(INSTALLER.InstallError):
            self.install(username="../root")

    def test_refuses_invalid_password_hash(self):
        with self.assertRaises(INSTALLER.InstallError):
            self.install(password_hash="plaintext-password")

    def test_refuses_symlink_escape_in_rootfs(self):
        root = self.workspace / "rootfs"
        (root / "etc/escape").symlink_to("/etc/passwd")
        with self.assertRaises(INSTALLER.InstallError):
            self.install()


if __name__ == "__main__":
    unittest.main()
