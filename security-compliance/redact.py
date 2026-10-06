"""Redact Kenya-facing identifiers and tokens before anything reaches disk."""
import json
import re
from pathlib import Path

BEARER = re.compile(r'Bearer\s+\S+', re.I)
# 8-digit national identity number, not a 7-to-10 catch-all: that eats timestamps
KENYA_ID = re.compile(r'\b\d{8}\b')
# Phone: 07XXXXXXXX or +2547XXXXXXXX
PHONE = re.compile(r'(?:\+254|0)7\d{8}\b')
# M-Pesa code: a letter then nine alphanumerics, so a 10-digit epoch never matches
MPESA = re.compile(r'\b[A-Z][A-Z0-9]{9}\b')

LOG = Path('logs/audit.jsonl')


def redact(text: str) -> str:
    text = BEARER.sub('Bearer [REDACTED]', text)
    text = PHONE.sub('[REDACTED_PHONE]', text)
    text = MPESA.sub('[REDACTED_MPESA]', text)
    text = KENYA_ID.sub('[REDACTED_ID]', text)
    return text


def write_audit(actor: str, action: str, resource: str, payload: str) -> str:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {
        'actor': actor,
        'action': action,
        'resource': resource,
        'payload': redact(payload),
    }
    with LOG.open('a') as f:
        f.write(json.dumps(row) + '\n')
    return row['payload']


if __name__ == '__main__':
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text('')
    stored = write_audit(
        'partner_clinic', 'check_stock', 'KSM-01',
        'id 12345678 phone 0712345678 code SH45K7L9M2 '
        'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.aaa')
    blob = LOG.read_text()
    assert '12345678' not in blob
    assert '0712345678' not in blob
    assert 'eyJhbGci' not in blob
    # A ten-digit epoch timestamp must survive the identity pattern
    assert redact('ts 1724000000 event') == 'ts 1724000000 event'
    print('redact OK', stored)