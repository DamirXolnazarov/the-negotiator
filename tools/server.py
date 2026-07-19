"""
FastAPI server exposing tool functions as HTTP endpoints ElevenLabs agents call
mid-conversation. Also serves data/ and web/ statically so dashboards can fetch data.

Run with: uvicorn tools.server:app --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from datetime import datetime, timezone
import json as json_lib

from core.job_spec import save_job_spec, latest_job_spec
from core.quote_store import log_quote, best_quote
from core.price_movement import log_price_point, get_movement
from core.honesty_ledger import log_claim

app = FastAPI(title="The Negotiator - Tool Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("data").mkdir(exist_ok=True)
Path("web").mkdir(exist_ok=True)
Path("data/transcripts").mkdir(exist_ok=True, parents=True)

app.mount("/data", StaticFiles(directory="data"), name="data")
app.mount("/web", StaticFiles(directory="web", html=True), name="web")


# ---------- Job spec ----------

class JobSpecPayload(BaseModel):
    job_id: Optional[str] = None
    vertical: str = "residential_moving"
    origin: dict
    destination: dict
    distance_miles: float
    move_date: str
    date_flexible: bool = True
    home_size: str
    large_items: list[str] = []
    packing_service_needed: bool = False
    special_notes: str = ""
    benchmark_price_range: Optional[dict] = None


@app.post("/tools/save_job_spec")
def api_save_job_spec(payload: JobSpecPayload):
    path = save_job_spec(payload.model_dump())
    return {"status": "saved", "path": path}


@app.get("/tools/latest_job_spec")
def api_latest_job_spec():
    try:
        return latest_job_spec()
    except FileNotFoundError:
        return {"status": "none_yet"}


# ---------- Quotes ----------

class LogQuotePayload(BaseModel):
    job_id: str
    company_name: str
    outcome: str
    itemized: dict = {}
    total: Optional[float] = None
    callback_time: Optional[str] = None
    persona: Optional[str] = None
    conversation_id: Optional[str] = None


@app.post("/tools/log_quote")
def api_log_quote(payload: LogQuotePayload):
    path = log_quote(
        job_id=payload.job_id,
        company_name=payload.company_name,
        outcome=payload.outcome,
        itemized=payload.itemized,
        total=payload.total,
        callback_time=payload.callback_time,
        persona=payload.persona,
        conversation_id=payload.conversation_id,
    )
    return {"status": "logged", "path": path}


@app.get("/tools/get_best_quote")
def api_get_best_quote(job_id: str):
    q = best_quote(job_id)
    if not q:
        return {"has_quote": False}
    return {"has_quote": True, "company_name": q["company_name"], "total": q["total"]}


# ---------- Price movement ----------

class PricePointPayload(BaseModel):
    job_id: str
    company_name: str
    stage: str
    amount: float
    note: str = ""


@app.post("/tools/log_price_point")
def api_log_price_point(payload: PricePointPayload):
    log_price_point(payload.job_id, payload.company_name, payload.stage, payload.amount, payload.note)
    return {"status": "logged"}


@app.get("/tools/get_movement")
def api_get_movement(job_id: str, company_name: str):
    m = get_movement(job_id, company_name)
    return m or {"status": "no_movement_yet"}


@app.get("/tools/all_price_movements")
def api_all_price_movements():
    movements = []
    for f in Path("data/price_movements").glob("*.json"):
        with open(f) as file:
            movements.append({"file": f.stem, "points": json_lib.load(file)})
    return {"movements": movements}


# ---------- Honesty ledger ----------

class ClaimPayload(BaseModel):
    job_id: str
    company_name: str
    claim: str
    source_field: str
    verified: bool


@app.post("/tools/log_claim")
def api_log_claim(payload: ClaimPayload):
    log_claim(payload.job_id, payload.company_name, payload.claim, payload.source_field, payload.verified)
    return {"status": "logged"}


@app.get("/tools/all_claims")
def api_all_claims():
    all_claims = []
    for f in Path("data/ledgers").glob("*.jsonl"):
        with open(f) as file:
            for line in file:
                if line.strip():
                    all_claims.append(json_lib.loads(line))
    all_claims.sort(key=lambda c: c["logged_at"])
    return {"claims": all_claims}


# ---------- Report generation ----------

@app.post("/tools/generate_report")
def api_generate_report(job_id: str):
    from core.report import generate_report
    from core.job_spec import load_job_spec
    from core.config import load_config

    spec = load_job_spec(job_id)
    cfg = load_config("moving")

    benchmark = spec.get("benchmark_price_range", {})
    low = benchmark.get("low", cfg["benchmark"]["default_low"])
    high = benchmark.get("high", cfg["benchmark"]["default_high"])

    report = generate_report(job_id, low, high)
    return report


# ---------- Transcript webhook ----------

@app.post("/webhooks/post_call")
async def post_call_webhook(request: dict):
    """Register in ElevenLabs dashboard: Agent -> Post-call webhooks."""
    conversation_id = request.get("conversation_id", f"unknown_{int(datetime.now().timestamp())}")
    path = Path("data/transcripts") / f"{conversation_id}.json"
    with open(path, "w") as f:
        json_lib.dump(request, f, indent=2)
    print(f"Transcript saved: {path}")
    return {"status": "received", "saved_to": str(path)}


@app.get("/tools/get_transcript")
def api_get_transcript(conversation_id: str):
    path = Path("data/transcripts") / f"{conversation_id}.json"
    if not path.exists():
        return {"status": "not_found"}
    with open(path) as f:
        return json_lib.load(f)


@app.get("/health")
def health():
    return {"status": "ok"}