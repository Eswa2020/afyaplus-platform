"""Gate: the manager brief must carry four headings and must not overclaim."""
import sys
from pathlib import Path

HEADS = ['Risks', 'Mitigations', 'Kenya DPA alignment', 'What we will not claim']
BANNED = ['unhackable']


def main(path: str = 'fixtures/manager_brief_headings.md') -> int:
    text = Path(path).read_text()
    low = text.lower()
    for word in BANNED:
        if word in low:
            print(f'FAIL: do not claim {word}')
            return 1
    missing = [h for h in HEADS if h.lower() not in low]
    if missing:
        print('FAIL missing headings', missing)
        return 1
    print('brief headings OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(*sys.argv[1:2]))