import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STARTUP = ROOT / "tools" / "kerynth-welcome-startup"
AUTOSTART = ROOT / "desktop" / "autostart" / "kerynth-welcome.desktop"


class WelcomeStartupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.mode_file = self.root / "boot-mode"
        self.state_log = self.root / "state.log"
        self.app_log = self.root / "app.log"

        state_tool = self.bin / "kerynth-welcome-state"
        state_tool.write_text(
            '#!/bin/sh\nprintf "%s\\n" "$*" >> "$STATE_LOG"\nprintf "%s\\n" "$STATE_RESULT"\n',
            encoding="utf-8",
        )
        state_tool.chmod(0o755)

        welcome_app = self.bin / "kerynth-welcome"
        welcome_app.write_text(
            '#!/bin/sh\nprintf "%s\\n" "$*" >> "$APP_LOG"\n',
            encoding="utf-8",
        )
        welcome_app.chmod(0o755)

    def tearDown(self):
        self.temp.cleanup()

    def run_startup(self, mode=None, state_result="show", include_app=True):
        if mode is None:
            self.mode_file.unlink(missing_ok=True)
        else:
            self.mode_file.write_text(mode + "\n", encoding="utf-8")

        environment = os.environ.copy()
        environment.update(
            {
                "PATH": str(self.bin) + os.pathsep + environment.get("PATH", ""),
                "KERYNTH_BOOT_MODE_FILE": str(self.mode_file),
                "STATE_LOG": str(self.state_log),
                "APP_LOG": str(self.app_log),
                "STATE_RESULT": state_result,
            }
        )
        if not include_app:
            (self.bin / "kerynth-welcome").unlink()

        return subprocess.run(
            [shutil.which("sh"), str(STARTUP)],
            capture_output=True,
            text=True,
            env=environment,
            check=False,
        )

    def test_startup_script_has_valid_shell_syntax(self):
        result = subprocess.run(
            [shutil.which("sh"), "-n", str(STARTUP)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_installed_mode_uses_persistent_preference_scope(self):
        result = self.run_startup("installed")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.state_log.read_text(encoding="utf-8").strip(),
            "should-show --mode installed",
        )
        self.assertEqual(self.app_log.read_text(encoding="utf-8").strip(), "--startup")

    def test_live_mode_uses_volatile_preference_scope(self):
        result = self.run_startup("live")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.state_log.read_text(encoding="utf-8").strip(),
            "should-show --mode live",
        )
        self.assertEqual(self.app_log.read_text(encoding="utf-8").strip(), "--startup")

    def test_hidden_preference_does_not_start_the_guide(self):
        result = self.run_startup("installed", state_result="hidden")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.state_log.is_file())
        self.assertFalse(self.app_log.exists())

    def test_unknown_or_missing_boot_mode_is_a_no_op(self):
        for mode in (None, "installer-manual", "unknown"):
            with self.subTest(mode=mode):
                self.state_log.unlink(missing_ok=True)
                self.app_log.unlink(missing_ok=True)
                result = self.run_startup(mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(self.state_log.exists())
                self.assertFalse(self.app_log.exists())

    def test_missing_graphical_application_is_a_no_op(self):
        result = self.run_startup("installed", include_app=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.state_log.exists())
        self.assertFalse(self.app_log.exists())

    def test_autostart_desktop_entry_uses_dispatcher(self):
        content = AUTOSTART.read_text(encoding="utf-8")
        self.assertIn("Type=Application", content)
        self.assertIn("Exec=kerynth-welcome-startup", content)
        self.assertIn("NoDisplay=true", content)


if __name__ == "__main__":
    unittest.main()
