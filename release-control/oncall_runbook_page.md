# Incident template + worked drill: 2026-10-02-a (rehearsal)

## Start (in this order: identifier first, theory last)
1. Get the identifier: `trace_id` from the Week 6 API response/log, or, for the stub app,
   the commit SHA of the running image (`deploy-staging` log).
2. Read `/health`: `prompt_version`, `prompt_sha256`.
3. Run `python check_prompt_pin.py --url http://<host>:8000/health`.
4. Run `python mcp_dashboard_sketch.py` and read `logs/mcp_activity.jsonl` for that window.

## What we saw (drill)
- `/health`: prompt_version=1.3.0-candidate, sha256=2231005e…
- `check_prompt_pin.py`: PROMPT PIN MISMATCH, exit 1 (pin expects 1.2.0 / 28b5f129…)
- `mcp_alert.py` drill: check_stock error_rate=0.12 → ALERT (threshold 0.10); ping 0.00

## Action
Rolled back: PROMPT_VERSION=1.2.0, restart, `check_prompt_pin.py` → prompt pin OK, exit 0.
Re-ran `eval_prompts.py` → eval_score=1.00, exit 0.

## Close
- clinical_ops notified that the candidate never served patients.
- Evidence: `prompt_pin_notes.txt`, `mcp_alert_notes.txt`.
- Follow-up ticket: P-12 (candidate needs a recorded fixture + shadow pass before canary).