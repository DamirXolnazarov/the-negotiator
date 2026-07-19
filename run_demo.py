"""
Demo-day convenience script. Checks system health, seeds a sample job_spec,
and prints URLs to open for the live demo.
"""
import requests
import sys

TOOL_SERVER_URL = "http://localhost:8000"


def check_server():
    try:
        r = requests.get(f"{TOOL_SERVER_URL}/health", timeout=3)
        return r.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def seed_sample_job_spec():
    sample = {
        "job_id": "demo_rockhill_charlotte",
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
        "benchmark_price_range": {"low": 1158, "high": 6506, "source": "moveBuddha/FMCSA"},
        "confirmed_by_user": True,
    }
    resp = requests.post(f"{TOOL_SERVER_URL}/tools/save_job_spec", json=sample)
    print("Seeded sample job_spec:", resp.json())
    return sample["job_id"]


if __name__ == "__main__":
    print("=== The Negotiator — Demo Checklist ===\n")

    if not check_server():
        print("❌ Tool server not running. Start it first:")
        print("   uvicorn tools.server:app --host 0.0.0.0 --port 8000\n")
        sys.exit(1)
    print("✅ Tool server is up.\n")

    seed = input("Seed sample job_spec for a dry run? [y/N] ").strip().lower()
    job_id = "demo_rockhill_charlotte"
    if seed == "y":
        job_id = seed_sample_job_spec()

    print(f"\n📋 job_id for this demo: {job_id}")
    print("\nOpen these URLs (use your public Codespaces port URL):")
    print(f"  Intake Widget:     {TOOL_SERVER_URL}/web/intake_widget.html")
    print(f"  Live Ticker:       {TOOL_SERVER_URL}/web/ticker.html")
    print(f"  Honesty Polygraph: {TOOL_SERVER_URL}/web/honesty.html")
    print(f"  Verdict Report:    {TOOL_SERVER_URL}/web/report.html")
    print(f"\nSet JOB_ID = \"{job_id}\" inside report.html's <script> before opening it.")
    print("\nAfter calls are logged, generate the report:")
    print(f'  curl -X POST "{TOOL_SERVER_URL}/tools/generate_report?job_id={job_id}"')