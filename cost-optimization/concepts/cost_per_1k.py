def cost_per_1k(total_usd: float, successful_requests: int) -> float:
    if successful_requests <= 0:
        raise ValueError('need successful request count')
    return 1000.0 * total_usd / successful_requests

# Example: $42.00 API spend across 100_000 triage calls
print(round(cost_per_1k(42.0, 100_000), 4))  # -> 0.42 USD per 1k