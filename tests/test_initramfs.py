import gzip
import importlib.util
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "kerynth-initramfs"
SPEC = importlib.util.spec_from_loader(
    "kerynth_initramfs",
    SourceFileLoader("kerynth_initramfs", str(TOOL_PATH)),
)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class InitramfsTests(unittest.TestCase):
    def make_root(self, root):
        (root / "bin").mkdir()
        (root / "init").write_text("#!/bin/busybox sh\n", encoding="utf-8")
        (root / "init").chmod(0o755)
        (root / "bin" / "busybox").write_bytes(b"busybox-test")
        (root / "bin" / "busybox").chmod(0o755)
        (root / "lib").mkdir()
        parser = root / "lib" / "kerynth-boot-mode"
        parser.write_text("#!/bin/busybox sh\\nexit 0\\n", encoding="utf-8")
        parser.chmod(0o755)

    def test_live_initramfs_uses_writable_overlay_over_squashfs(self):
        init = (ROOT / "initramfs" / "init").read_text(encoding="utf-8")
        kernel = (ROOT / "kernel" / "kerynth-x86_64.fragment").read_text(encoding="utf-8")
        self.assertIn("mount -t squashfs -o loop,ro /media/live/rootfs.squashfs /lower", init)
        self.assertIn("size=256M", init)
        self.assertIn("mount -t overlay overlay", init)
        self.assertIn("CONFIG_OVERLAY_FS=y", kernel)

        self.assertIn("CONFIG_TMPFS_XATTR=y", kernel)
        self.assertIn("CONFIG_TMPFS_XATTR=y", PIPELINE.KERNEL_REQUIRED)

    def test_builds_deterministic_gzip_newc_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            root.mkdir()
            self.make_root(root)
            output_a = Path(directory) / "a.cpio.gz"
            output_b = Path(directory) / "b.cpio.gz"
            BUILDER.build(root, output_a)
            BUILDER.build(root, output_b)
            self.assertEqual(output_a.read_bytes(), output_b.read_bytes())
            archive = gzip.decompress(output_a.read_bytes())
            self.assertTrue(archive.startswith(b"070701"))
            self.assertIn(b"TRAILER!!!\0", archive)


    def test_rejects_missing_boot_mode_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            root.mkdir()
            self.make_root(root)
            (root / "lib" / "kerynth-boot-mode").unlink()
            with self.assertRaises(BUILDER.InitramfsError):
                BUILDER.collect(root)

    def test_rejects_missing_init(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bin").mkdir()
            binary = root / "bin" / "busybox"
            binary.write_bytes(b"busybox")
            binary.chmod(0o755)
            with self.assertRaises(BUILDER.InitramfsError):
                BUILDER.collect(root)

    def test_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            root.mkdir()
            self.make_root(root)
            (root / "link").symlink_to(root / "init")
            with self.assertRaises(BUILDER.InitramfsError):
                BUILDER.collect(root)


if __name__ == "__main__":
    unittest.main()
