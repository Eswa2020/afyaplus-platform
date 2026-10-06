"""Schema check for kms_twin.json: five jobs, two real twins on each."""
import json
import sys
from pathlib import Path

REQUIRED_JOBS = ['store_secret', 'encrypt_dek', 'rotate', 'audit', 'grant_identity']
PLACEHOLDERS = {'', 'tbd', 'todo', 'n/a'}


def blank(value) -> bool:
    return str(value or '').strip().lower() in PLACEHOLDERS


def main() -> int:
    path = Path('kms_twin.json')
    if not path.exists():
        print('FAIL missing kms_twin.json')
        return 1
    data = json.loads(path.read_text())
    problems = []
    for job in REQUIRED_JOBS:
        node = data.get(job)
        if not isinstance(node, dict):
            problems.append((job, 'missing job'))
            continue
        for side in ('azure', 'aws'):
            if blank(node.get(side)):
                problems.append((job, f'blank {side} twin'))
    if problems:
        print('FAIL kms_twin schema')
        for row in problems:
            print(' ', row)
        return 1
    print('OK kms_twin schema:', len(REQUIRED_JOBS), 'jobs, both twins present')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())