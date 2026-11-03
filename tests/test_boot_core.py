import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BootCoreTests(unittest.TestCase):
    def test_init_script_has_valid_shell_syntax(self):
        shell = shutil.which("sh")
        self.assertIsNotNone(shell)
        result = subprocess.run(
            [shell, "-n", str(ROOT / "initramfs" / "init")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_required_boot_files_exist(self):
        required = [
            ROOT / "initramfs" / "init",
            ROOT / "initramfs" / "busybox.config.fragment",
            ROOT / "kernel" / "kerynth-x86_64.fragment",
            ROOT / "docs" / "boot-core.md",
        ]
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_file())

    def test_init_script_defaults_to_read_only_root(self):
        content = (ROOT / "initramfs" / "init").read_text(encoding="utf-8")
        self.assertIn('mount_args="-o ro"', content)
        self.assertIn('if [ "$ROOTFLAGS" = "rw" ]', content)
        self.assertIn('switch_root /newroot /sbin/init', content)


if __name__ == "__main__":
    unittest.main()
