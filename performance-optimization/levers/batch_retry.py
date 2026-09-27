"""Retry and dead-letter path for the batch queue.

- Every job carries an attempts count, incremented and committed BEFORE the work,
  so a job that crashes the worker still uses up a try.
- If a whole batch fails, its jobs are retried one at a time, so one bad job
  cannot sink the healthy ones in the same batch.
- A job still failing after MAX_ATTEMPTS becomes 'dead': out of the queue,
  visible to a person.

Usage:
    python batch_retry.py seed    # fresh queue: 3 healthy jobs + 1 poison job
    python batch_retry.py         # one worker pass
"""
import sys

from batch_worker import DB, init, enqueue, fetch_batch, summarise_batch

MAX_ATTEMPTS = 3


def migrate(conn):
    cols = [row[1] for row in conn.execute('PRAGMA table_info(jobs)')]
    if 'attempts' not in cols:
        conn.execute('ALTER TABLE jobs ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0')
        conn.commit()


def process_once(batch_size=8):
    conn = init()
    migrate(conn)
    batch = fetch_batch(conn, batch_size)
    if not batch:
        return 0, 0
    ids = [b[0] for b in batch]
    marks = ','.join('?' * len(ids))
    conn.execute(f'UPDATE jobs SET attempts = attempts + 1 WHERE id IN ({marks})', ids)
    conn.commit()

    done = failed = 0
    try:
        results = summarise_batch([b[1] for b in batch])
        pairs = list(zip(ids, results))
    except Exception as exc:
        print(f'batch of {len(batch)} failed ({exc}); retrying jobs one at a time')
        pairs = []
        for job_id, text in batch:
            try:
                pairs.append((job_id, summarise_batch([text])[0]))
            except Exception:
                failed += 1  # stays pending, attempt already counted

    for job_id, result in pairs:
        conn.execute("UPDATE jobs SET status='done', result=? WHERE id=?", (result, job_id))
        done += 1
    conn.execute("UPDATE jobs SET status='dead' WHERE status='pending' AND attempts >= ?",
                 (MAX_ATTEMPTS,))
    conn.commit()
    return done, failed


def report():
    conn = init()
    rows = conn.execute('SELECT id, status, attempts, text FROM jobs ORDER BY id').fetchall()
    summary = dict(conn.execute('SELECT status, count(*) FROM jobs GROUP BY status').fetchall())
    return summary, rows


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'seed':
        DB.unlink(missing_ok=True)
        conn = init()
        migrate(conn)
        for text in ['fever hydration themes', 'stock delay FAQ', '<poison> malformed row',
                     'delivery window questions']:
            enqueue(conn, text)
        print('fresh queue:', report()[0])
    else:
        done, failed = process_once()
        summary, rows = report()
        print(f'done={done} failed={failed}', summary)
        for job_id, status, attempts, text in rows:
            if status != 'done':
                print(f'  job {job_id}: {status}, attempts={attempts}, text={text!r}')