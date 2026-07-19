import json
from pathlib import Path
from datetime import datetime, timezone

MOVEMENT_DIR = Path("data/price_movements")
MOVEMENT_DIR.mkdir(parents=True, exist_ok=True)


def log_price_point(job_id: str, company_name: str, stage: str, amount: float, note: str = ""):
    """
    stage: 'initial_quote' or 'post_leverage_quote'
    """
    entry = {
        "job_id": job_id,
        "company_name": company_name,
        "stage": stage,
        "amount": amount,
        "note": note,
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }
    path = MOVEMENT_DIR / f"{job_id}_{company_name.replace(' ', '_')}_movement.json"

    existing = []
    if path.exists():
        with open(path) as f:
            existing = json.load(f)
    existing.append(entry)

    with open(path, "w") as f:
        json.dump(existing, f, indent=2)


def get_movement(job_id: str, company_name: str) -> dict | None:
    path = MOVEMENT_DIR / f"{job_id}_{company_name.replace(' ', '_')}_movement.json"
    if not path.exists():
        return None
    with open(path) as f:
        points = json.load(f)

    initial = next((p for p in points if p["stage"] == "initial_quote"), None)
    post = next((p for p in points if p["stage"] == "post_leverage_quote"), None)

    if not initial or not post:
        return None

    delta = initial["amount"] - post["amount"]
    return {
        "company_name": company_name,
        "initial": initial["amount"],
        "after_leverage": post["amount"],
        "saved": round(delta, 2),
        "saved_pct": round(100 * delta / initial["amount"], 1) if initial["amount"] else 0,
        "note": post.get("note", ""),
    }