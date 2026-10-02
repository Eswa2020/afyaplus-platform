# Release control: CI/CD for versioned AI + MCP health

## Overview
Every behaviour-shaping artefact of the AfyaPlus triage service is versioned: the system
prompt (file per version, sha256 on `/health`), the model config, and the logistics MCP
server (`version://current`). A GitHub Actions pipeline gates every pull request and every
push to `master` in four stages: **lint + tests → golden-set eval → MCP health → deploy stub**.
Any red stage stops everything after it. The MCP health contract is a real stdio handshake:
`check_stock` must be listed and the server must report major version `1`.

## Where each deliverable lives
| Deliverable | Files |
|---|---|
| 1. Versioned prompts, config, MCP | `prompts/` + `pin.json`, `config/triage.yaml`, `logistics_mcp_versioned.py`, `release.yaml`, `prompt_app.py` (`/health`), `CHANGELOG.md` |
| 2. Pipeline YAML | `../.github/workflows/ci.yml`, `../azure-pipelines.yml` (twin) |
| 3. Eval + regression gate | `eval_prompts.py`, `evals/golden.jsonl`, `fixtures/responses/`, `eval_quarantine.py`, `quarantine_policy.md` |
| 4. MCP health in pipeline | `scripts/check_mcp_health.py`, job `mcp-health`; `deploy-staging` needs it |
| 5. Runbook + DoD | `runbook.md` (§7–8 DoD, §10 governance), `oncall_runbook_page.md`, `clinical_ops_change_brief.md` |

## Versions (release v1.2.0)
- **prompt:** 1.2.0, sha256 `28b5f129a4bd3650b5765d74681c63df803ea241a0dd749dc7c99d4b0bd4d4ff`
- **config:** `config/triage.yaml`, gpt-4o-mini, temperature 0.2, max_tokens 300
- **mcp server:** afyaplus-logistics 1.1.0 (unchanged this release; not bumped to match, see `release.yaml`)
- **image tag:** `triage-api:1.2.0` + commit-SHA tag; local build id `sha256:49b718e45de0…`
- **git tag:** `v1.2.0` · rollback target `v1.1.0`

Alignment is enforced, not remembered: `tests/test_config.py` and `tests/test_release.py`
fail CI if `pin.json`, `config/triage.yaml`, `release.yaml`, the eval step and the deploy job disagree.

## Pipeline
Actions run: **(after push)**
Required checks on `master`: `ci / lint-test`, `ci / eval`, `ci / mcp-health`.
The deploy stage builds the image, starts it, and runs `check_prompt_pin.py` against the
**running container**, so a container serving the wrong prompt fails the deploy.

## Eval gate
- **Metric:** a case passes only if the urgency label matches **and** every `must_include`
  phrase is present **and** no `must_not` phrase appears (no diagnosis or prescription language).
- **Threshold:** `eval_score >= 0.85` (on the command line in `ci.yml`, so changing it is a reviewed diff).
- **Fails closed:** no recorded fixture for the prompt's sha256 → exit 1. An unevaluated prompt cannot pass.
- **Failing runs (local):** a relabelled golden case gives `eval_score=0.67`, exit 1;
  the 1.3.0-candidate gives "No response fixture", exit 1. **Blocked PR in CI: (after push)**

## MCP health
```bash
python scripts/check_mcp_health.py   # exit 0 healthy, 1 unhealthy
```
Fails on: a missing required tool (verified by renaming `check_stock`, giving exit 1), an
unexpected major version (verified with `2.0.0`, giving exit 1), any crash, or a 30 s timeout.
Runtime counterpart: `mcp_dashboard_sketch.py` alerts at a per-tool error rate ≥ 0.10
(`mcp_alert.py`, giving `mcp_alert_notes.txt`).

## Continuous improvement
A/B: `ab_prompt_flag.py` (sticky sha256 bucket), `ab_metrics.py` (one row per request, message hashed),
`ab_report.py` giving `ab_report.json` (B = 23/100 at 20%). Shadow: `shadow_score.py` giving
`shadow_report.json` (agreement 0.67, so the candidate does **not** proceed). Pre-registered:
`experiment_card.yaml`, `prompt_opt_card.txt`, `canary_schedule.txt`. Run records: `mlflow_eval_run.py`.

## Fallbacks declared
- [x] **No retrain:** the model is vendor-hosted gpt-4o-mini; nothing is trained. No stub retrain job is claimed.
- [x] **No paid model calls:** eval scores recorded replies (`fixtures/responses/<sha>.json`), keyed on the prompt hash.
- [x] **No paid Azure:** `azure-pipelines.yml` is config-as-code; each stage mirrors a GitHub job that runs.
- [x] **No cluster:** the deploy stage is `docker build` + `docker run` on the runner, with the pin check against the container.
- [ ] Actions minutes: not needed (public repository on GitHub-hosted runners).
- [ ] Live MCP: not needed. CI launches the real server over stdio.

## Reuse of earlier artefacts
- Logistics MCP server `logistics_mcp.py` and `clinics.json`, copied and versioned as 1.1.0 (original untouched).
- Triage API and Docker tagging habits: image `triage-api:1.1.0` and git tag `v1.1.0` are the rollback target.
- Cost lens: `ab_report.json` records the candidate's +32% tokens per request as a guardrail.

## Run locally
```bash
pip install -r requirements.txt
ruff check . && pytest -q
python eval_prompts.py --threshold 0.85
python scripts/check_mcp_health.py
uvicorn prompt_app:app   # then: python check_prompt_pin.py
```

## Checklist
- [x] Tag alignment evidenced (tests + `release.yaml`)
- [x] Eval fails closed
- [x] MCP health in the pipeline, and deploy depends on it
- [x] Runbook and Definition of Done complete
- [x] Earlier artefacts reuse documented
- [ ] Green Actions run linked **(after push)**
- [ ] Blocked PR linked **(after push)**
- [ ] Branch protection screenshots in `evidence/branch_protection/` **(after push)**
- [x] No secrets committed (`.env` ignored)