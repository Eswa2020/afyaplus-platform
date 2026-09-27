# AfyaPlus triage: scaling for the payday partner channel

**Recommendation: GO, with four conditions (below).** The service can absorb the partner
channel's payday spike at a predictable cost, provided the response cache is live first.

## What one triage answer costs
- **$0.20 per 1,000 answers** to run (AI model + servers).
- **$0.30 per 1,000** including engineer time to operate it (8 hours a month, placeholder rate).
- A normal month (2 million answers) costs **$404** to run, inside the **$450** monthly budget.

## The payday spike
The partner expects **10× normal traffic** on one payday weekend a month, which adds 1.2 million
answers (3.2 million in the month).

| Payday-spike month | Run cost | vs $450 budget |
|---|---|---|
| No cache | $646 | **Over by $196** |
| Cache answers 35% of requests | $450 | At the limit |
| Cache answers 60% of requests (lab result) | $309 | Under by $141 |

**The cache is what keeps the spike affordable.** It must answer at least 35% of requests.

## Two cost levers, built and tested
1. **Reuse identical answers (cache).** When the same question arrives again within 10 minutes,
   the stored answer is returned instead of paying the AI model again. In testing, 60 of 100
   requests were served this way, **halving the cost per answer to $0.10 per 1,000**, with no
   change to the answers themselves.
2. **Move non-urgent work overnight (batch queue).** Reports that can wait no longer compete
   with patients for capacity. Each job is paid for once, and a broken job is set aside for a
   person to review instead of blocking the rest.

**Tested and rejected:** a cheaper, shorter-answer setup cut AI cost by 65% but **changed 1 in 5
urgency decisions**, including one that downgraded a patient who should have been flagged
urgent. Not acceptable for health triage.

## Where the AI runs
Keep renting the AI model (API). Running our own GPU servers only becomes cheaper above
**8.6 million answers a month** (17 million with the cache), more than four times today's volume,
and adds round-the-clock operating risk.

## Main risk and mitigation
**Risk:** the 60% cache rate was measured on test data. If real patients rarely repeat the same
wording, the spike month could exceed the budget by up to $196.
**Mitigation:** measure the real rate on the first payday weekend. Budget alerts fire at 80% of
spend ($360) and whenever the month is forecast to exceed $450, early enough to throttle the
partner's traffic before the overrun.

## Conditions for GO
1. **Cache live** before the first partner payday weekend.
2. **Partner limits agreed:** a request rate limit, and retries only after server errors. A
   badly behaved client retrying on 5% of traffic adds 20% to the bill.
3. **Budget alerts active** at 80% of actual spend and at a 100% forecast, scoped to the
   triage service, with a named engineer on the alert.
4. **Pre-approved contingency:** a one-month budget of up to $650 if the real cache rate
   comes in below 35%, with a review before any further increase.

*Basis: AI model prices are published list prices for gpt-4o-mini; in this build the triage
model call is a placeholder, so costs are modelled, not billed. Details: `cost_model.md`,
`measurements.md`, `api_vs_selfhost.md`.*