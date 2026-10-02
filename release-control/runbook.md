# LLMOps Runbook: AfyaPlus triage + logistics MCP

Audience: whoever is on call. Every step is a command or a file. No step says "investigate".

## 1. What is live (one release = one rollback decision)
`release.yaml` names the release. Current: **v1.2.0**

| Component | Version | Proof at runtime |
|---|---|---|
| Triage prompt | 1.2.0, sha256 `28b5f129…d4d4ff` | `GET /health` → `prompt_version`, `prompt_sha256` |
| Config | `config/triage.yaml` (gpt-4o-mini, temp 0.2, 300 tokens) | reviewed diff only, never a portal |
| Logistics MCP | afyaplus-logistics 1.1.0 | MCP resource `version://current` |
| Image | `triage-api:1.2.0` (+ commit-SHA tag) | CI job `deploy-staging`, last step prints the image id |

Previous release: **v1.1.0** (Week 7). Tests (`tests/test_config.py`, `tests/test_release.py`)
fail CI if `pin.json`, `config/triage.yaml`, `release.yaml` and `ci.yml` ever disagree.

## 2. Where to look
| Question | Where |
|---|---|
| Which prompt is serving? | `curl http://<host>:8000/health` |
| Did the gates pass for this commit? | GitHub → Actions → run → jobs `ci / lint-test`, `ci / eval`, `ci / mcp-health`, `deploy-staging` |
| Eval score and threshold | `eval` job log line `eval_score=… threshold=0.85 prompt_sha256=…` |
| MCP tools alive at deploy time? | `mcp-health` job log line `tools [...] version 1.1.0` |
| MCP tool errors at runtime | `python mcp_dashboard_sketch.py` (per-tool `error_rate`, alert at 0.10) |
| MCP call history | `logs/mcp_activity.jsonl` (arguments hashed, never stored) |
| MCP server messages | server stderr: CI job log or `docker logs <container>` |
| A/B assignment per request | `logs/ab_requests.jsonl` (variant, version, latency, message hash) |
| Params beside score | MLflow experiment `afyaplus-triage` (`mlflow ui --backend-store-uri sqlite:///<abs path>/mlflow.db`) |

**Known gap:** the `release-control` stub app does not emit a `trace_id`. Week 6's
`secure_triage_api.py` does; when the stub is wired to it, start incidents from that id
(see `oncall_runbook_page.md`). Until then, start from `/health` and the CI run for the deployed commit.

## 3. Roll back (rehearsed; target under 5 minutes)
Same image, previous prompt pointer, then **verify**. Setting a variable is not proof.

```bash
# 1. Point at the last known-good prompt (same image; no rebuild)
export PROMPT_VERSION=1.2.0          # PowerShell: $env:PROMPT_VERSION="1.2.0"
# 2. Restart the service so it re-reads the pin (a running process keeps the old prompt)
# 3. Verify against the committed pin: must print "prompt pin OK" and exit 0
python check_prompt_pin.py --url http://<host>:8000/health
# 4. Re-run the gate before closing the incident
python eval_prompts.py --threshold 0.85
```

Whole-release rollback: deploy image `triage-api:1.1.0` / git tag `v1.1.0`, then steps 3–4.
Rehearsal evidence: `prompt_pin_notes.txt` (candidate → exit 1; back to 1.2.0 → exit 0).

## 4. Roll forward (a new prompt version)
1. Add a **new** file `prompts/triage_system_vX.Y.Z.txt`. Never edit a pinned file.
2. Fill in `prompt_opt_card.txt` and `experiment_card.yaml` **before** any results.
3. Record replies for the new sha256 in `fixtures/responses/<sha>.json` (no fixture = gate exits 1).
4. Bump `pin.json`, `config/triage.yaml`, `ci.yml` `PROMPT_VERSION`, `release.yaml` together
   (the tests refuse a partial bump). Add a `CHANGELOG.md` line.
5. Open a PR → CODEOWNERS review → all four CI jobs green.
6. Shadow first (`shadow_score.py`), then canary per `canary_schedule.txt`. Never skip the golden eval.
7. Tag `vX.Y.Z` only after 100% holds for 24 h.

## 5. Thresholds (change only by PR)
| Gate | Value | File |
|---|---|---|
| Golden eval | `eval_score >= 0.85` | `ci.yml` `--threshold 0.85` |
| Quarantine ceiling | `<= 5%` of golden set | `eval_quarantine.py` `MAX_QUAR_RATE` |
| Tool error alert | `error_rate >= 0.10` | `mcp_dashboard_sketch.py` `ALERT_THRESHOLD` |
| MCP contract | `check_stock` present, version `1.x` | `scripts/check_mcp_health.py` |

## 6. Who reviews what
`.github/CODEOWNERS` routes `prompts/`, `evals/`, `fixtures/` and `.github/workflows/` to the owner.
Clinical-adjacent wording (anything shaping urgency, escalation or refusal) needs a named
**clinical_ops** reviewer before production. Solo-repo exception: see `branch_protection_checklist.md`.

## 7. Definition of Done: prompt PR
- [ ] New versioned file in `prompts/`; no pinned file edited in place
- [ ] `pin.json`, `config/triage.yaml`, `release.yaml`, `ci.yml` bumped together (tests green)
- [ ] Fixture recorded for the new sha256; `ci / eval` green at 0.85
- [ ] Experiment card and prompt-optimisation card committed **before** results
- [ ] Shadow run scored; canary plan follows `canary_schedule.txt`
- [ ] clinical_ops review recorded on the PR (clinical-adjacent wording)
- [ ] Previous release tag still deployable; rollback command in the PR description
- [ ] Variant + prompt_version logged on every request
- [ ] `CHANGELOG.md` updated

## 8. Definition of Done: MCP PR
- [ ] Semver bump is honest: additive → MINOR, rename/remove required field → MAJOR
- [ ] `MCP_VERSION` and `version://current` updated; `release.yaml` matches (test green)
- [ ] `ci / mcp-health` green (required tools present, expected major)
- [ ] Breaking change: `[Unreleased] Breaking` entry + migration window **before** release
- [ ] `CHANGELOG.md` updated

## 9. Sprint board (two-week sprint, prompt work beside code)
| Ticket | Type | Done evidence |
|---|---|---|
| P-12 prompt 1.3.0-candidate | Prompt PR | fixture for sha `2231005e…`, eval green, clinical_ops approval |
| E-04 grow golden set to ≥ 20 cases | Eval fixture | `evals/golden.jsonl`; unlocks quarantine (see policy) |
| M-08 MCP health in CI | Pipeline | `ci / mcp-health` green; renamed tool → exit 1 |
| R-02 rollback drill | Runbook | §3 executed, `check_prompt_pin.py` exit 0 recorded |

## 10. Governance: the system recommends, humans decide
AfyaPlus recommends **advisory urgency bands** and logistics next steps. Clinicians, patients
and clinic operators **decide** care and fulfilment. Engineering owns pipelines, eval gates and
rollback; clinical partners own patient decisions. Prompts must not diagnose or prescribe.
This is enforced twice: automatically by `must_not` checks in `evals/golden.jsonl`, and by a
human clinical_ops reviewer reading the actual wording before release.