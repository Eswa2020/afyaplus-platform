#!/usr/bin/env bash
# secrets_not_in_git.sh: executable hygiene checks that fail closed.
# Resolves the repo root, because .env lives there, not in security-compliance/.
set -euo pipefail

fail() { echo "FAIL: $*" >&2; exit 1; }

ROOT="$(git rev-parse --show-toplevel)" || fail "not inside a git repository"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1) .env must be ignored (checked at the repo root)
if ! git -C "$ROOT" check-ignore -v .env >/dev/null 2>&1; then
  fail ".env is not gitignored"
fi

# 2) .env must never appear in history, on any branch.
#    Capture first: piping into grep -q under pipefail can hide a real match.
HISTORY="$(git -C "$ROOT" log --all --full-history --oneline -- .env 2>/dev/null || true)"
if [ -n "$HISTORY" ]; then
  fail ".env appears in git history: rotate the secrets"
fi

# 3) Compose must not inline quoted secret values
python "$HERE/check_gitignore.py" || fail "check_gitignore.py reported a problem"

echo "OK: secrets_not_in_git.sh passed"