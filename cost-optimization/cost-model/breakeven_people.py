"""Sensitivity of the break-even volume to the on-call line.

Everything here reuses breakeven.py's constants. The only quantity that
moves is on-call people time, so the difference in the answer is
attributable to people time and nothing else.
"""
from breakeven import (break_even_requests, api_per_req,
                       SELFHOST_VAR_PER_REQ, GPU_INSTANCE_MONTHLY,
                       STORAGE_OBS_MONTHLY)

fixed_honest = GPU_INSTANCE_MONTHLY + 400.0 + STORAGE_OBS_MONTHLY
fixed_free = GPU_INSTANCE_MONTHLY + 0.0 + STORAGE_OBS_MONTHLY

n_honest = break_even_requests(api_per_req, fixed_honest, SELFHOST_VAR_PER_REQ)
n_free = break_even_requests(api_per_req, fixed_free, SELFHOST_VAR_PER_REQ)
shift_pct = 100.0 * (n_honest - n_free) / n_honest

print(f'break_even_with_oncall={n_honest:.0f}')
print(f'break_even_without_oncall={n_free:.0f}')
print(f'shift={shift_pct:.1f}% lower when on-call is free')

with open('breakeven_memo.txt', 'a') as fh:
    fh.write('\nSensitivity: people cost\n')
    fh.write(f'break_even_with_oncall={n_honest:.0f}\n')
    fh.write(f'break_even_without_oncall={n_free:.0f}\n')
    fh.write(f'Setting on-call to zero cuts the break-even volume by {shift_pct:.1f}%, '
             'so self-hosting appears to pay off at a volume AfyaPlus would '
             'reach much sooner.\n')
    fh.write('The honest figure is the one to present to Finance: the on-call '
             'hours are worked either way, and a recommendation that only holds '
             'when engineering time is priced at zero is not a recommendation.\n')