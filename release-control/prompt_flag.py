import hashlib


def select_prompt_version(partner_id: str, flag_pct: int = 10) -> str:
    """Deterministic 10% canary. The same partner always sees the same
    variant, even after a pod restart (do not use the builtin hash())."""
    bucket = int(hashlib.sha256(partner_id.encode()).hexdigest(), 16) % 100
    if bucket < flag_pct:
        return '1.3.0-candidate'
    return '1.2.0'


# Acceptance (two processes must agree):
# python prompt_flag.py; python prompt_flag.py
if __name__ == '__main__':
    for pid in ('clinic-a', 'kisumu-01'):
        b = int(hashlib.sha256(pid.encode()).hexdigest(), 16) % 100
        print(pid, 'bucket', b, 'version', select_prompt_version(pid))