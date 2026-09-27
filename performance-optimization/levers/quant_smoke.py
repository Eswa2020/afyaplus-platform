"""Cheap-path quality smoke test (a proxy for quantization, no GPU needed).

Full path: urgency label plus a one-sentence reason (up to 60 output tokens).
Small path: urgency label only (up to 4 output tokens), a cheaper, compressed answer.
The full path's label is the reference, so agreement means "the cheap path would have
given the same urgency as the full path", not clinical correctness.
Makes 40 live gpt-4o-mini calls (20 fixtures x 2 paths), a fraction of a US cent.
"""
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / '.env')  # OPENAI_API_KEY lives in the project-root .env

# Prices come from the cost model, one source of truth
sys.path.insert(0, str(ROOT / 'cost-optimization' / 'cost-model'))
from cost_model import PRICE_PROMPT_PER_M, PRICE_COMPLETION_PER_M  # noqa: E402

MODEL = 'gpt-4o-mini'
N = 20
LABELS = ('emergency', 'urgent', 'routine')

FULL_PROMPT = ('Classify the urgency of this patient message as exactly one of: '
               'routine, urgent, emergency. Reply as "<label>: <one short reason>". '
               'Do not diagnose.\nMessage: {m}')
SMALL_PROMPT = ('Urgency of this patient message, one word only '
                '(routine, urgent or emergency):\n{m}')

client = OpenAI()


def parse_label(text: str) -> str:
    text = text.lower()
    found = [(text.find(l), l) for l in LABELS if l in text]
    return min(found)[1] if found else 'unparsed'


def run(prompt: str, max_tokens: int):
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=max_tokens,
        temperature=0,
    )
    text = (r.choices[0].message.content or '').strip()
    return parse_label(text), r.usage.prompt_tokens, r.usage.completion_tokens


def usd(prompt_tokens: int, completion_tokens: int) -> float:
    return (prompt_tokens * PRICE_PROMPT_PER_M
            + completion_tokens * PRICE_COMPLETION_PER_M) / 1_000_000


with open('fixtures/triage_messages.json', encoding='utf-8') as f:
    messages = json.load(f)[:N]

matches = 0
tok = {'full_prompt': 0, 'full_completion': 0, 'small_prompt': 0, 'small_completion': 0}
disagreements = []
for m in messages:
    full, fp, fc = run(FULL_PROMPT.format(m=m), max_tokens=60)
    small, sp, sc = run(SMALL_PROMPT.format(m=m), max_tokens=4)
    tok['full_prompt'] += fp
    tok['full_completion'] += fc
    tok['small_prompt'] += sp
    tok['small_completion'] += sc
    if full == small:
        matches += 1
    else:
        disagreements.append({'message': m, 'full': full, 'small': small})

usd_full = usd(tok['full_prompt'], tok['full_completion'])
usd_small = usd(tok['small_prompt'], tok['small_completion'])

out = {
    'n': N,
    'model': MODEL,
    'agreement_rate': round(matches / N, 3),
    'tokens_full': tok['full_prompt'] + tok['full_completion'],
    'tokens_small': tok['small_prompt'] + tok['small_completion'],
    'usd_per_1k_full': round(1000 * usd_full / N, 4),
    'usd_per_1k_small': round(1000 * usd_small / N, 4),
    'disagreements': disagreements,
    'notes': ('Proxy for quantization: same model, shorter prompt and a 4-token label-only '
              'answer vs label plus reason. Reference is the full path, not a clinical '
              'label; agreement measures consistency, not correctness. Prices from '
              'cost_model.py, API cost only (no infra overhead). Replace with a real INT8 '
              'endpoint when available.'),
}
with open('quality_smoke.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2)
print(json.dumps({k: v for k, v in out.items() if k != 'notes'}, indent=2))

