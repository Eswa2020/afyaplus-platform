# AfyaPlus Week 9 security and compliance brief

## Risks
- Partner URLs without TLS; secrets in git; override-style user text; unpinned FAQ files;
  over-scoped MCP tools; unbounded logs.

## Mitigations
- Partner traffic must be HTTPS; localhost HTTP is a written lab exception (transit_policy.py).
- .env is gitignored and absent from all git history, checked in CI (secrets_not_in_git.sh, check_gitignore.py, gitignore_evidence.txt).
- The signing key is referenced by name, never stored, and the service refuses to boot without it (secret_refs.yaml, resolve_secrets.py, boot_guard.py).
- Override-style text is refused with a 400 before any model call (injection_guard.py).
- FAQ files are pinned by hash; a silent edit fails CI (knowledge/pin.json, check_corpus_pin.py, pin_fail_notes.txt).
- Partners can only call check_stock, only for known clinics (rbac.py, test_rbac.py, allowlist_stock.py, mcp_blast_radius.json).
- Logs keep who-did-what, with identifiers redacted and payloads hashed (redact.py, redact_then_hash.py, audit_log.py).
- Chats are kept 90 days, and every sweep leaves a deletion record (retention.json, retention_sweep.py, deletion_records.jsonl).

## Kenya DPA alignment
- AfyaPlus is the controller for triage; the model vendor is a processor (dpa_who.txt).
- Triage text is treated as sensitive health-adjacent data and flagged special category (data_inventory.json, check_inventory.py).
- Each dataset has a written purpose and a not-purpose (purpose_notes.txt).
- Access requests return counts, not message content (rights_lookup.py); breach drill is contain, assess, notify within 72 hours of awareness, record (breach_path.txt).
- Open items: ODPC registration threshold (s.18) and the cross-border basis for the model host still need legal confirmation (dpa_extra_duties.md).

## What we will not claim
- We do not claim the system cannot be broken into, or that the model cannot be jailbroken; we refuse known override phrasing and log the attempt.
- We do not claim a production Key Vault: this lab uses vault_name local-env.
- We do not claim legal compliance: lawful-basis labels are teaching labels pending legal review, and the impact note is a stub.
- We do not claim redaction is complete: it is a tested net for known Kenyan ID, phone and M-Pesa formats, not a DLP product.
- AfyaPlus advises; it does not diagnose. People decide.

## Finance transfer (BenkiYetu)
- The same controls carry over to a lender: vault references, fail-closed boot, role-limited tools, redacted logs, and the data inventory (benkiyetu_transfer.md).
- One line does not move: the assistant may recommend, it never decides. Fraud hints help staff; people approve, decline or price credit.
- Credit bureau retention can run for years and may conflict with an erasure request. We document that conflict and route it to the data owner; the FAQ assistant cannot erase a bureau record and will not claim it did.