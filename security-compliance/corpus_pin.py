"""Create a tiny knowledge file if missing, then freeze its hash in knowledge/pin.json."""
import hashlib
import json
from pathlib import Path

KNOWLEDGE = Path('knowledge/ors_faq.md')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == '__main__':
    KNOWLEDGE.parent.mkdir(parents=True, exist_ok=True)
    if not KNOWLEDGE.exists():
        KNOWLEDGE.write_text('ORS is oral rehydration. Seek clinic care if unsure.\n')
    pin = {'knowledge/ors_faq.md': sha(KNOWLEDGE)}
    Path('knowledge/pin.json').write_text(json.dumps(pin, indent=2))
    print('wrote knowledge/pin.json', pin)