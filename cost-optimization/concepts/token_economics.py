# Documented ballpark gpt-4o-mini rates (USD per 1M tokens), verify before board packs
PRICE_PROMPT_PER_M = 0.15
PRICE_COMPLETION_PER_M = 0.60

def estimate_request_usd(prompt_tokens: int, completion_tokens: int) -> float:
    return (prompt_tokens * PRICE_PROMPT_PER_M
            + completion_tokens * PRICE_COMPLETION_PER_M) / 1_000_000

# Typical AfyaPlus triage: ~450 prompt (system + message), ~180 completion
print(round(estimate_request_usd(450, 180), 6))