import importlib.util
from pathlib import Path
import socket
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
WITH_SERVER_PATHS = (
    ROOT / 'skills/custom/web/scripts/with_server.py',
    ROOT / 'skills/vendor/guanyang/webapp-testing/scripts/with_server.py',
)


def load_with_server(path):
    module_name = 'with_server_' + '_'.join(path.parts[-5:-1])
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WithServerReadinessTests(unittest.TestCase):
    def test_exited_process_is_rejected_when_foreign_listener_owns_port(self):
        with socket.socket() as foreign_listener:
            foreign_listener.bind(('localhost', 0))
            foreign_listener.listen()
            port = foreign_listener.getsockname()[1]

            process = subprocess.Popen([sys.executable, '-c', 'pass'])
            process.wait(timeout=5)

            for path in WITH_SERVER_PATHS:
                with self.subTest(path=path):
                    module = load_with_server(path)
                    with self.assertRaisesRegex(
                        RuntimeError,
                        r'Exit-Code 0',
                    ):
                        module.is_server_ready(port, process, timeout=0.1)


if __name__ == '__main__':
    unittest.main()
