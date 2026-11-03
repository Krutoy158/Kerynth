import importlib.util
import json
import stat
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "kerynth-welcome-state"
SPEC = importlib.util.spec_from_loader(
    "kerynth_welcome_state",
    SourceFileLoader("kerynth_welcome_state", str(TOOL_PATH)),
)
STATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STATE)


class WelcomeStateTests(unittest.TestCase):
    def test_first_run_shows_guide_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            for mode in ("installed", "live"):
                with self.subTest(mode=mode):
                    self.assertTrue(
                        STATE.should_show(mode, state_dir=Path(directory) / mode)
                    )

    def test_installed_preference_is_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            STATE.set_show_at_startup("installed", False, state_dir=directory)
            self.assertFalse(STATE.should_show("installed", state_dir=directory))

    def test_live_and_installed_preferences_are_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            live_dir = Path(directory) / "runtime"
            config_dir = Path(directory) / "config"
            STATE.set_show_at_startup("live", False, state_dir=live_dir)
            self.assertTrue(STATE.should_show("installed", state_dir=config_dir))
            self.assertFalse(STATE.should_show("live", state_dir=live_dir))

    def test_new_live_session_shows_guide_again(self):
        with tempfile.TemporaryDirectory() as directory:
            first_session = Path(directory) / "runtime-first"
            next_session = Path(directory) / "runtime-next"
            STATE.set_show_at_startup("live", False, state_dir=first_session)
            self.assertTrue(STATE.should_show("live", state_dir=next_session))

    def test_user_can_reenable_startup_display(self):
        with tempfile.TemporaryDirectory() as directory:
            STATE.set_show_at_startup("installed", False, state_dir=directory)
            STATE.set_show_at_startup("installed", True, state_dir=directory)
            self.assertTrue(STATE.should_show("installed", state_dir=directory))

    def test_live_uses_runtime_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            expected = Path(directory) / "kerynth" / "welcome.json"
            actual = STATE.resolve_state_path(
                "live",
                environ={"XDG_RUNTIME_DIR": directory},
            )
            self.assertEqual(actual, expected)

    def test_installed_uses_config_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            expected = Path(directory) / "kerynth" / "welcome.json"
            actual = STATE.resolve_state_path(
                "installed",
                environ={"XDG_CONFIG_HOME": directory},
            )
            self.assertEqual(actual, expected)

    def test_installed_falls_back_to_home_config(self):
        with tempfile.TemporaryDirectory() as directory:
            expected = Path(directory) / ".config" / "kerynth" / "welcome.json"
            actual = STATE.resolve_state_path(
                "installed",
                environ={"HOME": directory},
            )
            self.assertEqual(actual, expected)

    def test_live_requires_runtime_directory(self):
        with self.assertRaises(STATE.WelcomeStateError):
            STATE.resolve_state_path("live", environ={})

    def test_invalid_state_defaults_to_show(self):
        with tempfile.TemporaryDirectory() as directory:
            path = STATE.resolve_state_path("installed", state_dir=directory)
            path.parent.mkdir(parents=True)
            path.write_text("{broken", encoding="utf-8")
            self.assertTrue(STATE.read_enabled(path))

    def test_unknown_schema_defaults_to_show(self):
        with tempfile.TemporaryDirectory() as directory:
            path = STATE.resolve_state_path("installed", state_dir=directory)
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps({"schema_version": 99, "show_at_startup": False}),
                encoding="utf-8",
            )
            self.assertTrue(STATE.read_enabled(path))

    def test_state_file_is_private_and_contains_only_preference(self):
        with tempfile.TemporaryDirectory() as directory:
            path = STATE.set_show_at_startup("installed", False, state_dir=directory)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"schema_version": 1, "show_at_startup": False},
            )
            self.assertEqual(list(path.parent.glob(".welcome-*.tmp")), [])

    def test_refuses_symlink_state_file(self):
        with tempfile.TemporaryDirectory() as directory:
            state_dir = Path(directory) / "state"
            state_dir.mkdir()
            outside = Path(directory) / "outside.json"
            outside.write_text("{}", encoding="utf-8")
            path = state_dir / "welcome.json"
            path.symlink_to(outside)
            self.assertTrue(STATE.read_enabled(path))
            with self.assertRaises(STATE.WelcomeStateError):
                STATE.write_enabled(path, False)
            self.assertEqual(outside.read_text(encoding="utf-8"), "{}")

    def test_rejects_invalid_mode_and_non_boolean_value(self):
        with self.assertRaises(STATE.WelcomeStateError):
            STATE.resolve_state_path("unknown", state_dir="/tmp")
        with self.assertRaises(STATE.WelcomeStateError):
            STATE.write_enabled("/tmp/welcome.json", 1)

    def test_cli_sets_and_reads_preference(self):
        with tempfile.TemporaryDirectory() as directory:
            hidden = subprocess.run(
                [
                    sys.executable,
                    str(TOOL_PATH),
                    "set",
                    "--mode",
                    "installed",
                    "--state-dir",
                    directory,
                    "--hide",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(hidden.returncode, 0, hidden.stderr)

            checked = subprocess.run(
                [
                    sys.executable,
                    str(TOOL_PATH),
                    "should-show",
                    "--mode",
                    "installed",
                    "--state-dir",
                    directory,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertEqual(checked.stdout.strip(), "hidden")


if __name__ == "__main__":
    unittest.main()
