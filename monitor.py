# monitor.py
# Small W-TEF stability monitor helper (test log creator)
# Writes WTEF_Daily_Log.json with a timestamp and a short test note.

import datetime
import json
import os
import sys

ARCHIVE_CSV = "WTEF_Persistent_Cognitive_Archive.csv"
OUT_JSON = "WTEF_Daily_Log.json"

def make_row(missing=False):
    if not missing:
        return {
            "timestamp_utc": datetime.datetime.utcnow().isoformat(),
            "status": "ok",
            "note": "archive-present"
        }
    else:
        return {
            "timestamp_utc": datetime.datetime.utcnow().isoformat(),
            "status": "test",
            "note": "archive-missing-test"
        }

def main():
    archive_exists = os.path.exists(ARCHIVE_CSV)
    row = make_row(missing=not archive_exists)
    try:
        with open(OUT_JSON, "w") as f:
            json.dump(row, f)
        print(f"Created {OUT_JSON} ->", row)
    except Exception as e:
        print("ERROR writing log:", e, file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
