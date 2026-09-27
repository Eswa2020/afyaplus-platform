"""Exact-match response cache for triage, with TTL, hit/miss metrics and an
optional Redis backend (falls back to an in-memory dict if Redis is not reachable)."""
import hashlib
import json
import os
import time
from functools import wraps

try:
    import redis
    r = redis.Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
                             decode_responses=True, socket_connect_timeout=1)
    r.ping()
    BACKEND = 'redis'
except Exception:
    r = None
    BACKEND = 'memory'

_MEM = {}
KEY_PREFIX = 'triage:'
metrics = {'hits': 0, 'misses': 0}


def _key(message: str) -> str:
    return KEY_PREFIX + hashlib.sha256(message.strip().lower().encode()).hexdigest()


def _get(key):
    if BACKEND == 'redis':
        raw = r.get(key)
        return json.loads(raw) if raw else None
    row = _MEM.get(key)
    if not row:
        return None
    expires_at, value = row
    return value if expires_at > time.time() else None


def _set(key, value, ttl_s):
    if BACKEND == 'redis':
            r.set(key, json.dumps(value), ex=ttl_s)
    else:
        _MEM[key] = (time.time() + ttl_s, value)


def clear_cache():
    """Empty the triage cache and reset counters, so every measured run starts cold."""
    if BACKEND == 'redis':
        for k in r.scan_iter(KEY_PREFIX + '*'):
            r.delete(k)
    _MEM.clear()
    metrics['hits'] = metrics['misses'] = 0


def cache_response(ttl_s=600):
    def deco(fn):
        @wraps(fn)
        def wrapper(message: str):
            key = _key(message)
            hit = _get(key)
            if hit is not None:
                metrics['hits'] += 1
                return {**hit, '_cache': 'HIT', '_backend': BACKEND}
            out = fn(message)
            _set(key, out, ttl_s)
            metrics['misses'] += 1
            return {**out, '_cache': 'MISS', '_backend': BACKEND}
        return wrapper
    return deco


def hit_rate():
    total = metrics['hits'] + metrics['misses']
    return (metrics['hits'] / total) if total else 0.0


@cache_response(ttl_s=600)
def triage(message: str) -> dict:
    # Stub stands in for the model call; keeps the lab free while wiring
    return {'urgency': 'routine',
            'advice': 'Rest and hydrate. Seek clinic care if symptoms worsen.'}


if __name__ == '__main__':
    clear_cache()
    m = 'Fever for two days'
    print(triage(m)['_cache'], triage(m)['_cache'], BACKEND, round(hit_rate(), 2))