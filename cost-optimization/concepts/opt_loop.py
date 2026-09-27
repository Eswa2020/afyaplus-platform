def optimisation_loop(baseline: dict, change: str, after: dict) -> dict:
    """Compare $/1k and p95 before/after a single lever change."""
    return {
        'change': change,
        'delta_cost_per_1k': after['cost_per_1k'] - baseline['cost_per_1k'],
        'delta_p95_ms': after['p95_ms'] - baseline['p95_ms'],
        'keep': (after['cost_per_1k'] <= baseline['cost_per_1k']
                 and after['p95_ms'] <= baseline['p95_ms'] * 1.05),
    }

before = {'cost_per_1k': 0.2018, 'p95_ms': 2100}
later = {'cost_per_1k': 0.1310, 'p95_ms': 1980}
print(optimisation_loop(before, 'response cache on identical messages', later))