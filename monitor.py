"""Generate a local W-TEF monitor snapshot and pass that exact file onward."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

OUT_DIR = os.path.join("automation", "v2", "outputs")


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    output_file = os.path.join(OUT_DIR, f"monitor_{timestamp}.json")
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": "Daily stability snapshot",
        "classification": "ILLUSTRATIVE_PLACEHOLDER",
        "metrics": {
            "cognitive_load": 0.87,
            "system_state": "stable",
            "entropy": 0.032,
        },
    }
    with open(output_file, "w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")
    print(f"Monitor output written: {output_file}")

    result = subprocess.run(
        [sys.executable, os.path.join("automation", "v2", "monitor_integration.py"), output_file],
        check=False,
    )
    if result.returncode:
        print(f"Monitor integration failed with exit code {result.returncode}", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
