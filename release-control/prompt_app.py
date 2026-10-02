"""AfyaPlus triage API, with the versioned prompt reported on /health."""
import hashlib
import os
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

PROMPTS_DIR = Path('prompts')
PROMPT_VERSION = os.environ.get('PROMPT_VERSION', '1.2.0')


def load_prompt(version: str) -> str:
    path = PROMPTS_DIR / f'triage_system_v{version}.txt'
    if not path.is_file():
        raise FileNotFoundError(f'No prompt for version {version!r}: {path}')
    return path.read_text(encoding='utf-8')


SYSTEM_PROMPT = load_prompt(PROMPT_VERSION)
PROMPT_SHA256 = hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()

app = FastAPI(title='AfyaPlus Triage', version='1.2.0')


class TriageIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'prompt_version': PROMPT_VERSION,
        'prompt_sha256': PROMPT_SHA256,
        'model': os.environ.get('LLM_MODEL', 'gpt-4o-mini'),
    }


@app.post('/triage')
def triage(body: TriageIn):
    # The lab focus is versioning. Wire your Week 6 OpenAI client here,
    # and always send SYSTEM_PROMPT as the system message.
    return {
        'advice': '(model call uses SYSTEM_PROMPT, stub for lab)',
        'prompt_version': PROMPT_VERSION,
        'disclaimer': 'Not a diagnosis. Seek professional care when unsure.',
    }


if __name__ == '__main__':
    # Print pin material for prompts/pin.json
    print('PROMPT_VERSION', PROMPT_VERSION)
    print('PROMPT_SHA256', PROMPT_SHA256)