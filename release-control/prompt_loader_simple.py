"""Load a versioned triage system prompt from prompts/."""
from pathlib import Path

PROMPTS_DIR = Path('prompts')


def load_prompt(version: str) -> str:
    path = PROMPTS_DIR / f'triage_system_v{version}.txt'
    if not path.is_file():
        raise FileNotFoundError(f'No prompt for version {version!r}: {path}')
    return path.read_text(encoding='utf-8')


if __name__ == '__main__':
    text = load_prompt('1.2.0')
    print('chars', len(text))
    print(text[:120], '...')