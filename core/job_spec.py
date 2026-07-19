import json
import os
from datetime import datetime, timezone
from pathlib import Path

JOB_SPEC_DIR = Path("data/job_specs")
JOB_SPEC_DIR.mkdir(parents=True, exist_ok=True)


def save_job_spec(spec: dict) -> str:
    """Save a confirmed job spec to disk, return its path."""
    spec.setdefault("confirmed_by_user", True)
    spec.setdefault("confirmed_at", datetime.now(timezone.utc).isoformat())
    job_id = spec.get("job_id") or f"move_{int(datetime.now().timestamp())}"
    spec["job_id"] = job_id

    path = JOB_SPEC_DIR / f"{job_id}.json"
    with open(path, "w") as f:
        json.dump(spec, f, indent=2)
    return str(path)


def load_job_spec(job_id: str) -> dict:
    path = JOB_SPEC_DIR / f"{job_id}.json"
    with open(path) as f:
        return json.load(f)


def latest_job_spec() -> dict:
    """Convenience: grab the most recently saved job spec."""
    files = sorted(JOB_SPEC_DIR.glob("*.json"), key=os.path.getmtime)
    if not files:
        raise FileNotFoundError("No job specs saved yet. Run intake first.")
    with open(files[-1]) as f:
        return json.load(f)