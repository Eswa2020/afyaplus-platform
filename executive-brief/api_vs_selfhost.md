# API-hosted vs self-hosted models for AfyaPlus triage

**Recommendation: stay API-hosted (gpt-4o-mini).** Self-hosting an open-source model only
becomes cheaper above **8.56 million requests a month**, more than four times today's volume,
and above **17 million** once the response cache is counted. Revisit if sustained volume passes
8 million a month or if a partner contract requires data to stay on AfyaPlus-run servers.

*No self-hosted model was run for this memo. Self-host figures are estimates, labelled as such.*

## The two options

| | API-hosted (current) | Self-hosted open-source model |
|---|---|---|
| What it is | Pay a provider per request; they run the model | Rent a GPU server and run an open model (e.g. Llama) with vLLM |
| Cost shape | Almost all per-request: $0.0002018 each | Mostly fixed: ~$1,300 a month, plus ~$0.00005 per request |
| Who operates it | The provider | AfyaPlus engineers, including nights and weekends |
| Scaling for payday spikes | Immediate, within provider quotas | Limited by GPUs already rented; more capacity takes time |
| Data location | Provider's chosen region | Wherever AfyaPlus places the server |
| Quality | Current model, known behaviour | Different model: needs its own quality testing before use |

Either way, the app's `/triage` interface stays the same: the model sits behind the
`LLM_BASE_URL` setting, so switching later is a configuration change, not a rewrite
(demonstrated in `cloud-platforms/deploy-config/endpoint_switch_notes.md`).

## Cost comparison

| Monthly volume | API-hosted | Self-hosted (estimate) | Cheaper option |
|---|---|---|---|
| 2.0M (normal month) | $403.65 | $1,400.00 | API, by $996 |
| 3.2M (payday-spike month) | $645.84 | $1,460.00 | API, by $814 |
| 20M sustained, no cache | $4,036.50 | $2,300.00 | Self-host, by $1,737 |
| 20M sustained, 60% cache | $1,930.50 | $1,700.00 | Self-host, by $231 |

**Break-even** is where the two cost lines cross: fixed cost ÷ (API cost per request −
self-host variable cost per request).
- Without caching: $1,300 ÷ ($0.0002018 − $0.00005) = **8,562,490 requests a month**.
- With a 60% cache hit rate on both paths: **16,987,912 requests a month**. The cache removes
  most of the per-request charge that self-hosting was meant to avoid.

## Why the people line decides it

The self-host fixed cost includes **$400 a month of engineer on-call time** to keep GPUs
patched, sized and running. Leave it out and break-even drops to **5.93 million**, 30.8% lower,
making self-hosting look attractive much sooner. That on-call work happens either way, so the
figure with people included is the one to use. Even the flattering 5.93M is nearly three times
today's volume, so the recommendation holds under both.

## Risks of self-hosting that the numbers do not show
- **Operations:** GPU failures, security patching and capacity planning become AfyaPlus's job,
  with patient-facing traffic depending on them around the clock.
- **Spikes:** a fixed GPU fleet cannot absorb a sudden 10× payday weekend the way an API can.
  Serving it means renting for the peak and paying for idle capacity the rest of the month.
- **Quality:** a different model gives different answers. This week's cheaper-path test changed
  4 of 20 urgency decisions, including one downgrade. Any self-hosted model would need a
  clinically labelled test set and clinician review first.
- **Security:** self-hosted logs of patient messages need encryption, access control and a
  retention policy, which the API provider currently covers contractually.

## What would change the decision
1. **Sustained volume above ~8.5M requests a month** (or above ~17M with the cache working):
   pilot self-hosting on the most repetitive, lowest-risk traffic first, and keep the API for
   spikes and everything else.
2. **A data-residency requirement** that no API provider region can meet: then self-hosting
   becomes a compliance decision, not a cost decision.
3. **A GPU price drop, or a real quote below $850 a month:** rerun `breakeven.py` with the
   quote; break-even falls in proportion.
4. **API price rises:** a higher per-request price lowers the break-even volume.

## Assumptions
- API side: $0.0002018 per request (model + 15% infra), from `cost-optimization/cost-model/cost_model.py`.
- Self-host fixed: GPU server $850 (A10-class, on-demand ballpark, not a quote), engineer
  on-call $400, storage and monitoring $50 = $1,300 a month. Variable: $0.00005 per request
  (energy and egress proxy). From `breakeven.py`.
- Cache scenario: 60% hit rate measured on a lab test set (`performance-optimization/levers/measurements.md`),
  applied to both paths; production hit rate not yet measured.
- Break-even figures: `breakeven.py`, `breakeven_people.py`, `breakeven_memo.txt`.