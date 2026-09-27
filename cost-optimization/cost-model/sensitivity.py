"""Sensitivity of USD per 1k triage requests to prompt and completion length.

Reuses Lab 1's cost_per_1k, so prices and infra overhead can never drift
between the point estimate and the grid.
"""
from cost_model import cost_per_1k, PROMPT_TOKENS, COMPLETION_TOKENS

PROMPT_GRID = [300, 450, 900]
COMPLETION_GRID = [80, 180, 360]

# Header row, then one row per prompt length
print(f'{"prompt":>8}  ' + '  '.join(f'c={c:<5}' for c in COMPLETION_GRID))
for p in PROMPT_GRID:
    cells = '  '.join(f'{cost_per_1k(p, c):7.4f}' for c in COMPLETION_GRID)
    print(f'{p:>8}  {cells}')

base = cost_per_1k(PROMPT_TOKENS, COMPLETION_TOKENS)
print('baseline $/1k', round(base, 4))
print('double prompt 450->900 @180:', round(cost_per_1k(900, 180) - base, 4))
print('double completion 180->360 @450:', round(cost_per_1k(450, 360) - base, 4))