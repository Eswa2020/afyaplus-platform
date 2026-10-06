"""Gate: the threat model must cover four kinds and carry real controls."""
import json
import sys
from pathlib import Path

REQUIRED = {'secret', 'data', 'config', 'mcp'}


def main() -> int:
    rows = json.loads(Path('threat_model.json').read_text(encoding='utf-8'))
    kinds = {r.get('kind') for r in rows}
    missing = REQUIRED - kinds
    if missing:
        print('FAIL missing kinds:', sorted(missing))
        return 1
    for r in rows:
        if len((r.get('control') or '').strip()) < 8:
            print('FAIL weak or blank control on', r.get('asset') or r.get('kind'))
            return 1
        for k in ('asset', 'actor', 'action', 'kind'):
            if not str(r.get(k) or '').strip():
                print('FAIL incomplete row', r)
                return 1
    print('OK', len(rows), 'rows')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())