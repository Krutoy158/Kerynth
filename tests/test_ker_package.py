import importlib.util
import tempfile
import unittest
from argparse import Namespace
from importlib.machinery import SourceFileLoader
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "ker-package"
SPEC = importlib.util.spec_from_loader("ker_package_test", SourceFileLoader("ker_package_test", str(TOOL)))
KER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(KER)


class KerPackageManagerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.work = Path(self.temporary.name)
        self.payload = self.work / "payload"
        self.payload.mkdir()
        (self.payload / "usr/bin").mkdir(parents=True)
        (self.payload / "usr/bin/hello").write_text("hello from Kerynth\n", encoding="utf-8")
        (self.payload / "usr/bin/hello").chmod(0o755)
        self.private = Ed25519PrivateKey.generate()
        self.private_path = self.work / "private.pem"
        self.private_path.write_bytes(self.private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
        public = self.private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.keyring = self.work / "keyring.json"
        self.keyring.write_text('{"test-key":"' + public.hex() + '"}', encoding="utf-8")
        allowed = ROOT / ".kerynth-work" / "targets"
        allowed.mkdir(parents=True, exist_ok=True)
        self.root_temp = tempfile.TemporaryDirectory(dir=allowed)
        self.target = Path(self.root_temp.name) / "root"

    def tearDown(self):
        self.root_temp.cleanup()
        self.temporary.cleanup()

    def make_package(self, name, version="1.0", depends=None, conflicts=None):
        output = self.work / (name + ".ker")
        args = Namespace(
            payload_dir=str(self.payload),
            name=name,
            version=version,
            architecture="x86_64",
            description="Test package " + name,
            key_id="test-key",
            private_key=str(self.private_path),
            depends=depends or [],
            conflicts=conflicts or [],
            output=str(output),
        )
        KER.build(args)
        return output

    def install_package(self, package):
        KER.install(Namespace(package=str(package), keyring=str(self.keyring), root=str(self.target)))

    def test_install_and_remove_signed_package(self):
        package = self.make_package("hello")
        self.install_package(package)
        installed_file = self.target / "usr/bin/hello"
        self.assertEqual(installed_file.read_text(encoding="utf-8"), "hello from Kerynth\n")
        records = KER.read_installed(self.target)
        self.assertEqual(records["hello"]["version"], "1.0")
        KER.remove(Namespace(name="hello", root=str(self.target)))
        self.assertFalse(installed_file.exists())
        self.assertNotIn("hello", KER.read_installed(self.target))

    def test_dependency_must_be_installed_before_package(self):
        package = self.make_package("app", depends=["base=1.0"])
        with self.assertRaises(KER.PackageError):
            self.install_package(package)
        self.assertFalse((self.target / "usr/bin/hello").exists())

    def test_package_dependency_blocks_removal(self):
        base = self.make_package("base")
        app = self.make_package("app", depends=["base=1.0"])
        self.install_package(base)
        self.install_package(app)
        with self.assertRaises(KER.PackageError):
            KER.remove(Namespace(name="base", root=str(self.target)))
        self.assertIn("base", KER.read_installed(self.target))

    def test_remove_refuses_modified_package_file(self):
        package = self.make_package("mutable")
        self.install_package(package)
        installed_file = self.target / "usr/bin/hello"
        installed_file.write_text("changed by user\n", encoding="utf-8")
        with self.assertRaises(KER.PackageError):
            KER.remove(Namespace(name="mutable", root=str(self.target)))
        self.assertTrue(installed_file.is_file())

    def test_package_conflict_blocks_install(self):
        blocker = self.make_package("blocker")
        app = self.make_package("app", conflicts=["blocker"])
        self.install_package(blocker)
        with self.assertRaises(KER.PackageError):
            self.install_package(app)

    def test_target_root_refuses_system_root(self):
        with self.assertRaises(KER.PackageError):
            KER.target_root("/")

    def test_package_relation_parser_rejects_duplicates(self):
        with self.assertRaises(KER.PackageError):
            KER.parse_relations(["base=1.0", "base=2.0"])


if __name__ == "__main__":
    unittest.main()
