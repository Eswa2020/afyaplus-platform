"""Retention sweeper stub: apply a fixed 90-day clock and record the deletion."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

NOW = 1_724_000_000
KEEP_SECONDS = 90 * 24 * 3600
CUT = NOW - KEEP_SECONDS
DELETION_LOG = Path('deletion_records.jsonl')


def sweep(src: Path, dest: Path, dataset: str = 'triage_messages') -> dict:
    kept, dropped = [], []
    for line in src.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        (kept if row['ts'] >= CUT else dropped).append(row)
    dest.write_text(''.join(json.dumps(r) + '\n' for r in kept))
    report = {
        'job_id': str(uuid.uuid4()),
        # Same frozen clock as CUT, so the record cannot claim a 2026 run date
        # for a window computed from an August 2024 epoch
        'run_date': datetime.fromtimestamp(NOW, timezone.utc).date().isoformat(),
        'clock': 'fixture: frozen NOW, not a production run',
        'dataset': dataset,
        'range': {'cut_ts': CUT, 'now_ts': NOW},
        'count_dropped': len(dropped),
        'count_kept': len(kept),
        'rule': f'{KEEP_SECONDS // 86400}-day retention for {dataset}',
    }
    # Never delete the deletion record itself
    with DELETION_LOG.open('a') as f:
        f.write(json.dumps(report) + '\n')
    Path('sweep_report.json').write_text(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    src = Path('fixtures/old_logs.jsonl')
    src.parent.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        src.write_text(
            json.dumps({'ts': NOW - KEEP_SECONDS - 10, 'id': 'old'}) + '\n'
            + json.dumps({'ts': NOW - 100, 'id': 'fresh'}) + '\n')
    print(sweep(src, Path('kept.jsonl'), dataset='triage_messages'))