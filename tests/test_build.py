import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import importlib.util
from importlib.machinery import SourceFileLoader


ROOT = Path(__file__).resolve().parents[1]
BUILD_TOOL_PATH = ROOT / "tools" / "kerynth-build"
SPEC = importlib.util.spec_from_loader(
    "kerynth_build",
    SourceFileLoader("kerynth_build", str(BUILD_TOOL_PATH)),
)
BUILD_TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD_TOOL)


class BuildToolTests(unittest.TestCase):
    def test_default_configuration_is_valid(self):
        config = BUILD_TOOL.load_config(ROOT / "kerynth.toml")
        self.assertEqual(config["architecture"], "x86_64")
        self.assertEqual(config["workspace"], (ROOT / ".kerynth-work").resolve())

    def test_workspace_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "kerynth.toml"
            config.write_text(
                '[build]\narchitecture = "x86_64"\nworkspace = "../outside"\n',
                encoding="utf-8",
            )
            with self.assertRaises(BUILD_TOOL.BuildError):
                BUILD_TOOL.load_config(config)

    def test_source_requires_https_and_digest(self):
        valid = {
            "name": "linux",
            "url": "https://example.invalid/linux.tar.xz",
            "filename": "linux.tar.xz",
            "sha256": "a" * 64,
        }
        self.assertEqual(BUILD_TOOL.validate_source(valid), valid)
        with self.assertRaises(BUILD_TOOL.BuildError):
            BUILD_TOOL.validate_source(dict(valid, url="http://example.invalid/linux.tar.xz"))

    def test_source_rejects_embedded_credentials(self):
        source = {
            "name": "linux",
            "url": "https://user:password@example.invalid/linux.tar.xz",
            "filename": "linux.tar.xz",
            "sha256": "a" * 64,
        }
        with self.assertRaises(BUILD_TOOL.BuildError):
            BUILD_TOOL.validate_source(source)

    def test_source_filename_cannot_contain_a_path(self):
        source = {
            "name": "linux",
            "url": "https://example.invalid/linux.tar.xz",
            "filename": "../linux.tar.xz",
            "sha256": "a" * 64,
        }
        with self.assertRaises(BUILD_TOOL.BuildError):
            BUILD_TOOL.validate_source(source)

    def test_source_filename_rejects_control_characters(self):
        source = {
            "name": "linux",
            "url": "https://example.invalid/linux.tar.xz",
            "filename": "linux\n.tar.xz",
            "sha256": "a" * 64,
        }
        with self.assertRaises(BUILD_TOOL.BuildError):
            BUILD_TOOL.validate_source(source)

    def test_sha256_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample"
            path.write_bytes(b"Kerynth")
            self.assertEqual(
                BUILD_TOOL.sha256_file(path),
                hashlib.sha256(b"Kerynth").hexdigest(),
            )

    def test_lock_rejects_duplicate_names_and_filenames(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sources.lock"
            source = {
                "name": "linux",
                "url": "https://example.invalid/linux.tar.xz",
                "filename": "linux.tar.xz",
                "sha256": "a" * 64,
            }
            path.write_text(
                json.dumps({"version": 1, "sources": [source, source]}),
                encoding="utf-8",
            )
            with self.assertRaises(BUILD_TOOL.BuildError):
                BUILD_TOOL.load_lock(path)

            second = dict(source, name="linux-source")
            path.write_text(
                json.dumps({"version": 1, "sources": [source, second]}),
                encoding="utf-8",
            )
            with self.assertRaises(BUILD_TOOL.BuildError):
                BUILD_TOOL.load_lock(path)

    def test_lock_rejects_unknown_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sources.lock"
            path.write_text(
                json.dumps({"version": 1, "sources": [], "telemetry": True}),
                encoding="utf-8",
            )
            with self.assertRaises(BUILD_TOOL.BuildError):
                BUILD_TOOL.load_lock(path)

    def test_fetch_rejects_cache_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "work"
            cache = workspace / "sources"
            cache.mkdir(parents=True)
            outside = root / "outside"
            outside.write_text("do not touch", encoding="utf-8")
            (cache / "linux.tar.xz").symlink_to(outside)
            source = {
                "name": "linux",
                "url": "https://example.invalid/linux.tar.xz",
                "filename": "linux.tar.xz",
                "sha256": "a" * 64,
            }
            with self.assertRaises(BUILD_TOOL.BuildError):
                BUILD_TOOL.fetch_source(source, workspace)
            self.assertEqual(outside.read_text(encoding="utf-8"), "do not touch")


if __name__ == "__main__":
    unittest.main()
