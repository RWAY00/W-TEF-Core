# ============ Phase-02.1 Auto-Output Integration ============
import os, json
from datetime import datetime

OUT_DIR = "automation/v2/outputs"
os.makedirs(OUT_DIR, exist_ok=True)

# Output JSON filename with timestamp
timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
output_file = os.path.join(OUT_DIR, f"monitor_{timestamp}.json")

# Example monitor summary data (you can replace with real metrics)
data = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "summary": "Daily stability snapshot",
    "metrics": {
        "cognitive_load": 0.87,
        "system_state": "stable",
        "entropy": 0.032
    }
}

# Save monitor output
with open(output_file, "w") as f:
    json.dump(data, f, indent=2)
print(f"🧩 Monitor output written: {output_file}")

# Trigger auto-upload
os.system("python automation/v2/monitor_integration.py")
# ============================================================
