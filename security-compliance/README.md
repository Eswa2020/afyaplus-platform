# Week 9: AI Security and Compliance

## Overview
This week locks the AfyaPlus AI path built in Weeks 6–8: the JWT-protected **triage API** (Week 6), the **logistics MCP server** and its `check_stock` tool (Weeks 6–8), and the versioned prompts and CI gates from Week 8 (`release-control/`). Controls are aligned to **Kenya's Data Protection Act, 2019**, with GDPR reach recorded. The non-technical summary is [`manager_brief.md`](manager_brief.md). Every gate below runs in CI on every push (`.github/workflows/security-compliance.yml`).

All commands run from inside `security-compliance/`.

## Encryption (Deliverable 1)
- **Transit / TLS:** `transit_policy.py` refuses `http://` on non-localhost partner hosts (assertion on `http://api.afyaplus.ke/triage`); localhost HTTP is a named lab exception (`LAB_HOSTS`). `tls_handshake_ok` performs a real certificate fetch.
- **Secrets not in git:** `secrets_not_in_git.sh` + `check_gitignore.py` check `.env` at the **repo root**, search **all branches'** history, and scan the root Compose file for inlined values. Evidence of a pass, a deliberate fail and a restore: `gitignore_evidence.txt`. Correct pattern shown in `compose.secrets.yml`.
- **At rest:** `encrypt_at_rest.py` (local Fernet sketch, key from env, fails closed), `at_rest_notes.txt` (platform flags, backups included), `envelope_notes.md` (CMK wraps DEK, recognise-level).
- **Key Vault / KMS:** `secret_refs.yaml` (names only, `vault_name: local-env`), `kms_twin.json` validated by `check_kms_twin.py` (evidence incl. a deliberately blanked AWS twin: `kms_twin_evidence.txt`), `rotation_notes.txt`.
- **Fail-closed boot:** `resolve_secrets.py` and `boot_guard.py` exit 1 on unset, empty or whitespace-only `JWT_SECRET`, printing the name, never the value (`resolve_secrets_notes.txt`).

## Access control, including MCP (Deliverable 2)
- - **Authentication unchanged:** `/triage` on `secure_triage_api.py` still requires a Week 6 JWT; a request with no token returns HTTP 401 (`jwt_required_evidence.txt`).
- **Authorisation:** `rbac.py` maps `partner_clinic → {check_stock}` and `clinical_ops → {check_stock, plan_delivery_route}`; unknown roles are denied by default. `test_rbac.py` (4 pytest tests) imports the real matrix and fails if any role gains a `dump`-style tool. Summary: `least_privilege.md`.
- **Input control:** `injection_guard.py` returns a 400-shaped refusal **before** any model or tool call, with a regression test against over-blocking; `allowlist_ids.py` and `allowlist_stock.py` + `clinics_allowlist.json` refuse `clinic_id="*"` (400) and treat an empty allowlist as a config failure (500).
- **MCP blast radius:** `mcp_blast_radius.json` declares what `check_stock` returns and never returns; `mcp_tool_response_leak.json` vs `mcp_tool_response_fixed.json` shows the debug-field leak and its fix.
- **Poisoning:** `knowledge/pin.json` + `check_corpus_pin.py` fail CI on a silent FAQ edit (`pin_fail_notes.txt`).
- **Threat model:** `threat_model.json` (secret, data, config, mcp rows) gated by `check_threat_model.py`.

## Logging (Deliverable 3)
- **Writers:** `redact.py` → `logs/audit.jsonl`; `redact_then_hash.py` → `logs/audit_stacked.jsonl` (redact first, then hash the cleaned text); `audit_log.py` (hashed payload only).
- **Approach:** Bearer tokens, Kenyan 8-digit IDs, phone numbers and M-Pesa codes are redacted before write; a timestamp assertion guards against over-wide patterns.
- **Sample lines:** quoted in `redact_notes.txt`. `logs/` is gitignored at the repo root **by design**, so runtime logs never enter git history.
- No trace identifier yet; rows carry actor, action, resource and outcome.

## Kenya DPA (Deliverable 4)
- **Roles:** `dpa_who.txt` (controller, processor, subject); extra duties (ODPC registration s.18, cross-border transfer) in `dpa_extra_duties.md`.
- **Inventory:** `data_inventory.json` (triage_messages, audit_logs, mcp_stock_queries, knowledge_files, jwt_subjects), gated by `check_inventory.py`; `triage_messages` must be `special_category: true` (`inventory_evidence.txt`). Purposes and not-purposes: `purpose_notes.txt`.
- **Retention:** `retention.json` keyed on the same dataset names; `retention_sweep.py` applies a frozen 90-day clock and **appends** to `deletion_records.jsonl`, which a sweep never removes.
- **Rights:** `rights_lookup.py` returns counts (never content) for an HMAC-peppered clinic ID against the static `fixtures/subjects.json`; owners and limits in `data_subject_rights_checklist.md`.
- **Breach and impact:** `breach_path.txt` (contain, assess, notify, record; clock starts at awareness), `dpia_stub.md`, `residual_risk.txt`, `gdpr_trigger_note.md`.
- Lawful-basis values are prefixed `teaching:` and are **not** legal determinations. No regulator reference numbers are claimed.

## Manager brief (Deliverable 5)
[`manager_brief.md`](manager_brief.md) contains the four headings **Risks, Mitigations, Kenya DPA alignment, What we will not claim**, plus a finance transfer paragraph (recommend, never decide on credit; see `benkiyetu_transfer.md`). Every mitigation cites a file. `check_brief.py manager_brief.md` passes and rejects the banned overclaim word, which does not appear in the brief. Shorter companions: `manager_threat_3sent.txt`, `ciso_keys_3sent.txt`.

## Fallbacks declared
- [x] No Azure Key Vault: `vault_name: local-env` plus `kms_twin.json`; values injected via environment / GitHub Actions secret.
- [x] No AWS account: twin card completed for both columns.
- [x] Local MCP stub: `allowlist_stock.py` is a stub `check_stock` carrying the allowlist; the role matrix is in `rbac.py`. The live Week 6–8 MCP server is not modified in this folder.
- [x] Legal review pending on every `lawful_basis` and on the cross-border basis for the model host.
- [x] No model calls used to test override phrasing; the guard is tested with assertions only.
- [x] Root-level pytest collects no Weeks 6–7 tests; the Week 8 suite (9 tests) runs from `release-control/`, and Week 9 tests run from here.

## Secrets and rotation
- No secrets committed (`secrets_not_in_git.sh` passes in CI with full history).
- A CI-only `JWT_SECRET` value was displayed once during setup; it was **rotated** in GitHub Actions secrets before use. Real `.env` values were never printed or committed.

## Checklist
- [x] Secrets not in git
- [x] MCP cannot dump the environment or every clinic
- [x] The brief is readable by a non-engineer