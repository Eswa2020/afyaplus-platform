import hashlib
import time
from functools import wraps

_CACHE = {}


def cache_response(ttl_s=600):
    def deco(fn):
        @wraps(fn)
        def wrapper(message: str):
            key = hashlib.sha256(message.strip().lower().encode()).hexdigest()
            row = _CACHE.get(key)
            if row and row[0] > time.time():
                return {**row[1], '_cache': 'HIT'}
            out = fn(message)
            _CACHE[key] = (time.time() + ttl_s, out)
            return {**out, '_cache': 'MISS'}
        return wrapper
    return deco


@cache_response(ttl_s=600)
def triage(message: str) -> dict:
    # Stub stands in for the model call
    return {'urgency': 'routine',
            'advice': 'Rest and hydrate. Seek clinic care if symptoms worsen.'}


if __name__ == '__main__':
    m = 'Fever for two days, drinking fluids'
    print(triage(m)['_cache'], triage(m)['_cache'])  # MISS then HIT