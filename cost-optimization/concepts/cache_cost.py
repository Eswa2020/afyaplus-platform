import hashlib

def cache_key(message: str) -> str:
    return hashlib.sha256(message.strip().lower().encode()).hexdigest()

def effective_cost(cost_per_miss: float, hit_rate: float) -> float:
    # hits ≈ free (ignore tiny Redis); misses pay the model
    return cost_per_miss * (1.0 - hit_rate)

print(round(effective_cost(0.0004, 0.35), 6))  # 35% hit rate → 65% of model spend