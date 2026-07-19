"""
Seeds realistic demo data directly into the system's data files, bypassing
live ElevenLabs API calls. Used because we hit API quota mid-testing.
This demonstrates the full reporting/negotiation logic pipeline, which is
100% real code — only the live voice call is simulated here.

Run: python seed_demo_data.py
"""
from core.job_spec import save_job_spec
from core.quote_store import log_quote
from core.price_movement import log_price_point
from core.honesty_ledger import log_claim
from core.report import generate_report

JOB_ID = "demo_final"

print("Seeding job spec...")
save_job_spec({
    "job_id": JOB_ID,
    "vertical": "residential_moving",
    "origin": {"city": "Rock Hill", "state": "SC", "stairs": False, "elevator": False, "long_carry": False},
    "destination": {"city": "Charlotte", "state": "NC", "stairs": True, "elevator": False, "long_carry": False},
    "distance_miles": 45,
    "move_date": "2026-08-08",
    "date_flexible": True,
    "home_size": "2BR apartment",
    "large_items": ["queen bed frame", "sofa", "dresser x2", "washer/dryer"],
    "packing_service_needed": False,
    "special_notes": "third-floor walkup at destination, no elevator",
    "confirmed_by_user": True,
    "benchmark_price_range": {"low": 1158, "high": 6506, "source": "moveBuddha/FMCSA"},
})

print("Logging Company A — the Stonewaller (callback outcome)...")
log_quote(
    JOB_ID, "Carolina Movers Co", "callback_commitment",
    callback_time="Tomorrow 2:00 PM", persona="stonewaller"
)

print("Logging Company B — the Lowballer (red flag)...")
log_price_point(JOB_ID, "QuickHaul LLC", "initial_quote", 780, "")
log_quote(
    JOB_ID, "QuickHaul LLC", "itemized_quote",
    itemized={"base": 610, "fuel_surcharge": 100, "stairs_fee": 70},
    total=780, persona="lowballer"
)

print("Logging Company C — the Tough Negotiator (price moves with leverage)...")
log_price_point(JOB_ID, "Palmetto Moving", "initial_quote", 2400, "")
log_price_point(
    JOB_ID, "Palmetto Moving", "post_leverage_quote", 1850,
    "Mentioned competing $1,900 quote from another company"
)
log_quote(
    JOB_ID, "Palmetto Moving", "itemized_quote",
    itemized={"base": 1400, "fuel_surcharge": 200, "stairs_fee": 150, "insurance": 100},
    total=1850, persona="tough_negotiator"
)

print("Logging honesty claims...")
log_claim(JOB_ID, "Palmetto Moving", "third-floor walkup, no elevator", "destination.stairs", True)
log_claim(JOB_ID, "Palmetto Moving", "moving from Rock Hill to Charlotte, 45 miles", "distance_miles", True)
log_claim(JOB_ID, "Palmetto Moving", "queen bed, sofa, two dressers, washer and dryer", "large_items", True)
log_claim(JOB_ID, "QuickHaul LLC", "2 bedroom apartment, standard items", "home_size", True)
log_claim(JOB_ID, "Carolina Movers Co", "moving August 8th, flexible on date", "move_date", True)

print("Generating final report...")
report = generate_report(JOB_ID, 1158, 6506)
print("\n✅ Done.")
print("Recommendation:", report["explanation"])
print(f"\nSet JOB_ID = \"{JOB_ID}\" in web/report.html, then open:")
print("  http://localhost:8000/web/ticker.html")
print("  http://localhost:8000/web/honesty.html")
print("  http://localhost:8000/web/report.html")