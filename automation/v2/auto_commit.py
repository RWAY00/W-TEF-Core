"""Validate monitor JSON and optionally archive it on a dedicated Git branch.

Dry-run is the default. Commit mode never writes directly to main.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_ROOT = Path("automation/v2/outputs")


def validate_output(path: Path) -> dict:
    resolved = path.resolve()
    allowed_root = OUTPUT_ROOT.resolve()
    if resolved.parent != allowed_root:
        raise ValueError(f"Output must be directly inside {allowed_root}")
    if not resolved.is_file() or resolved.stat().st_size == 0:
        raise ValueError("Output file is missing or empty")
    with resolved.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError("Output JSON root must be an object")
    for field in ("generated_at", "summary", "metrics"):
        if field not in data:
            raise ValueError(f"Output JSON is missing required field: {field}")
    if not isinstance(data["metrics"], dict):
        raise ValueError("Output metrics must be a JSON object")
    return data


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def archive_output(path: Path) -> None:
    # Fail closed if this is not a clean Git checkout.
    if run_git(["diff", "--cached", "--quiet"]) != "":
        raise RuntimeError("Unexpected staged changes; refusing to archive")
    run_id = os.getenv("GITHUB_RUN_ID", "")
    suffix = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    branch = f"automation/monitor-output-{suffix}"
    run_git(["switch", "-c", branch])
    run_git(["add", "--", str(path)])
    run_git(["commit", "-m", f"archive: monitor output {path.name}"])
    run_git(["push", "--set-upstream", "origin", branch])
    remote = run_git(["ls-remote", "--heads", "origin", branch])
    if not remote:
        raise RuntimeError("Push returned but remote branch could not be verified")
    print(f"ARCHIVE_VERIFIED: {branch}:{path.as_posix()}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_path", help="Exact JSON output to validate/archive")
    parser.add_argument("--commit", choices=("yes", "no"), default=os.getenv("DO_COMMIT", "no"))
    args = parser.parse_args()
    if args.commit not in ("yes", "no"):
        print("Invalid commit mode; expected yes or no.", file=sys.stderr)
        return 2
    try:
        path = Path(args.output_path)
        validate_output(path)
        print(f"VALIDATION_PASS: {path.as_posix()}")
        if args.commit == "no":
            print("DRY_RUN_PASS: no Git writes attempted")
            return 0
        archive_output(path)
        return 0
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
