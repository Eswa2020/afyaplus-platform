# Memo: AfyaPlus controls to BenkiYetu

## Transfer table: the three cells left for us
| Control | AfyaPlus (health) | BenkiYetu (finance) |
|---|---|---|
| Encryption in transit | HTTPS on /triage | HTTPS on loan, wallet and FAQ APIs; same transit_policy.py rule |
| Keys | Key Vault object jwt-signing-key | Same pattern: named vault refs, fail-closed boot, KMS twin card |
| Poisoning | Pin the ORS FAQ | Pin terms, fee schedules and eligibility text; a compliance/product owner signs off, not a clinician |
| Retention against erasure | 90-day triage_messages vs an erasure request | Bureau retention can run for years and may conflict with erasure; document the conflict and route to the data owner |

## Transfers unchanged
1. Secret references plus fail-closed boot (secret_refs.yaml, resolve_secrets.py): key handling does not depend on the industry.
2. Deny-by-default roles and tests (rbac.py, test_rbac.py): only the role names change (agent, credit_ops, auditor).
3. Redact-then-hash logs (redact.py, redact_then_hash.py): Kenyan ID, phone and M-Pesa patterns matter even more for a lender.
4. Data inventory, retention sweeper and manager brief shape (data_inventory.json, retention_sweep.py, manager_brief.md).

## Must not transfer
1. Decision boundary: triage advice becomes credit *hints* only. The copilot may flag fraud patterns to the operations team; it must never approve, decline or price a loan. Humans decide credit actions.
2. Retention logic: a 90-day sweep cannot be copied onto credit data. Bureau retention rules can require years, which can contradict an erasure request; the FAQ assistant cannot erase a bureau record and must never say it did.

## Will not copy
We will not reuse clinical FAQ content, or treat "advisory urgency" bands as if they were a credit score.

Label: teaching memo; confirm the current ODPC digital-credit guidance and bureau rules before relying on it.