# Impact assessment stub (teaching)

## System
AfyaPlus triage plus the logistics MCP server

## Risks
- A patient's health-adjacent message is exposed through logs, backups or a support bundle.
- A partner clinic, or an attacker with a partner token, extracts other clinics' stock or patients' data.
- A poisoned or wrong FAQ leads a patient to delay care.
- Triage text is reused beyond its purpose, e.g. for model training or third-party analytics.
- Prompts containing personal data leave Kenya via a foreign model host without a transfer basis.

## Mitigations
- Redact then hash before any log write (redact.py, redact_then_hash.py, audit_log.py); 90-day retention with deletion records (retention_sweep.py).
- Deny-by-default role matrix and clinic allowlist (rbac.py, test_rbac.py, allowlist_stock.py); minimal tool responses (mcp_blast_radius.json).
- Corpus pinned in CI (knowledge/pin.json, check_corpus_pin.py); override text refused before the model (injection_guard.py).
- Purpose and not_purpose written per dataset (purpose_notes.txt, data_inventory.json).
- Transfer flagged as a separate duty (dpa_extra_duties.md).

## Residual
- Redaction patterns are a coarse net, not a DLP product; novel identifier formats may survive.
- A pinned FAQ can still be wrong; clinical human review remains required.
- Cross-border transfer basis for the model host is not yet confirmed by legal.

Label: teaching stub, not a lawyer-signed assessment.