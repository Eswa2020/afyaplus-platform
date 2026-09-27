"""Drive 100 cached triage calls (40 unique + 60 repeats) and enforce hit_rate >= 0.55."""
import json
import random
import sys

from cache_triage import triage, clear_cache, BACKEND

TARGET = 0.55

random.seed(7)
with open('fixtures/triage_messages.json', encoding='utf-8') as f:
    msgs = json.load(f)[:40]
assert len(msgs) == 40

calls = list(msgs) + [random.choice(msgs) for _ in range(60)]
random.shuffle(calls)

clear_cache()  # start cold, so earlier runs cannot inflate the result
hits = misses = 0
for m in calls:
    if triage(m)['_cache'] == 'HIT':
        hits += 1
    else:
        misses += 1

rate = hits / len(calls)
print(f'backend={BACKEND} hits={hits} misses={misses} hit_rate={rate:.2f}')
sys.exit(0 if rate >= TARGET else 1)