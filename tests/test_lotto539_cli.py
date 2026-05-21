import subprocess
import sys
import unittest


class Lotto539CliTests(unittest.TestCase):
    def test_history_command_runs_with_default_windows_console_encoding(self):
        result = subprocess.run(
            [sys.executable, "lotto539.py", "--history", "1"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("最近1期開獎紀錄", result.stdout)


if __name__ == "__main__":
    unittest.main()
