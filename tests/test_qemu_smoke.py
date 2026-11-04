import importlib.util
import socket
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "kerynth-qemu-smoke"
SPEC = importlib.util.spec_from_loader(
    "kerynth_qemu_smoke_test",
    SourceFileLoader("kerynth_qemu_smoke_test", str(TOOL)),
)
SMOKE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SMOKE)


class RunningProcess:
    def poll(self):
        return None


class QemuSmokeTests(unittest.TestCase):
    def test_wait_socket_accepts_path_objects(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "qemu-monitor.sock"
            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            server.bind(str(path))
            server.listen(1)
            try:
                client = SMOKE.wait_socket(path, RunningProcess(), 1)
                self.assertIsInstance(client, socket.socket)
                client.close()
            finally:
                server.close()


if __name__ == "__main__":
    unittest.main()
