import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRUB_CONFIG = ROOT / "boot" / "grub" / "grub.cfg"


class BootMenuTests(unittest.TestCase):
    def test_grub_config_exists(self):
        self.assertTrue(GRUB_CONFIG.is_file())

    def test_menu_has_exactly_three_choices(self):
        content = GRUB_CONFIG.read_text(encoding="utf-8")
        entries = re.findall(r'^menuentry "([^"]+)"', content, re.MULTILINE)
        self.assertEqual(
            entries,
            ["Manual Installation", "Automatic Installation", "Live System"],
        )

    def test_menu_displays_only_ker_branding(self):
        content = GRUB_CONFIG.read_text(encoding="utf-8")
        self.assertIn('echo "  K   K  EEEEE  RRRR"', content)
        self.assertNotIn("Fastfetch", content)
        self.assertNotIn("uname", content)
        self.assertNotIn("lspci", content)
        self.assertNotIn("meminfo", content)

    def test_menu_never_times_out_into_an_installation(self):
        content = GRUB_CONFIG.read_text(encoding="utf-8")
        self.assertRegex(content, r"(?m)^set timeout=-1$")
        self.assertNotRegex(content, r"(?m)^set timeout=\d+$")

    def test_entries_pass_distinct_boot_modes(self):
        content = GRUB_CONFIG.read_text(encoding="utf-8")
        self.assertIn("kerynth.mode=installer-manual", content)
        self.assertIn("kerynth.mode=installer-automatic", content)
        self.assertIn("kerynth.mode=live", content)


if __name__ == "__main__":
    unittest.main()
