import gzip
import importlib.util
import shutil
import stat
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_loader(
        name,
        SourceFileLoader(name, str(path)),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ISO_TOOL = load_module("kerynth_iso", ROOT / "tools" / "kerynth-iso")
INITRAMFS_TOOL = load_module("kerynth_initramfs_for_iso", ROOT / "tools" / "kerynth-initramfs")


class IsoBuilderTests(unittest.TestCase):
    def make_root(self, directory):
        root = Path(directory) / "iso-root"
        (root / "boot" / "grub").mkdir(parents=True)
        (root / "live").mkdir()
        (root / "boot" / "grub" / "grub.cfg").write_text(
            (ROOT / "boot" / "grub" / "grub.cfg").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (root / "boot" / "vmlinuz").write_bytes(b"kernel-test-image")
        (root / "live" / "rootfs.squashfs").write_bytes(b"hsqs" + b"\0" * 92)

        initramfs_root = Path(directory) / "initramfs-root"
        (initramfs_root / "bin").mkdir(parents=True)
        (initramfs_root / "lib").mkdir()
        for relative in ("init", "bin/busybox", "lib/kerynth-boot-mode"):
            path = initramfs_root / relative
            path.write_bytes(b"kerynth-test")
            path.chmod(0o755)

        INITRAMFS_TOOL.build(
            initramfs_root,
            root / "boot" / "initramfs.cpio.gz",
        )
        return root

    def test_accepts_complete_iso_staging_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            self.assertEqual(ISO_TOOL.validate_iso_root(root), root.resolve())

    def test_rejects_missing_required_iso_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / "live" / "rootfs.squashfs").unlink()
            with self.assertRaises(ISO_TOOL.IsoError):
                ISO_TOOL.validate_iso_root(root)

    def test_rejects_symlinks_in_iso_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / "live" / "linked-image").symlink_to(root / "boot" / "vmlinuz")
            with self.assertRaises(ISO_TOOL.IsoError):
                ISO_TOOL.validate_iso_root(root)

    def test_rejects_invalid_squashfs_magic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / "live" / "rootfs.squashfs").write_bytes(b"nope" + b"\0" * 92)
            with self.assertRaises(ISO_TOOL.IsoError):
                ISO_TOOL.validate_iso_root(root)

    def test_rejects_grub_menu_with_an_automatic_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            config = root / "boot" / "grub" / "grub.cfg"
            config.write_text(
                config.read_text(encoding="utf-8").replace("set timeout=-1", "set timeout=5"),
                encoding="utf-8",
            )
            with self.assertRaises(ISO_TOOL.IsoError):
                ISO_TOOL.validate_iso_root(root)

    def test_rejects_initramfs_without_boot_mode_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            archive = bytearray()
            archive.extend(
                INITRAMFS_TOOL.cpio_record(
                    "init", stat.S_IFREG | 0o755, b"init", 1
                )
            )
            archive.extend(
                INITRAMFS_TOOL.cpio_record(
                    "bin/busybox", stat.S_IFREG | 0o755, b"busybox", 2
                )
            )
            archive.extend(INITRAMFS_TOOL.cpio_record("TRAILER!!!", 0, b"", 3))
            with (root / "boot" / "initramfs.cpio.gz").open("wb") as stream:
                stream.write(gzip.compress(bytes(archive), mtime=0))
            with self.assertRaises(ISO_TOOL.IsoError):
                ISO_TOOL.validate_iso_root(root)

    def test_rejects_invalid_cpio_inside_gzip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_root(directory)
            (root / "boot" / "initramfs.cpio.gz").write_bytes(gzip.compress(b"invalid"))
            with self.assertRaises(ISO_TOOL.IsoError):
                ISO_TOOL.validate_iso_root(root)

    def test_iso9660_signature_check(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.iso"
            with path.open("wb") as stream:
                stream.truncate(16 * 2048)
                stream.write(b"\x01CD001\x01")
            self.assertTrue(ISO_TOOL.has_iso9660_signature(path))

    def test_output_path_must_stay_in_project_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory) / "outside.iso"
            with self.assertRaises(ISO_TOOL.IsoError):
                ISO_TOOL.ensure_workspace_path(outside, "ISO output")


if __name__ == "__main__":
    unittest.main()
