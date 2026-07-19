# The Negotiator

Voice-agent MVP that intakes a moving job by voice, calls the market to gather
itemized quotes, negotiates using leverage from competing bids, and reports
back a ranked, evidence-cited recommendation.

Built for Hack-Nation × ElevenLabs — "The Negotiator" challenge.

## Quick start

```bash
./setup.sh
uvicorn tools.server:app --host 0.0.0.0 --port 8000
# make port 8000 public (Codespaces "Ports" tab), copy URL into .env as TOOL_SERVER_URL
python agents/create_agents.py
python run_demo.py
```

## Live demo pages
- `{TOOL_SERVER_URL}/web/intake_widget.html` — talk to the intake agent
- `{TOOL_SERVER_URL}/web/ticker.html` — live price-movement dashboard
- `{TOOL_SERVER_URL}/web/honesty.html` — honesty polygraph
- `{TOOL_SERVER_URL}/web/report.html` — final verdict report

## Vertical config
`config/moving.yaml` is the active vertical. `config/auto_repair.yaml` is a
stub proving the system generalizes via config, not code changes.

## Docs
See TROUBLESHOOTING.md if something breaks on demo day.