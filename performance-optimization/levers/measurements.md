# Optimisation levers: before and after

Two levers implemented and measured on fixed test sets, plus a cheaper-model check that was
measured and **not** adopted. All transcripts are saved in `evidence/`.

## Summary

| Lever | Before | After | Quality impact | Decision |
|---|---|---|---|---|
| 1. Response cache (exact match, Redis, 10-min TTL) | 100 of 100 requests billed; run cost $0.2018 per 1,000 | 40 of 100 billed (hit rate 60%); run cost $0.0965 per 1,000 [1] | None: a hit returns the exact stored answer | **Adopt** |
| 2. Batch queue for overnight summaries | Summaries would compete with patients on the live path | Separate queue; completed work never re-run; bad jobs isolated | None on answers; protects live response times | **Adopt** |
| 3. Cheaper answer path (quantization proxy) | Full answer: 1,247 tokens, $0.0158 per 1,000 [2] | Label only: 637 tokens (−49%), $0.0055 per 1,000 (−65%) | Changed 4 of 20 urgency decisions, 1 downgrade | **Do not adopt** for triage |

[1] Run cost = model + 15% infra, using `cost-optimization/cost-model/tco.py`. Cache hits skip
the model charge but still pass through the service, so infra applies to all requests.
[2] Tiny test prompts and API cost only: valid for comparing the two paths against each
other, not as AfyaPlus's unit cost (see `cost_model.md` for that).

## Lever 1: Response cache

**What it does.** Each patient message is trimmed and lowercased, then turned into a SHA-256
fingerprint used as the cache key. An identical message within 10 minutes gets the stored
answer instead of a new model call. Redis holds the cache, so several copies of the service
can share it; if Redis is unreachable, it falls back to an in-memory cache.

**Evidence.**
- `evidence/cache_miss_hit.jpg`: first call MISS, identical second call HIT.
- `evidence/cache_hitrate_redis.jpg`: screenshot of the Redis run and the hit-rate check (hit_rate 0.60, exit code 0).confirmed.
- `evidence/cache_hitrate.txt`: `backend=redis hits=60 misses=40 hit_rate=0.60`, exit code 0.
  The script exits with an error if the hit rate falls below 0.55, so it doubles as a
  regression check. Redis held exactly 40 keys afterwards, one per unique message.

**Test set.** `fixtures/triage_messages.json`: 40 unique messages; 100 requests = each
message once plus 60 random repeats (fixed seed 7). Every run starts from an empty cache.

**Limits, stated plainly.**
- 60% is a lab figure on a test set built with 60% repeats. The real hit rate depends on how
  often patients send identical wording, and is not yet measured. `cost_model.md` shows that
  the payday-spike month needs at least 34.9% to stay inside the $450 budget.
- Exact match only: "fever for 2 days" and "fever for two days" are different keys. Semantic
  (near-match) caching was deliberately not used, because two messages that look similar
  can need different urgency.
- The cache stores the answer and a fingerprint of the message, not the raw message text.
  Production use still needs a retention and access policy for health-related data.
- Response time was not measured: the model is a stub in this lab, so latency before and
  after would be meaningless. A p95 comparison needs the live model and a load script.

## Lever 2: Batch queue for non-urgent work

**What it does.** Work that can wait (for example, an overnight summary of the day's triage
themes) goes into a queue table, not the live `/triage` path. A worker processes pending jobs
in batches and marks each one done only after its summary succeeds.

**Evidence.**
- `evidence/batch_worker.txt`: first run `processed 3`, second run `processed 0`, so completed
  work is never repeated or billed twice.
- `evidence/batch_retry.txt`: 3 healthy jobs + 1 malformed job. Pass 1 completes the 3 healthy
  jobs; the malformed job fails, is retried, and becomes `dead` after 3 attempts, where a
  person can inspect it, instead of blocking the queue or disappearing.

**Trade-off.** When a batch fails, its jobs are retried one at a time so healthy work is not
lost. That costs extra calls, for the failed batch only.

**What was not measured.** The saving here is protecting live response times and billing
each job once, not a lower price per call. Some providers offer discounted batch pricing;
that has not been priced or tested for AfyaPlus.

## Lever 3: Cheaper answer path (measured, not adopted)

**What was tested.** No GPU was available, so quantization was simulated: the same model,
asked for the urgency label only with a 4-token cap, against the full path (label plus a
one-sentence reason). 20 fixed messages, 40 live `gpt-4o-mini` calls, temperature 0. The full
path's answer is the reference, so agreement means "the cheap path gave the same urgency",
not clinical correctness. Evidence: `evidence/quant_smoke.txt`, `quality_smoke.json`.

**Result.** Tokens −49%, API cost −65%, agreement 80% (16 of 20).

| Message | Full path | Cheap path | Direction |
|---|---|---|---|
| Fever for two days, drinking fluids | routine | urgent | more cautious |
| Stomach pain after eating | routine | urgent | more cautious |
| Toothache for three days | routine | urgent | more cautious |
| Low-grade fever with body aches | urgent | routine | **less cautious** |

**Decision.** Not adopted. One in five urgency decisions changed, including one downgrade,
which is the unsafe direction in triage. Any cheaper model would need a clinically labelled
test set and clinician review before use.

## Fallbacks declared
- Model: stub for the cache and batch labs (cost logic unaffected); live `gpt-4o-mini` only
  for the cheap-path check.
- Quantization: simulated with a shorter answer cap, not real INT8 weights (no GPU).
- Cache backend: Redis (local Docker container `redis:7-alpine`); in-memory fallback available.
- No load test or p95 measurement (stub model).