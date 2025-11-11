# auto_commit.py
import os
if os.getenv("DO_COMMIT", "no") != "yes":
    print("Commit disabled (dry run).")
    exit(0)

GITHUB_OWNER = "RWAY00"
GITHUB_REPO = "W-TEF-Core"
API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents"
TOKEN = os.getenv("WTEF_PAT")  # put as GitHub secret

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

def upload_file(path, content_bytes, message):
    sha = get_file_sha(path)
    payload = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode(),
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha
    url = f"{API}/{path}"
    r = requests.put(url, headers=headers, data=json.dumps(payload))
    r.raise_for_status()
    return r.json()

def main():
    exp_id = make_experiment_id()
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Example: create a small run log
    run_log = {
        "id": exp_id,
        "timestamp": timestamp,
        "note": "Auto sync run",
        "files": ["WTEF_Daily_Log.json"]
    }
    path = f"automation/v2/logs/runs/{exp_id}.json"
    content = json.dumps(run_log, indent=2).encode()
    res = upload_file(path, content, f"Auto: add run log {exp_id}")
    print("Uploaded:", res.get("content", {}).get("path"))

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("WTEF_PAT environment variable missing.")
    main()
