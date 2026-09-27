"""Overnight batch queue: SQLite table of jobs, a worker that summarises them
in batches and marks them done. Kept off the interactive /triage path.

Usage:
    python batch_worker.py seed    # add three sample jobs
    python batch_worker.py         # process one batch of pending jobs
"""
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent / 'jobs.sqlite'  # same file whatever folder you run from
SCHEMA = (
    'CREATE TABLE IF NOT EXISTS jobs ('
    'id INTEGER PRIMARY KEY AUTOINCREMENT,'
    'text TEXT NOT NULL,'
    "status TEXT NOT NULL DEFAULT 'pending',"
    'result TEXT)'
)


def init():
    conn = sqlite3.connect(DB)
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def enqueue(conn, text: str):
    conn.execute('INSERT INTO jobs(text) VALUES (?)', (text,))
    conn.commit()


def fetch_batch(conn, n=8):
    return conn.execute(
        "SELECT id, text FROM jobs WHERE status='pending' ORDER BY id LIMIT ?",
        (n,)).fetchall()


def summarise_batch(texts: list) -> list:
    # Stub: replace with one batched API call or capped concurrent calls.
    # '<poison>' simulates a malformed job the summariser cannot handle.
    for t in texts:
        if '<poison>' in t:
            raise ValueError(f'cannot summarise: {t}')
    return [f'Theme stub ({len(t.split())} words)' for t in texts]


def process_once(batch_size=8):
    conn = init()
    batch = fetch_batch(conn, batch_size)
    if not batch:
        return 0
    ids = [b[0] for b in batch]
    results = summarise_batch([b[1] for b in batch])
    for job_id, result in zip(ids, results):  # mark done only after the work succeeded
        conn.execute("UPDATE jobs SET status='done', result=? WHERE id=?", (result, job_id))
    conn.commit()
    return len(ids)


def counts():
    conn = init()
    return dict(conn.execute('SELECT status, count(*) FROM jobs GROUP BY status').fetchall())


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'seed':
        c = init()
        for sample in ['fever hydration', 'stock delay FAQ', 'delivery window']:
            enqueue(c, sample)
        print('enqueued 3', counts())
    else:
        print('processed', process_once(), counts())