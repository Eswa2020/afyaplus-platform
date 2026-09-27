"""API vs self-hosted break-even for AfyaPlus triage.

Honest defaults: self-host only wins at volume. GPU ops are real, include
people time in fixed monthly cost or you are lying to yourself.
"""
from cost_model import fully_loaded_usd, PROMPT_TOKENS, COMPLETION_TOKENS

# API side (from Lab 1)
api_per_req = fully_loaded_usd(PROMPT_TOKENS, COMPLETION_TOKENS)

# Self-host side, EDIT with quotes from your cloud of choice
GPU_INSTANCE_MONTHLY = 850.0    # 1x A10-class or similar, on-demand ballpark
PEOPLE_ONCALL_MONTHLY = 400.0   # fraction of SRE / ML eng time (honest!)
STORAGE_OBS_MONTHLY = 50.0
SELFHOST_FIXED = GPU_INSTANCE_MONTHLY + PEOPLE_ONCALL_MONTHLY + STORAGE_OBS_MONTHLY
SELFHOST_VAR_PER_REQ = 0.00005  # egress / energy proxy, not zero


def break_even_requests(api_cost: float, fixed: float, var: float) -> float:
    margin = api_cost - var
    if margin <= 0:
        return float('inf')
    return fixed / margin


def memo_lines(n_star: float) -> str:
    lines = [
        'AfyaPlus triage, API vs self-hosted break-even',
        f'api_usd_per_req={api_per_req:.6f}',
        f'selfhost_fixed_monthly={SELFHOST_FIXED:.2f}',
        f'selfhost_var_per_req={SELFHOST_VAR_PER_REQ:.6f}',
        f'break_even_monthly_requests={n_star:.0f}'
        if n_star != float('inf') else 'break_even=never (var >= api)',
        '',
        'Recommendation sketch:',
        '- Below break-even: stay API-hosted; invest in cache, prompt trim, rate limits.',
        '- Near break-even: pilot self-host on hot FAQ paths only; keep /triage contract.',
        '- Above break-even: migrate hot volume; keep API for bursts and experiments.',
        '- GPU ops risk: patching, capacity, cold start, budget PEOPLE_ONCALL_MONTHLY.',
    ]
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    n_star = break_even_requests(api_per_req, SELFHOST_FIXED, SELFHOST_VAR_PER_REQ)
    text = memo_lines(n_star)
    with open('breakeven_memo.txt', 'w') as fh:
        fh.write(text)
    print(text)