import json
from datetime import datetime, timezone
from pathlib import Path

QUOTE_DIR = Path("data/quotes")
QUOTE_DIR.mkdir(parents=True, exist_ok=True)


def log_quote(
    job_id: str,
    company_name: str,
    outcome: str,
    itemized: dict = None,
    total: float = None,
    callback_time: str = None,
    persona: str = None,
    conversation_id: str = None,
) -> str:
    """
    outcome: one of 'itemized_quote', 'callback_commitment', 'documented_decline'
    itemized: dict of fee_name -> amount, expected if outcome == itemized_quote
    conversation_id: the ElevenLabs conversation ID for this call, used to link
                      the quote back to its transcript
    """
    quote = {
        "job_id": job_id,
        "company_name": company_name,
        "persona": persona,
        "outcome": outcome,
        "itemized": itemized or {},
        "total": total,
        "callback_time": callback_time,
        "conversation_id": conversation_id,
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }
    quote_id = f"{job_id}_{company_name.replace(' ', '_')}_{int(datetime.now().timestamp())}"
    path = QUOTE_DIR / f"{quote_id}.json"
    with open(path, "w") as f:
        json.dump(quote, f, indent=2)
    return str(path)


def load_quotes_for_job(job_id: str) -> list[dict]:
    quotes = []
    for file in QUOTE_DIR.glob(f"{job_id}_*.json"):
        with open(file) as f:
            quotes.append(json.load(f))
    return quotes


def best_quote(job_id: str) -> dict | None:
    """Return the lowest itemized total logged so far — used as leverage in later calls."""
    quotes = [
        q for q in load_quotes_for_job(job_id)
        if q["outcome"] == "itemized_quote" and q.get("total")
    ]
    if not quotes:
        return None
    return min(quotes, key=lambda q: q["total"])