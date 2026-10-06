"""Fail closed if .env is not ignored or a Compose file inlines a secret.

Runs from any folder: paths are resolved against the git repo root,
because .env and docker-compose.yml live there, not in security-compliance/.
"""
import re
import subprocess
import sys
from pathlib import Path

COMPOSE_CANDIDATES = ['docker-compose.yml', 'docker-compose.yaml', 'compose.yaml']
COMMENT = re.compile(r'#.*$')
LONG_QUOTED = re.compile(r'["\'][^"\']{32,}["\']')   # spec: quoted value of 32+ chars
SECRET_KEYS = ('JWT_SECRET', 'OPENAI_API_KEY')


def repo_root() -> Path | None:
    r = subprocess.run(['git', 'rev-parse', '--show-toplevel'],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return Path(r.stdout.strip())


def strip_comments(text: str) -> str:
    """Remove # comments so teaching notes do not trip the scanner."""
    return '\n'.join(COMMENT.sub('', line) for line in text.splitlines())


def env_ignored(root: Path) -> bool:
    r = subprocess.run(['git', '-C', str(root), 'check-ignore', '-v', '.env'],
                       capture_output=True, text=True)
    return r.returncode == 0 and bool(r.stdout.strip())


def looks_inlined(text: str) -> bool:
    for line in strip_comments(text).splitlines():
        if not any(k in line for k in SECRET_KEYS):
            continue
        if '${' in line or 'secrets.' in line:
            continue                      # a reference, not a value
        if LONG_QUOTED.search(line):
            return True
    return False


def compose_clean(root: Path) -> bool:
    scanned = []
    for name in COMPOSE_CANDIDATES:
        p = root / name
        if p.exists():
            scanned.append(name)
            if looks_inlined(p.read_text(encoding='utf-8')):
                print('FAIL: inlined secret in', name)
                return False
    print('compose scanned:', scanned if scanned else 'none found at repo root')
    return True


def main() -> int:
    root = repo_root()
    if root is None:
        print('FAIL: not inside a git repository')
        return 1
    if not env_ignored(root):
        print('FAIL: .env is not gitignored. Add it, then re-run.')
        return 1
    if not compose_clean(root):
        print('FAIL: a Compose file looks like it inlines a secret. Use ${JWT_SECRET}.')
        return 1
    print('OK: .env ignored and Compose looks clean')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())