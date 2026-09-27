# AfyaPlus triage: cost model and cost per 1,000 requests

**Headline:** a triage request costs **$0.2018 per 1,000** to run (model + infrastructure).
Including a people/ops line, fully loaded TCO is **$0.3018 per 1,000** in a normal month.
The partner channel's payday spike pushes the month to **$645.84** of run cost, which breaks
the $450 budget unless the response cache serves at least **34.9%** of requests.

All figures are reproducible: `python cost_model.py`, `python sensitivity.py`,
`python retry_storm_cost.py`, `python tco.py` (saved output: `tco_output.txt`).

## 1. Unit cost: one triage request

| Line | Calculation | USD per request |
|---|---|---|
| Prompt tokens [P1][T1] | 450 × $0.15 / 1M | 0.0000675 |
| Completion tokens [P2][T1] | 180 × $0.60 / 1M | 0.0001080 |
| **Model (API) cost** | | **0.0001755** |
| Infrastructure [I1] | 15% of model cost | 0.0000263 |
| **Run cost per request** | | **0.0002018** |
| **Run cost per 1,000 requests** | | **$0.2018** |

Completion tokens are 38% of the tokens but 62% of the model cost, because they are priced
4× higher. The sensitivity grid (`sensitivity.py`) confirms it: doubling answer length adds
$0.1242 per 1,000, while doubling prompt length adds only $0.0776. Capping answer length is
the stronger lever.

## 2. Total cost of ownership: monthly lines

| TCO line | Normal month (2.0M requests) | Source |
|---|---|---|
| Model (API) | $351.00 | Section 1 × volume |
| Infrastructure | $52.65 | [I1] |
| People / ops | $200.00 | [A4][A5] |
| **TCO** | **$603.65** | |
| **TCO per 1,000 requests** | **$0.3018** | |
| Incident risk (not in base) | +$80.73 in a retry-storm month | [R1] |

**Incidents.** `retry_storm_cost.py` models a partner client retrying blindly on 5% of traffic
(4 extra billed calls each): the monthly run cost rises from $403.65 to $484.38, **+20%**.
A sane retry policy (retry only on 503/timeout, honour Retry-After) adds just $4.04. This is
kept out of the base and treated as a risk the rate limits and spend breaker must prevent.

## 3. The 10× spike

**Assumption [A2][A3]:** the partner channel brings 10× normal daily traffic for one payday
weekend (2 days) a month. That adds 1.2M requests, making a **3.2M-request month**.
A sustained 10× month (20M requests) is shown as a stress case.

| Scenario | Requests | Cache hit rate | Run cost | TCO | Run $/1k | TCO $/1k | vs $450 budget |
|---|---|---|---|---|---|---|---|
| Normal month | 2.0M | 0% | $403.65 | $603.65 | 0.2018 | 0.3018 | ok |
| Normal month | 2.0M | 30% | $298.35 | $498.35 | 0.1492 | 0.2492 | ok |
| Normal month | 2.0M | 60% | $193.05 | $393.05 | 0.0965 | 0.1965 | ok |
| **Payday-spike month** | 3.2M | 0% | **$645.84** | $845.84 | 0.2018 | 0.2643 | **over** |
| Payday-spike month | 3.2M | 30% | $477.36 | $677.36 | 0.1492 | 0.2117 | over |
| Payday-spike month | 3.2M | 60% | $308.88 | $508.88 | 0.0965 | 0.1590 | ok |
| Sustained 10× (stress) | 20.0M | 0% | $4,036.50 | $4,236.50 | 0.2018 | 0.2118 | over |

How to read it:
- **Run cost per 1,000 does not change with volume.** Model and infra scale linearly, so 10×
  traffic means 10× the bill for those lines. Only caching lowers the unit cost.
- **TCO per 1,000 falls as volume grows,** because the fixed $200 people line is spread
  over more requests ($0.10 per 1,000 at 2M, $0.01 at 20M).
- **The spike breaks the budget without caching.** The cache must serve at least **34.9%** of
  requests for the spike month to stay under $450. The lab measured 60% on a fixed test set
  of repeated messages [A6]; the real hit rate on production traffic is not yet known.

## 4. Assumptions and rates

- **[P1][P2]** gpt-4o-mini list prices used in the course: $0.15 per 1M prompt tokens,
  $0.60 per 1M completion tokens. Verify at https://openai.com/api/pricing before any board use.
- **[T1]** Typical triage shape: 450 prompt tokens (system prompt + patient message),
  180 completion tokens (advice + disclaimer). Course baseline; to be replaced with measured
  averages from usage logs.
- **[I1]** Infrastructure overhead 15% of model cost (compute, logs, egress, TLS). A teaching
  default, not AfyaPlus accounting.
- **[A1]** 2,000,000 requests in a normal month (course planning figure).
- **[A2][A3]** Payday spike: 10× daily volume for 2 days a month.
- **[A4][A5]** People/ops on the API path: 8 engineer-hours a month (on-call, prompt and cost
  reviews, key rotation) at $25/hour loaded. **Placeholder, to be confirmed with Finance.**
- **[A6]** Cache hit rates: 60% measured on 100 requests with 60 exact repeats
  (`performance-optimization/levers/cache_hitrate.py`); 30% is a conservative scenario.
- **[R1]** Retry storm: 5% of 2M requests, 4 extra billed calls each (`retry_storm_notes.txt`).
- Budget cap $450: `cloud-platforms/deploy-config/budget_alert_notes.md`.