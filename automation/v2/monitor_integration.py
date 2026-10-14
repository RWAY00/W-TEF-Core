"""Validate and hand the current run's exact output to the archival gate."""
import os
import subprocess
import sys

AUTO_COMMIT = os.path.join("automation", "v2", "auto_commit.py")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: monitor_integration.py <output-json-path>", file=sys.stderr)
        return 2
    output_path = sys.argv[1]
    mode = os.getenv("DO_COMMIT", "no")
    if mode not in ("yes", "no"):
        print("Invalid DO_COMMIT value; expected 'yes' or 'no'.", file=sys.stderr)
        return 2
    command = [sys.executable, AUTO_COMMIT, output_path, "--commit", mode]
    print(f"Archival gate mode: {'COMMIT' if mode == 'yes' else 'DRY-RUN'}")
    result = subprocess.run(command, check=False)
    if result.returncode:
        print(f"Archival gate failed with exit code {result.returncode}", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
