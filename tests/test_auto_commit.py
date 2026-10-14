"""Unit tests for the W-TEF output validation and dry-run contract."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

MODULE_PATH = Path(__file__).resolve().parents[1] / "automation" / "v2" / "auto_commit.py"
SPEC = importlib.util.spec_from_file_location("wtef_auto_commit", MODULE_PATH)
auto_commit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(auto_commit)


class AutoCommitContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_cwd = os.getcwd()
        os.chdir(self.temp.name)
        self.output_dir = Path("automation/v2/outputs")
        self.output_dir.mkdir(parents=True)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp.cleanup()

    def write_output(self, name="monitor-test.json", data=None, raw=None):
        path = self.output_dir / name
        if raw is not None:
            path.write_text(raw, encoding="utf-8")
        else:
            payload = data if data is not None else {
                "generated_at": "2026-10-14T00:00:00+00:00",
                "summary": "test snapshot",
                "metrics": {"state": "test"},
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_valid_output_passes(self):
        path = self.write_output()
        self.assertIn("metrics", auto_commit.validate_output(path))

    def test_missing_required_field_fails(self):
        path = self.write_output(data={"summary": "missing fields", "metrics": {}})
        with self.assertRaises(ValueError):
            auto_commit.validate_output(path)

    def test_invalid_json_fails(self):
        path = self.write_output(raw="{invalid")
        with self.assertRaises(json.JSONDecodeError):
            auto_commit.validate_output(path)

    def test_output_outside_canonical_directory_fails(self):
        outside = Path("automation/v2/not-output.json")
        outside.write_text(json.dumps({
            "generated_at": "x", "summary": "x", "metrics": {}
        }), encoding="utf-8")
        with self.assertRaises(ValueError):
            auto_commit.validate_output(outside)

    def test_dry_run_validates_without_git_writes(self):
        path = self.write_output()
        with mock.patch("sys.argv", ["auto_commit.py", str(path), "--commit", "no"]), \
             mock.patch.object(auto_commit, "run_git", side_effect=AssertionError("git must not run")):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = auto_commit.main()
        self.assertEqual(code, 0)
        self.assertIn("DRY_RUN_PASS", stdout.getvalue())

    def test_missing_file_fails(self):
        with self.assertRaises(ValueError):
            auto_commit.validate_output(self.output_dir / "missing.json")


if __name__ == "__main__":
    unittest.main()
