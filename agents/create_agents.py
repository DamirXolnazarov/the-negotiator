"""
Creates the intake and caller agents on ElevenLabs (ElevenAgents platform) via
API, and registers our FastAPI tool server as webhook tools.

IMPORTANT: Start tools/server.py first and get its public URL (Codespaces
"Ports" tab -> port 8000 -> Public). Set TOOL_SERVER_URL in .env to that URL.

If tool creation 422s, create the tools manually via the ElevenLabs dashboard
(Agent -> Add Tool -> Webhook) using the field values below, then hardcode
the resulting tool_ids into create_agent() calls.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["ELEVENLABS_API_KEY"]
TOOL_SERVER_URL = os.environ.get("TOOL_SERVER_URL", "http://localhost:8000")
BASE_URL = "https://api.elevenlabs.io/v1/convai"

HEADERS = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json",
}


def read_prompt(path: str) -> str:
    with open(path) as f:
        return f.read()

def create_tool(name: str, description: str, method: str, path: str, properties: dict = None, required: list = None):
    payload = {
        "tool_config": {
            "type": "webhook",
            "name": name,
            "description": description,
            "api_schema": {
                "url": f"{TOOL_SERVER_URL}{path}",
                "method": method,
            },
        }
    }
    if properties:
        payload["tool_config"]["api_schema"]["request_body_schema"] = {
            "type": "object",
            "properties": properties,
            "required": required or list(properties.keys()),
        }

    resp = requests.post(f"{BASE_URL}/tools", headers=HEADERS, json=payload)
    if resp.status_code != 200:
        print(f"\n❌ ERROR creating tool '{name}':")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}\n")
    resp.raise_for_status()
    tool = resp.json()
    print(f"Tool created: {name} -> {tool.get('tool_id') or tool.get('id')}")
    return tool

def create_agent(name: str, prompt_path: str, first_message: str, tool_ids: list[str], voice_id: str):
    prompt = read_prompt(prompt_path)
    payload = {
        "name": name,
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": prompt,
                    "tool_ids": tool_ids,
                },
                "first_message": first_message,
                "language": "en",
            },
            "tts": {"voice_id": voice_id},
        },
    }
    resp = requests.post(f"{BASE_URL}/agents/create", headers=HEADERS, json=payload)
    if resp.status_code != 200:
        print(f"\n❌ ERROR creating agent '{name}':")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}\n")
    resp.raise_for_status()
    agent = resp.json()
    print(f"Agent created: {name} -> {agent['agent_id']}")
    return agent

if __name__ == "__main__":
    address_schema = {
        "type": "object",
        "description": "Address details including access conditions",
        "properties": {
            "city": {"type": "string", "description": "City name"},
            "state": {"type": "string", "description": "State abbreviation, e.g. SC"},
            "stairs": {"type": "boolean", "description": "Whether there are stairs at this location"},
            "elevator": {"type": "boolean", "description": "Whether there is an elevator"},
            "long_carry": {"type": "boolean", "description": "Whether there's a long carry from truck to door"},
        },
        "required": ["city", "state"],
    }

    save_spec_tool = create_tool(
        name="save_job_spec",
        description="Save the confirmed structured job specification once the user has confirmed all details.",
        method="POST",
        path="/tools/save_job_spec",
        properties={
            "origin": address_schema,
            "destination": address_schema,
            "distance_miles": {"type": "number", "description": "Distance in miles"},
            "move_date": {"type": "string", "description": "Move date in YYYY-MM-DD format. MUST use year 2026 or later."},
            "home_size": {"type": "string", "description": "e.g. 2BR apartment"},
            "large_items": {
                "type": "array",
                "description": "List of large/unusual items",
                "items": {"type": "string", "description": "Name of one large item"}
            },
        },
        required=["origin", "destination", "distance_miles", "move_date", "home_size"],
    )
    log_quote_tool = create_tool(
        name="log_quote",
        description="Log the structured outcome of a call: itemized quote, callback commitment, or decline.",
        method="POST",
        path="/tools/log_quote",
        properties={
            "job_id": {"type": "string", "description": "The job spec ID this call is for"},
            "company_name": {"type": "string", "description": "Name of the moving company called"},
            "outcome": {"type": "string", "description": "One of: itemized_quote, callback_commitment, documented_decline"},
            "itemized": {"type": "object", "description": "Fee breakdown as key-value pairs, e.g. base, fuel, stairs"},
            "total": {"type": "number", "description": "Total quoted price"},
            "persona": {"type": "string", "description": "Which negotiation persona answered"},
            "conversation_id": {"type": "string", "description": "This call's conversation ID"},
        },
        required=["job_id", "company_name", "outcome"],
    )

    price_point_tool = create_tool(
        name="log_price_point",
        description="Log a price checkpoint — 'initial_quote' before leverage, 'post_leverage_quote' after.",
        method="POST",
        path="/tools/log_price_point",
        properties={
            "job_id": {"type": "string", "description": "The job spec ID"},
            "company_name": {"type": "string", "description": "Company being called"},
            "stage": {"type": "string", "description": "'initial_quote' or 'post_leverage_quote'"},
            "amount": {"type": "number", "description": "The quoted total at this stage"},
            "note": {"type": "string", "description": "What leverage was used, if any"},
        },
        required=["job_id", "company_name", "stage", "amount"],
    )

    claim_tool = create_tool(
        name="log_claim",
        description="Log a factual claim stated about the job, for honesty verification.",
        method="POST",
        path="/tools/log_claim",
        properties={
            "job_id": {"type": "string", "description": "The job spec ID"},
            "company_name": {"type": "string", "description": "Company being called"},
            "claim": {"type": "string", "description": "The exact fact stated"},
            "source_field": {"type": "string", "description": "Which job_spec field this traces to"},
            "verified": {"type": "boolean", "description": "True if it matches the confirmed job spec exactly"},
        },
        required=["job_id", "company_name", "claim", "source_field", "verified"],
    )

   
    
    def tid(t):
        return t.get("tool_id") or t.get("id")

    intake_agent = create_agent(
        name="negotiator-intake-agent",
        prompt_path="agents/prompts/intake_system_prompt.txt",
        first_message="Hi! I'm here to help gather the details for your move. Let's start — what city are you moving from?",
        tool_ids=[tid(save_spec_tool)],
        voice_id="21m00Tcm4TlvDq8ikWAM",
    )

    caller_agent = create_agent(
        name="negotiator-caller-agent",
        prompt_path="agents/prompts/caller_system_prompt.txt",
        first_message="Hi, I'm calling to get a moving quote — do you have a moment?",
        tool_ids=[tid(log_quote_tool), tid(price_point_tool), tid(claim_tool)],
        voice_id="21m00Tcm4TlvDq8ikWAM",
    )

    with open("data/agent_ids.json", "w") as f:
        json.dump({
            "intake_agent_id": intake_agent["agent_id"],
            "caller_agent_id": caller_agent["agent_id"],
        }, f, indent=2)

    print("\nDone. Agent IDs saved to data/agent_ids.json")
    print("Test agents live at: https://elevenlabs.io/app/agents")