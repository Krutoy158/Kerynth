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
            ROOT / "initramfs" / "kerynth-boot-mode",
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

    def test_live_mounts_explicit_iso_uuid_and_squashfs_read_only(self):
        content = (ROOT / 'initramfs' / 'init').read_text(encoding='utf-8')
        self.assertIn('kerynth.media=*', content)
        self.assertIn('mount -o ro "$MEDIA_DEVICE" /media', content)
        self.assertIn('mount -t squashfs -o loop,ro /media/live/rootfs.squashfs /newroot', content)
        self.assertIn('mount --move /media /newroot/run/kerynth-media', content)


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
                self.assertIn("kerynth.media=UUID=$kerynth_media_uuid", match.group(1))
                self.assertIn("probe --set=kerynth_media_uuid --fs-uuid ($root)", match.group(1))
                self.assertIn("initrd /boot/initramfs.cpio.gz", match.group(1))


class BootModeParserTests(unittest.TestCase):
    def setUp(self):
        self.shell = shutil.which("sh")
        self.parser = ROOT / "initramfs" / "kerynth-boot-mode"

    def run_parser(self, cmdline):
        return subprocess.run(
            [self.shell, str(self.parser), cmdline],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_parser_has_valid_shell_syntax(self):
        result = subprocess.run(
            [self.shell, "-n", str(self.parser)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_parser_accepts_all_three_boot_modes(self):
        modes = (
            "installer-manual",
            "installer-automatic",
            "live",
            "installed",
        )
        for mode in modes:
            with self.subTest(mode=mode):
                result = self.run_parser(f"quiet root=UUID=abc kerynth.mode={mode}")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, f"{mode}\n")

    def test_installed_mode_is_not_an_extra_boot_menu_choice(self):
        result = self.run_parser("quiet kerynth.mode=installed")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "installed\n")

    def test_parser_rejects_missing_unknown_and_duplicate_modes(self):
        invalid_cmdlines = (
            "quiet root=/dev/sda1",
            "kerynth.mode=desktop",
            "kerynth.mode=live kerynth.mode=live",
            "kerynth.mode=live kerynth.mode=installer-manual",
        )
        for cmdline in invalid_cmdlines:
            with self.subTest(cmdline=cmdline):
                result = self.run_parser(cmdline)
                self.assertNotEqual(result.returncode, 0)

    def test_parser_rejects_shell_metacharacters_in_mode(self):
        result = self.run_parser("kerynth.mode=live;touch /tmp/kerynth-mode-test")
        self.assertNotEqual(result.returncode, 0)

    def test_init_publishes_mode_only_under_volatile_run(self):
        content = (ROOT / "initramfs" / "init").read_text(encoding="utf-8")
        self.assertIn('/lib/kerynth-boot-mode "$CMDLINE"', content)
        self.assertIn('mount -t tmpfs -o mode=755,nosuid,nodev tmpfs /newroot/run', content)
        self.assertIn('/newroot/run/kerynth/boot-mode', content)

    def test_proc_is_mounted_before_kernel_command_line_is_read(self):
        content = (ROOT / "initramfs" / "init").read_text(encoding="utf-8")
        self.assertLess(
            content.index("$BB mount -t proc proc /proc"),
            content.index('cat /proc/cmdline'),
        )
        self.assertEqual(content.count("$BB mount -t proc proc /proc"), 1)



if __name__ == "__main__":
    unittest.main()
