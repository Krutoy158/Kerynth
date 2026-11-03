import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from importlib.machinery import SourceFileLoader


ROOT = Path(__file__).resolve().parents[1]
BUILD_TOOL = SourceFileLoader("aether_build", str(ROOT / "tools" / "aether-build")).load_module()


class BuildToolTests(unittest.TestCase):
    def test_default_configuration_is_valid(self):
        config = BUILD_TOOL.load_config(ROOT / "aether.toml")
        self.assertEqual(config["architecture"], "x86_64")
        self.assertEqual(config["workspace"], (ROOT / ".aether-work").resolve())

    def test_workspace_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "aether.toml"
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

        invalid = dict(valid, url="http://example.invalid/linux.tar.xz")
        with self.assertRaises(BUILD_TOOL.BuildError):
            BUILD_TOOL.validate_source(invalid)

    def test_source_filename_cannot_contain_a_path(self):
        source = {
            "name": "linux",
            "url": "https://example.invalid/linux.tar.xz",
            "filename": "../linux.tar.xz",
            "sha256": "a" * 64,
        }
        with self.assertRaises(BUILD_TOOL.BuildError):
            BUILD_TOOL.validate_source(source)

    def test_sha256_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample"
            path.write_bytes(b"AETHER OS")
            self.assertEqual(
                BUILD_TOOL.sha256_file(path),
                hashlib.sha256(b"AETHER OS").hexdigest(),
            )

    def test_lock_rejects_duplicate_names(self):
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


if __name__ == "__main__":
    unittest.main()
