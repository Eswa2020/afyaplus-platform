"""Monthly TCO and $/1k for AfyaPlus triage, at baseline and under the payday spike.

Adds the people/ops line and the spike scenarios on top of cost_model.py.
Every assumption is a named constant below; change it here and re-run.
"""
from cost_model import (api_usd, INFRA_OVERHEAD, PROMPT_TOKENS, COMPLETION_TOKENS)

# --- Traffic assumptions ---
BASELINE_MONTHLY = 2_000_000        # [A1] planned requests per normal month
DAYS_PER_MONTH = 30
SPIKE_MULTIPLIER = 10               # [A2] partner channel on payday weekends
SPIKE_DAYS = 2                      # [A3] one payday weekend per month

# --- People / ops (API-hosted path) ---
OPS_HOURS_PER_MONTH = 8             # [A4] on-call, prompt and cost reviews, key rotation
OPS_RATE_USD_PER_HOUR = 25.0        # [A5] loaded engineer cost, placeholder to confirm

# --- Cache hit-rate scenarios ---
HIT_RATES = [0.0, 0.30, 0.60]       # [A6] 0.60 measured on fixtures; 0.30 conservative guess

BUDGET_CAP = 450.0                  # from cloud-platforms/deploy-config budgets

api_per_req = api_usd(PROMPT_TOKENS, COMPLETION_TOKENS)
infra_per_req = api_per_req * INFRA_OVERHEAD
people_monthly = OPS_HOURS_PER_MONTH * OPS_RATE_USD_PER_HOUR

daily = BASELINE_MONTHLY / DAYS_PER_MONTH
spike_month = int(BASELINE_MONTHLY + daily * (SPIKE_MULTIPLIER - 1) * SPIKE_DAYS)
sustained_10x = BASELINE_MONTHLY * SPIKE_MULTIPLIER

scenarios = [
    ('baseline month', BASELINE_MONTHLY),
    ('payday-spike month', spike_month),
    ('sustained 10x month', sustained_10x),
]


def monthly(volume, hit_rate):
    """Cache hits skip the model call but still pass through the service (infra)."""
    api = volume * (1 - hit_rate) * api_per_req
    infra = volume * infra_per_req
    return api, infra


print(f'unit: api={api_per_req:.7f} infra={infra_per_req:.7f} USD per request')
print(f'people/ops: {people_monthly:.2f} USD per month '
      f'({OPS_HOURS_PER_MONTH} h x {OPS_RATE_USD_PER_HOUR:.0f} USD)')
print()
print(f'{"scenario":<22}{"requests":>12}{"hit":>6}{"api+infra":>11}'
      f'{"TCO":>9}{"$/1k run":>10}{"$/1k TCO":>10}  budget')
for name, vol in scenarios:
    for h in HIT_RATES:
        api, infra = monthly(vol, h)
        run = api + infra
        tco = run + people_monthly
        flag = 'OVER' if run > BUDGET_CAP else 'ok'
        print(f'{name:<22}{vol:>12,}{h:>6.0%}{run:>11.2f}{tco:>9.2f}'
              f'{1000 * run / vol:>10.4f}{1000 * tco / vol:>10.4f}  {flag}')

# Hit rate needed to keep the payday-spike month inside the budget cap
needed = 1 - (BUDGET_CAP / spike_month - infra_per_req) / api_per_req
print()
print(f'payday-spike month needs a cache hit rate of at least {needed:.1%} '
      f'to stay under the {BUDGET_CAP:.0f} USD cap')