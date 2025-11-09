# Colab/ Python cell — upload local JSON to your repo via GitHub API
import os, base64, json, requests, sys, glob
from datetime import datetime

# required: WTEF_PAT must already be set in os.environ
PAT = os.environ.get("WTEF_PAT")
if not PAT:
    raise SystemExit("WTEF_PAT missing in environment. Set it first.")

OWNER = "RWAY00"
REPO = "W-TEF-Core"
BRANCH = "main"   

API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"

# find the test file(s) you created
files = sorted(glob.glob("automation/v2/outputs/test_monitor_*.json"))
if not files:
    raise SystemExit("No test_monitor_*.json found in automation/v2/outputs. Create one first.")

fn = files[-1]   # latest
print("Uploading local file:", fn)

with open(fn, "rb") as f:
    content_bytes = f.read()

remote_path = f"automation/v2/artifacts/{os.path.basename(fn)}"  # where to store in repo
message = f"Auto-upload test {os.path.basename(fn)}"
b64 = base64.b64encode(content_bytes).decode()

# check if file already exists to get sha
headers = {"Authorization": f"token {PAT}", "Accept": "application/vnd.github.v3+json"}
get_url = f"{API_BASE}/{remote_path}"
r = requests.get(get_url, headers=headers)
payload = {
    "message": message,
    "content": b64,
    "branch": BRANCH
}
if r.status_code == 200:
    sha = r.json().get("sha")
    payload["sha"] = sha
    print("Existing file found in repo (will update).")
elif r.status_code == 404:
    print("New file (will create).")
else:
    print("Warning: GET returned", r.status_code, r.text[:300])

# do the PUT
put_url = get_url
resp = requests.put(put_url, headers=headers, data=json.dumps(payload), timeout=30)
if resp.status_code in (200,201):
    print("Success! Uploaded to:", resp.json()["content"]["path"])
    print("Commit:", resp.json()["commit"]["sha"])
else:
    print("Upload failed:", resp.status_code)
    print(resp.text)
