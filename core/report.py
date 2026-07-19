import json
from pathlib import Path
from core.quote_store import load_quotes_for_job
from core.redflag import is_redflag

REPORT_DIR = Path("data")


def generate_report(job_id: str, benchmark_low: float, benchmark_high: float) -> dict:
    quotes = load_quotes_for_job(job_id)

    ranked = []
    for q in quotes:
        verdict = {"flagged": False, "reason": None}
        if q["outcome"] == "itemized_quote":
            verdict = is_redflag(q.get("total"), benchmark_low)

        entry = {
            "company_name": q["company_name"],
            "persona": q.get("persona"),
            "outcome": q["outcome"],
            "total": q.get("total"),
            "itemized": q.get("itemized"),
            "callback_time": q.get("callback_time"),
            "redflag": verdict["flagged"],
            "reason": verdict["reason"],
            "transcript_path": f"/data/transcripts/{q['conversation_id']}.json" if q.get("conversation_id") else None,
        }
        ranked.append(entry)

    def sort_key(e):
        if e["outcome"] == "itemized_quote" and not e["redflag"]:
            return (0, e["total"])
        elif e["outcome"] == "itemized_quote" and e["redflag"]:
            return (2, e["total"])
        elif e["outcome"] == "callback_commitment":
            return (1, 0)
        else:
            return (3, 0)

    ranked.sort(key=sort_key)

    non_redflag_quotes = [e for e in ranked if e["outcome"] == "itemized_quote" and not e["redflag"]]
    recommended = non_redflag_quotes[0] if non_redflag_quotes else None

    report = {
        "job_id": job_id,
        "benchmark_range": {"low": benchmark_low, "high": benchmark_high},
        "ranked_quotes": ranked,
        "recommended": recommended,
        "explanation": _explain(recommended, ranked, benchmark_low, benchmark_high),
    }

    out_path = REPORT_DIR / f"report_{job_id}.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    return report


def _explain(recommended, ranked, low, high) -> str:
    if not recommended:
        return "No safe itemized quote was collected yet — all calls ended in callback or decline."

    flags = [r for r in ranked if r["redflag"]]
    flag_note = f" {len(flags)} quote(s) were flagged as suspiciously below market and excluded." if flags else ""

    return (
        f"Recommended: {recommended['company_name']} at ${recommended['total']:.0f}, "
        f"within the ${low:.0f}-${high:.0f} market range for this move.{flag_note}"
    )