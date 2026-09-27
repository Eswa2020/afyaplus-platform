def billed_attempts(base_cost: float, attempts: int) -> float:
    """Naive upper bound: every attempt hits the model."""
    return base_cost * attempts

# One triage @ $0.0004 x 5 blind retries = 5x the intended spend
print(billed_attempts(0.0004, 5))