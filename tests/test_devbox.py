import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]


class DevboxTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.directory = Path(self.scratch.name)
        self.log = self.directory / "commands.jsonl"
        self.env = {
            **{key: value for key, value in os.environ.items() if not key.startswith("DEVBOX_")},
            "PATH": f"{self.directory}:{os.environ['PATH']}",
            "COMMAND_LOG": str(self.log),
            "DEVBOX_IP": "dev.example.test",
            "DEVBOX_USERNAME": "ted",
        }
        for name in ("ssh", "mosh", "mosh-client", "brew", "uname"):
            command = self.directory / name
            command.write_text(
                f"#!{sys.executable}\n"
                "import json, os, sys\n"
                "from pathlib import Path\n"
                "name = Path(sys.argv[0]).name\n"
                "with open(os.environ['COMMAND_LOG'], 'a') as log:\n"
                "    log.write(json.dumps([name, *sys.argv[1:]]) + '\\n')\n"
                "if name == 'uname':\n"
                "    print(os.environ.get('MOCK_OS', 'Darwin'))\n"
                "if name in ('mosh', 'mosh-client'):\n"
                "    if os.environ.get('MOCK_MOSH_STATUS', '0') != '0':\n"
                "        print('dyld: Library not loaded: libabsl_die_if_null.2601.0.0.dylib', file=sys.stderr)\n"
                "    sys.exit(int(os.environ.get('MOCK_MOSH_STATUS', '0')))\n"
                "if name == 'brew' and sys.argv[1] == os.environ.get('MOCK_BREW_FAIL'):\n"
                "    sys.exit(1)\n"
            )
            command.chmod(0o755)

    def run_script(self, name, *args, **env):
        return subprocess.run(
            ["/bin/bash", str(REPO / "bin" / name), *args],
            env={**self.env, **env}, capture_output=True, text=True, timeout=10,
        )

    def commands(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_broken_mosh_does_not_reap_remote_sessions(self):
        result = self.run_script("devbox", MOCK_MOSH_STATUS="134")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("devbox-repair", result.stderr)
        self.assertNotIn("ssh", [command[0] for command in self.commands()])
        self.assertNotIn("mosh", [command[0] for command in self.commands()])

    def test_healthy_mosh_keeps_connection_arguments(self):
        result = self.run_script("devbox", "echo", "hello world",
                                 DEVBOX_PORT="2222", DEVBOX_MOSH_PORT="60001")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.commands()[0], ["mosh-client", "--version"])
        self.assertEqual(self.commands()[-1], [
            "mosh", "--ssh=ssh -p 2222", "-p", "60001",
            "ted@dev.example.test", "echo", "hello world",
        ])

    def test_missing_mosh_does_not_contact_remote(self):
        (self.directory / "mosh").unlink()
        result = self.run_script("devbox", PATH=str(self.directory))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("devbox-repair", result.stderr)
        self.assertEqual(self.commands(), [])

    def test_missing_host_cannot_contact_remote(self):
        result = self.run_script("devbox", DEVBOX_IP="")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.commands(), [])

    def test_repair_reinstalls_dependencies_and_checks_linkage(self):
        result = self.run_script("devbox-repair")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.commands(), [
            ["uname", "-s"],
            ["brew", "update"],
            ["brew", "reinstall", "abseil", "protobuf", "mosh"],
            ["brew", "linkage", "--test", "abseil", "protobuf", "mosh"],
            ["mosh-client", "--version"],
        ])

    def test_failed_reinstall_does_not_claim_success(self):
        result = self.run_script("devbox-repair", MOCK_BREW_FAIL="reinstall")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Mosh is ready", result.stdout)
        self.assertNotIn("mosh-client", [command[0] for command in self.commands()])

    def test_failed_health_check_does_not_claim_success(self):
        result = self.run_script("devbox-repair", MOCK_MOSH_STATUS="134")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Mosh is ready", result.stdout)

    def test_failed_linkage_check_does_not_claim_success(self):
        result = self.run_script("devbox-repair", MOCK_BREW_FAIL="linkage")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Mosh is ready", result.stdout)

    def test_repair_refuses_linux_before_modifying_packages(self):
        result = self.run_script("devbox-repair", MOCK_OS="Linux")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("macOS", result.stderr)
        self.assertEqual(self.commands(), [["uname", "-s"]])


if __name__ == "__main__":
    unittest.main()
