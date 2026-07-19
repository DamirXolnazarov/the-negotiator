# Troubleshooting — read before demo day, keep open during it

## Tool server dies mid-demo
Fix: `uvicorn tools.server:app --host 0.0.0.0 --port 8000` in a visible terminal.
Codespaces can idle-sleep the port forward — check it periodically before the demo.

## ElevenLabs webhook calls 404 or 422
Cause: registered tool URL doesn't match your current public Codespaces URL
(these change on restart). Fix: `curl {TOOL_SERVER_URL}/health` first — if that
fails, re-register tool URLs in the ElevenLabs dashboard (Agent -> Tools -> edit
each webhook tool's URL).

## Dashboards show nothing
1. Check browser console (F12) for CORS/404 errors.
2. Confirm TOOL_SERVER_URL is hardcoded correctly inside each HTML file's <script>.
3. `curl {TOOL_SERVER_URL}/tools/all_claims` and `/tools/all_price_movements` —
   if empty, the problem is upstream (agent isn't calling the tool).

## Agent doesn't call log_price_point / log_claim
Strengthen the system prompt with a blunt imperative: "You MUST call
log_price_point immediately after receiving ANY price, before saying anything else."

## Price never "moves" during a demo call
Live-performance risk, not code risk. Rehearse the leverage line word-for-word;
pre-agree the persona's drop amount so it's not improvised live.

## Real business call goes badly (dead air, hangup)
This is in scope — graceful friction handling is graded. Let it happen, then
narrate: "here's how the agent handles that" and show documented_decline
landing correctly in the report.

## report.html shows stale data
The report is a static snapshot. Re-run generate_report after your calls finish:
  curl -X POST "{TOOL_SERVER_URL}/tools/generate_report?job_id=YOUR_JOB_ID"
before refreshing the page.

## Fallback if ElevenLabs is rate-limited during the live demo
Have a pre-recorded successful run + screen recording of the dashboards ready as backup.

## Known unverified assumptions
- Post-call webhook payload field names were inferred, not confirmed against a
  live payload. Print the raw payload on first real call and adjust
  core/report.py's field lookups if needed.
- Webhook tool creation JSON schema in create_agents.py was inferred from the
  dashboard flow. If it 422s, create the 4 tools manually via dashboard
  (Agent -> Add Tool -> Webhook) and hardcode the resulting tool_ids.