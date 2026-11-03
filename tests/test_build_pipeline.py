import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools" / "kerynth-build-pipeline"
SPEC = importlib.util.spec_from_loader("kerynth_pipeline_test", SourceFileLoader("kerynth_pipeline_test", str(PATH)))
PIPELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PIPELINE)


class BuildPipelineTests(unittest.TestCase):
    def test_safe_name_rejects_traversal_and_absolute_paths(self):
        for value in ("../escape", "pkg/../../escape", "/etc/passwd", "pkg\\escape", "C:/escape"):
            with self.subTest(value=value):
                with self.assertRaises(PIPELINE.PipelineError):
                    PIPELINE.safe_name(value)

    def test_safe_name_strips_archive_root(self):
        self.assertEqual(PIPELINE.safe_name("./linux-6.6.161/README").as_posix(), "linux-6.6.161/README")

    def test_safe_link_rejects_escape(self):
        self.assertFalse(PIPELINE.safe_link(PurePosixPath("usr/link"), "../../../outside"))
        self.assertTrue(PIPELINE.safe_link(PurePosixPath("usr/lib/link"), "../libc.so"))

    def test_extract_source_strips_single_archive_root(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            archive_path = base / "source.tar"
            with tarfile.open(archive_path, "w") as archive:
                data = b"Kerynth source"
                info = tarfile.TarInfo("sample-1/README")
                info.size = len(data)
                info.mode = 0o644
                archive.addfile(info, io.BytesIO(data))
            source = {"name": "sample", "filename": "sample.tar", "sha256": "a" * 64}
            result = PIPELINE.extract_source(source, archive_path, base)
            self.assertEqual((result / "README").read_bytes(), b"Kerynth source")
            self.assertEqual(json.loads((result / ".kerynth-source.json").read_text()), source)

    def test_extract_source_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            archive_path = base / "bad.tar"
            with tarfile.open(archive_path, "w") as archive:
                data = b"escape"
                info = tarfile.TarInfo("sample-1/../../outside")
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
            source = {"name": "sample", "filename": "bad.tar", "sha256": "b" * 64}
            with self.assertRaises(PIPELINE.PipelineError):
                PIPELINE.extract_source(source, archive_path, base)

    def test_busybox_config_enables_static_required_applets(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".config"
            path.write_text("# CONFIG_STATIC is not set\n# CONFIG_INIT is not set\n", encoding="utf-8")
            PIPELINE.set_busybox_config(path, ROOT / "initramfs" / "busybox.config.fragment")
            content = path.read_text(encoding="utf-8")
            for symbol in ("STATIC", "INIT", "MOUNT", "SWITCH_ROOT", "GETTY", "BLKID", "ID"):
                self.assertIn("CONFIG_{}=y".format(symbol), content)
            self.assertIn("# CONFIG_TC is not set", content)

    def test_base_root_account_is_locked_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            PIPELINE.write_base(root, False)
            self.assertIn("root:!", (root / "etc/shadow").read_text(encoding="utf-8"))
            self.assertIn("/etc/init.d/kerynth-session", (root / "etc/inittab").read_text(encoding="utf-8"))
            self.assertIn("/sbin/getty", (root / "etc/init.d/kerynth-session").read_text(encoding="utf-8"))

    def test_developer_shell_requires_explicit_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            PIPELINE.write_base(root, True)
            self.assertIn("console::respawn:/bin/sh", (root / "etc/inittab").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
