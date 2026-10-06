"""CI gate: every knowledge file must still hash to its committed pin."""
import hashlib
import json
import sys
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    pin = json.loads(Path('knowledge/pin.json').read_text())
    bad = []
    for rel, expected in pin.items():
        p = Path(rel)
        if not p.exists():
            bad.append((rel, 'MISSING', expected))
            continue
        got = sha(p)
        if got != expected:
            bad.append((rel, got, expected))
    if bad:
        print('CORPUS PIN MISMATCH')
        for row in bad:
            print(' ', row)
        return 1
    print('corpus pin OK', list(pin))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())