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


class BootMenuTests(unittest.TestCase):
    def setUp(self):
        self.content = (ROOT / "boot" / "grub" / "grub.cfg").read_text(
            encoding="utf-8"
        )

    def test_menu_has_exactly_three_user_choices(self):
        import re

        entries = re.findall(
            r'^menuentry\s+"([^"]+)"\s+--id\s+([a-z0-9-]+)\s*\{',
            self.content,
            flags=re.MULTILINE,
        )
        self.assertEqual(
            entries,
            [
                ("Manual Installation", "kerynth-manual"),
                ("Automatic Installation", "kerynth-automatic"),
                ("Live System", "kerynth-live"),
            ],
        )

    def test_menu_waits_for_user(self):
        self.assertIn("set timeout=-1", self.content)
        self.assertIn("set default=0", self.content)
        self.assertNotIn("timeout_style", self.content)

    def test_menu_shows_only_ker_branding(self):
        self.assertIn('echo "  K   K  EEEEE  RRRR"', self.content)
        import re

        self.assertNotRegex(
            self.content,
            r"(?i)\b(cpu|memory|ram|hostname|username|processor|gpu|network|release|version)\b",
        )

    def test_menu_entries_use_distinct_boot_modes(self):
        expected = {
            "kerynth-manual": "kerynth.mode=installer-manual",
            "kerynth-automatic": "kerynth.mode=installer-automatic",
            "kerynth-live": "kerynth.mode=live",
        }
        import re

        for entry_id, mode in expected.items():
            with self.subTest(entry=entry_id):
                match = re.search(
                    rf'menuentry\s+"[^"]+"\s+--id\s+{entry_id}\s*\{{(.*?)^\}}',
                    self.content,
                    flags=re.MULTILINE | re.DOTALL,
                )
                self.assertIsNotNone(match)
                self.assertIn(mode, match.group(1))
                self.assertIn("initrd /boot/initramfs.cpio.gz", match.group(1))


if __name__ == "__main__":
    unittest.main()
