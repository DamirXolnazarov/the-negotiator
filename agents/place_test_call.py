"""
Places an outbound call from the caller agent to a real phone number via
ElevenLabs' Twilio-native integration. Optional — only needed if you want
the agent to call a real phone during the demo instead of testing in-dashboard.

Requires a phone number imported in the ElevenLabs dashboard first
(Phone Numbers section), with its ID set as ELEVENLABS_PHONE_NUMBER_ID in .env.
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["ELEVENLABS_API_KEY"]
BASE_URL = "https://api.elevenlabs.io/v1/convai"

HEADERS = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json",
}


def place_call(agent_id: str, agent_phone_number_id: str, to_number: str, job_id: str):
    payload = {
        "agent_id": agent_id,
        "agent_phone_number_id": agent_phone_number_id,
        "to_number": to_number,
        "conversation_initiation_client_data": {
            "dynamic_variables": {"job_id": job_id}
        }
    }
    resp = requests.post(f"{BASE_URL}/twilio/outbound-call", headers=HEADERS, json=payload)
    resp.raise_for_status()
    result = resp.json()
    print("Call placed:", json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python agents/place_test_call.py <to_number> <persona_label> <job_id>")
        sys.exit(1)

    to_number, persona, job_id = sys.argv[1], sys.argv[2], sys.argv[3]

    with open("data/agent_ids.json") as f:
        agent_ids = json.load(f)

    phone_number_id = os.environ.get("ELEVENLABS_PHONE_NUMBER_ID")
    if not phone_number_id:
        print("Set ELEVENLABS_PHONE_NUMBER_ID in .env first.")
        sys.exit(1)

    print(f"Placing call to {to_number}, persona={persona}, job_id={job_id}...")
    place_call(agent_ids["caller_agent_id"], phone_number_id, to_number, job_id)