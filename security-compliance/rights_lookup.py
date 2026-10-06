"""Access-request sketch: count events for a peppered subject hash, never content.

Why not plain SHA-256: there are only three clinic IDs, so anyone can hash all three
and reverse the mapping instantly. The secret pepper (HMAC key) makes the digest a
real one-way step.
"""
import hashlib
import hmac
import json
import os
from pathlib import Path


def pepper() -> bytes:
    # Prefer a vault-injected reference; fall back to the lab stand-in
    val = os.getenv('SUBJECT_PEPPER') or os.getenv('JWT_SECRET') or ''
    if not val:
        raise SystemExit('missing SUBJECT_PEPPER (or JWT_SECRET as a lab stand-in)')
    return val.encode()


def key(clinic_id: str) -> str:
    """HMAC with a pepper: clinic IDs are low cardinality, so plain SHA is guessable."""
    return hmac.new(pepper(), clinic_id.encode(), hashlib.sha256).hexdigest()[:16]


def lookup(clinic_id: str, path: str = 'fixtures/subjects.json') -> dict:
    want = key(clinic_id)
    rows = json.loads(Path(path).read_text())
    n = sum(1 for r in rows if r.get('subject_hash') == want)
    return {'found': n > 0, 'n_events': n}


if __name__ == '__main__':
    # The fixture is shipped statically. Do not regenerate it here.
    path = Path('fixtures/subjects.json')
    assert path.exists(), 'missing fixtures/subjects.json (shipped static fixture)'
    found = lookup('KSM-01')
    absent = lookup('HBA-01')
    assert found == {'found': True, 'n_events': 3}, found
    assert absent == {'found': False, 'n_events': 0}, absent
    print(found)
    print(absent)