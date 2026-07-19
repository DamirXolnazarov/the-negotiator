import json
from pathlib import Path
from datetime import datetime, timezone

LEDGER_DIR = Path("data/ledgers")
LEDGER_DIR.mkdir(parents=True, exist_ok=True)


def log_claim(job_id: str, company_name: str, claim: str, source_field: str, verified: bool):
    """
    claim: the actual sentence/fact the agent said
    source_field: which job_spec field this traces to, e.g. "destination.stairs"
    verified: True if it matches job_spec exactly, False if agent drifted
    """
    entry = {
        "job_id": job_id,
        "company_name": company_name,
        "claim": claim,
        "source_field": source_field,
        "verified": verified,
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }
    path = LEDGER_DIR / f"{job_id}_{company_name.replace(' ', '_')}_ledger.jsonl"
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def load_ledger(job_id: str, company_name: str) -> list[dict]:
    path = LEDGER_DIR / f"{job_id}_{company_name.replace(' ', '_')}_ledger.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def ledger_summary(job_id: str, company_name: str) -> dict:
    entries = load_ledger(job_id, company_name)
    total = len(entries)
    verified = sum(1 for e in entries if e["verified"])
    return {
        "total_claims": total,
        "verified_claims": verified,
        "integrity_pct": round(100 * verified / total, 1) if total else 100.0,
        "entries": entries,
    }