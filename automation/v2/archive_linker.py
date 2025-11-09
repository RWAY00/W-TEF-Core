#!/usr/bin/env python3
"""
Phase-02.2 : Timeline-to-Cognitive-Archive Linker
Reads automation/v2/timeline_sync.json and appends summary rows to
WTEF_Persistent_Cognitive_Archive.csv
"""

import json, csv, os
from datetime import datetime

TIMELINE = "automation/v2/timeline_sync.json"
ARCHIVE = "WTEF_Persistent_Cognitive_Archive.csv"

def read_timeline():
    if not os.path.exists(TIMELINE):
        print("No timeline file found.")
        return []
    with open(TIMELINE,"r") as f:
        return json.load(f)

def read_existing_ids():
    if not os.path.exists(ARCHIVE):
        return set()
    with open(ARCHIVE,"r",encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {r["id"] for r in reader if "id" in r}

def append_to_archive(records):
    exists = os.path.exists(ARCHIVE)
    with open(ARCHIVE,"a",newline="",encoding="utf-8") as f:
        fieldnames = ["id","title","timestamp","author","tags","notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        for r in records:
            writer.writerow({
                "id": r.get("id"),
                "title": r.get("title"),
                "timestamp": r.get("timestamp"),
                "author": r.get("author"),
                "tags": ", ".join(r.get("tags",[])),
                "notes": r.get("notes","")
            })

def main():
    data = read_timeline()
    existing = read_existing_ids()
    new_records = [d for d in data if d["id"] not in existing]
    if not new_records:
        print("No new records to append.")
        return
    append_to_archive(new_records)
    print(f"✅ Appended {len(new_records)} new entries to {ARCHIVE}.")

if __name__ == "__main__":
    main()
