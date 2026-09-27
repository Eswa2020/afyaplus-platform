TAGS = {
    'service': 'triage-api',
    'env': 'prod',
    'partner_id': 'kisumu-pilot',
    'model': 'gpt-4o-mini',
}

# Attach to structured logs / cloud resource tags / OpenAI metadata where supported
def log_usage(trace_id: str, prompt_tokens: int, completion_tokens: int, usd: float):
    print({'trace_id': trace_id, **TAGS,
           'prompt_tokens': prompt_tokens,
           'completion_tokens': completion_tokens,
           'usd': round(usd, 6)})

log_usage('abc123', 450, 180, 0.000202)