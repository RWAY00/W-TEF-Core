#!/usr/bin/env python3
import json, sys, hashlib
from datetime import datetime

def make_id():
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    short = hashlib.sha1(ts.encode()).hexdigest()[:6]
    return f"WTEF-{ts}-{short}"

def create_basic_metadata(title="Untitled", author="RWAY"):
    meta = {
        "id": make_id(),
        "title": title,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "author": author,
        "tags": [],
        "source_files": [],
        "notes": ""
    }
    print(json.dumps(meta, indent=2))

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv)>1 else "New Experiment"
    create_basic_metadata(title=t)
