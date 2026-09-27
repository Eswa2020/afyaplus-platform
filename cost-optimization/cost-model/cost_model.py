"""AfyaPlus triage, USD per 1,000 requests estimator.

Pricing constants below are documented ballparks for gpt-4o-mini
(USD per 1M tokens). Verify on the vendor pricing page before any
board pack or partner quote, list prices change.
"""

# --- Documented price inputs (edit when vendors update) ---
PRICE_PROMPT_PER_M = 0.15       # USD / 1M prompt tokens
PRICE_COMPLETION_PER_M = 0.60   # USD / 1M completion tokens
INFRA_OVERHEAD = 0.15           # +15% for compute, logs, egress fraction

# --- Baseline AfyaPlus triage shape (from usage logs) ---
PROMPT_TOKENS = 450             # system prompt + patient message
COMPLETION_TOKENS = 180         # advice + disclaimer (never diagnose)
REQUESTS = 1_000


def api_usd(prompt_tokens: int, completion_tokens: int) -> float:
    return (prompt_tokens * PRICE_PROMPT_PER_M
            + completion_tokens * PRICE_COMPLETION_PER_M) / 1_000_000


def fully_loaded_usd(prompt_tokens: int, completion_tokens: int) -> float:
    return api_usd(prompt_tokens, completion_tokens) * (1.0 + INFRA_OVERHEAD)


def cost_per_1k(prompt_tokens: int = PROMPT_TOKENS,
                completion_tokens: int = COMPLETION_TOKENS) -> float:
    return REQUESTS * fully_loaded_usd(prompt_tokens, completion_tokens)


def monthly_at(volume: int, prompt_tokens: int = PROMPT_TOKENS,
               completion_tokens: int = COMPLETION_TOKENS) -> float:
    return volume * fully_loaded_usd(prompt_tokens, completion_tokens)


if __name__ == '__main__':
    per_1k = cost_per_1k()
    print('model=gpt-4o-mini')
    print(f'prompt_tokens={PROMPT_TOKENS} completion_tokens={COMPLETION_TOKENS}')
    print(f'price_prompt_per_m={PRICE_PROMPT_PER_M}')
    print(f'price_completion_per_m={PRICE_COMPLETION_PER_M}')
    print(f'infra_overhead={INFRA_OVERHEAD}')
    print(f'usd_per_request={fully_loaded_usd(PROMPT_TOKENS, COMPLETION_TOKENS):.6f}')
    print(f'usd_per_1k={per_1k:.4f}')
    print(f'monthly_at_100k={monthly_at(100_000):.2f}')
    print(f'monthly_at_1M_10x={monthly_at(1_000_000):.2f}')