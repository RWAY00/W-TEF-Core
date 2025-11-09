#!/usr/bin/env python3
"""
monitor_integration.py
Phase-02.1
Links monitor outputs to GitHub auto-commit system.
"""

import os, glob, subprocess, json
from datetime import datetime

OUT_DIR = "automation/v2/outputs"
AUTO_COMMIT = "python automation/v2/auto_commit.py"

def find_latest_output():
    files = sorted(glob.glob(os.path.join(OUT_DIR, "*.json")),
                   key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def main():
    latest = find_latest_output()
    if not latest:
        print("No monitor output found in", OUT_DIR)
        return

    meta = {
        "title": "Monitor Output Sync",
        "notes": "Auto-uploaded from monitor integration",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    cmd = f'{AUTO_COMMIT} "{latest}" --meta=\'{json.dumps(meta)}\''
    print("▶ Running:", cmd)
    result = subprocess.run(cmd, shell=True)
    if result.returncode == 0:
        print("✅ Monitor integration complete.")
    else:
        print("❌ Auto-commit failed with code:", result.returncode)

if __name__ == "__main__":
    main()
