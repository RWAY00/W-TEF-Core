#!/usr/bin/env python3
"""
auto_commit.py (Phase-02.1)
Usage:
  python automation/v2/auto_commit.py /path/to/local/file1.json /path/to/local/file2.txt
This will upload files to repo under automation/v2/ artifacts path,
and optionally update timeline_sync.json when you pass --meta '{"title":"..."}'
"""

import os, base64, json, requests, hashlib, sys
from datetime import datetime

GITHUB_OWNER = "RWAY00"
GITHUB_REPO = "W-TEF-Core"
API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents"
TOKEN = os.getenv("WTEF_PAT")
BRANCH = os.getenv("WTEF_BRANCH","main")

if not TOKEN:
    raise SystemExit("WTEF_PAT environment variable missing. Set it before running.")

headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

def make_experiment_id():
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    short = hashlib.sha1(ts.encode()).hexdigest()[:6]
    return f"WTEF-{ts}-{short}"

def get_file_sha(path):
    url = f"{API}/{path}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get("sha")
    return None

def upload_bytes(path, content_bytes, message):
    sha = get_file_sha(path)
    payload = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode(),
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha
    url = f"{API}/{path}"
    r = requests.put(url, headers=headers, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()

def upload_file_local(local_path, remote_dir="automation/v2/artifacts"):
    if not os.path.exists(local_path):
        raise FileNotFoundError(local_path)
    b = open(local_path,"rb").read()
    fname = os.path.basename(local_path)
    remote_path = f"{remote_dir}/{fname}"
    msg = f"Auto: upload {remote_path}"
    res = upload_bytes(remote_path, b, msg)
    return res.get("content",{}).get("path")

def fetch_timeline():
    url = f"{API}/automation/v2/timeline_sync.json"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get("content")
    return None

def get_timeline_json():
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/automation/v2/timeline_sync.json"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        payload = r.json()
        content = base64.b64decode(payload["content"]).decode()
        sha = payload["sha"]
        return json.loads(content), sha
    return [], None

def update_timeline(metadata_obj):
    arr, sha = get_timeline_json()
    arr.append(metadata_obj)
    arr = sorted(arr, key=lambda x: x.get("timestamp",""))
    new_content = json.dumps(arr, indent=2).encode()
    payload = {
        "message": f"Auto: update timeline {metadata_obj.get('id')}",
        "content": base64.b64encode(new_content).decode(),
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha
    url = f"{API}/automation/v2/timeline_sync.json"
    r = requests.put(url, headers=headers, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()

def make_run_metadata(exp_id, title="Auto Run", files=None, notes=""):
    return {
        "id": exp_id,
        "title": title,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "author": "auto",
        "tags": ["autosync"],
        "source_files": files or [],
        "notes": notes
    }

def main():
    args = sys.argv[1:]
    if not args:
        # legacy behavior: create a simple run log
        exp_id = make_experiment_id()
        path = f"automation/v2/logs/runs/{exp_id}.json"
        run_log = make_run_metadata(exp_id, title="Auto heartbeat", files=[])
        res = upload_bytes(path, json.dumps(run_log, indent=2).encode(), f"Auto: add run log {exp_id}")
        print("Uploaded run log:", res.get("content",{}).get("path"))
        return

    # If files provided, upload them and update timeline
    local_files = []
    meta = {}
    for a in args:
        if a.startswith("--meta="):
            try:
                meta = json.loads(a.split("=",1)[1])
            except:
                meta = {}
            continue
        local_files.append(a)

    exp_id = make_experiment_id()
    uploaded = []
    for lf in local_files:
        p = upload_file_local(lf)
        uploaded.append(p)
        print("Uploaded:", p)

    metadata = make_run_metadata(exp_id,
                                 title=meta.get("title","Auto experiment"),
                                 files=uploaded,
                                 notes=meta.get("notes",""))
    update_timeline(metadata)
    # also create run log
    run_path = f"automation/v2/logs/runs/{exp_id}.json"
    upload_bytes(run_path, json.dumps(metadata, indent=2).encode(), f"Auto: add run log {exp_id}")
    print("Completed run:", exp_id)

if __name__ == "__main__":
    main()
