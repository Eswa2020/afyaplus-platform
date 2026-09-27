"""Monthly cost of a blind-retry partner client vs a sane retry policy.

Unit cost comes from Lab 1's cost_model, so this script can never
disagree with the baseline $/1k.
"""
from cost_model import fully_loaded_usd, PROMPT_TOKENS, COMPLETION_TOKENS

MONTHLY_REQ = 2_000_000
STORM_FRACTION = 0.05        # share of requests caught in a retry loop
EXTRA_ATTEMPTS_STORM = 4     # avg extra billed calls: retries 429/timeouts, no backoff
EXTRA_ATTEMPTS_SANE = 0.2    # rare 503/timeout retries only, max 2, honours Retry-After

unit = fully_loaded_usd(PROMPT_TOKENS, COMPLETION_TOKENS)
baseline = MONTHLY_REQ * unit
storm = baseline + MONTHLY_REQ * STORM_FRACTION * EXTRA_ATTEMPTS_STORM * unit
sane = baseline + MONTHLY_REQ * STORM_FRACTION * EXTRA_ATTEMPTS_SANE * unit

lines = [
    f'unit_usd={unit:.6f}',
    f'baseline_monthly={baseline:.2f}',
    f'storm_monthly={storm:.2f}',
    f'sane_monthly={sane:.2f}',
    f'storm_amplification={storm / baseline:.3f}',
]

with open('retry_storm_notes.txt', 'w') as fh:
    fh.write('\n'.join(lines) + '\n')

print('\n'.join(lines))