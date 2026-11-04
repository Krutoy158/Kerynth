import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from importlib.machinery import SourceFileLoader
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
KER_SPEC = importlib.util.spec_from_loader(
    "ker_repository_test_package",
    SourceFileLoader("ker_repository_test_package", str(ROOT / "tools" / "ker-package")),
)
KER = importlib.util.module_from_spec(KER_SPEC)
KER_SPEC.loader.exec_module(KER)

REPO_SPEC = importlib.util.spec_from_loader(
    "ker_repository_test_tool",
    SourceFileLoader("ker_repository_test_tool", str(ROOT / "tools" / "ker-repository")),
)
REPOSITORY = importlib.util.module_from_spec(REPO_SPEC)
REPO_SPEC.loader.exec_module(REPOSITORY)


class KerRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.packages = self.root / "packages"
        self.packages.mkdir()
        self.private = Ed25519PrivateKey.generate()
        self.private_path = self.root / "private.pem"
        self.private_path.write_bytes(self.private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
        public = self.private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.keyring = self.root / "keyring.json"
        self.keyring.write_text(json.dumps({"test-key": public.hex()}), encoding="utf-8")
        self.repo = self.root / "repository"

    def tearDown(self):
        self.temporary.cleanup()

    def make_package(self, name, version="1.0"):
        payload = self.root / ("payload-" + name + "-" + version)
        file_path = payload / "usr/share/kerynth-tests" / (name + ".txt")
        file_path.parent.mkdir(parents=True)
        file_path.write_text(name + " " + version + "\n", encoding="utf-8")
        output = self.packages / (name + "-" + version + ".ker")
        KER.build(Namespace(
            payload_dir=str(payload),
            name=name,
            version=version,
            architecture="x86_64",
            description="Test package " + name,
            key_id="test-key",
            private_key=str(self.private_path),
            depends=[],
            conflicts=[],
            output=str(output),
        ))
        return output

    def build_repository(self):
        REPOSITORY.build_repository(Namespace(
            repository="stable",
            packages_dir=str(self.packages),
            output_dir=str(self.repo),
            keyring=str(self.keyring),
            key_id="test-key",
            private_key=str(self.private_path),
        ))

    def test_signed_repository_build_and_verify(self):
        self.make_package("hello")
        self.build_repository()
        index = REPOSITORY.verify_repository(self.repo, self.keyring)
        self.assertEqual(index["repository"], "stable")
        self.assertEqual(len(index["packages"]), 1)
        self.assertEqual(index["packages"][0]["name"], "hello")
        self.assertEqual((self.repo / "index.ed25519").stat().st_size, 64)

    def test_package_tampering_is_rejected(self):
        package = self.make_package("tamper")
        self.build_repository()
        with package.open("ab") as stream:
            stream.write(b"changed")
        with self.assertRaises(REPOSITORY.RepositoryError):
            REPOSITORY.verify_repository(self.repo, self.keyring)

    def test_index_tampering_is_rejected(self):
        self.make_package("index-test")
        self.build_repository()
        index_path = self.repo / "index.json"
        index_path.write_bytes(index_path.read_bytes() + b" ")
        with self.assertRaises(REPOSITORY.RepositoryError):
            REPOSITORY.verify_repository(self.repo, self.keyring)

    def test_untrusted_repository_key_is_rejected(self):
        self.make_package("untrusted")
        self.build_repository()
        other = Ed25519PrivateKey.generate().public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        wrong_keyring = self.root / "wrong-keyring.json"
        wrong_keyring.write_text(json.dumps({"other-key": other.hex()}), encoding="utf-8")
        with self.assertRaises(REPOSITORY.RepositoryError):
            REPOSITORY.verify_repository(self.repo, wrong_keyring)

    def test_multiple_versions_of_one_package_are_rejected(self):
        self.make_package("duplicate", "1.0")
        self.make_package("duplicate", "2.0")
        with self.assertRaises(REPOSITORY.RepositoryError):
            self.build_repository()
        self.assertFalse(self.repo.exists())

    def test_path_traversal_in_index_is_rejected(self):
        value = {
            "format_version": 1,
            "repository": "stable",
            "architecture": "x86_64",
            "signing_key_id": "test-key",
            "packages": [{
                "filename": "../outside.ker",
                "name": "outside",
                "version": "1.0",
                "architecture": "x86_64",
                "description": "Outside package",
                "sha256": "0" * 64,
                "size": 1,
                "dependencies": [],
                "conflicts": [],
            }],
        }
        with self.assertRaises(REPOSITORY.RepositoryError):
            REPOSITORY.read_index(REPOSITORY.canonical(value))


if __name__ == "__main__":
    unittest.main()
