import hashlib
import json
import time


def audit(actor: str, action: str, resource: str, ok: bool,
          payload: str | None = None) -> None:
    row = {
        'ts': int(time.time()),
        'actor': actor,
        'action': action,
        'resource': resource,
        'ok': ok,
        'payload_sha': hashlib.sha256((payload or '').encode()).hexdigest()[:16],
    }
    print(json.dumps(row))


if __name__ == '__main__':
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        audit('partner_clinic', 'check_stock', 'KSM-01', True,
              'national id 12345678 fever two days')
    row = json.loads(buf.getvalue())
    # The sentence must not reach the log, only a correlatable token
    assert '12345678' not in buf.getvalue()
    assert row['actor'] == 'partner_clinic' and row['ok'] is True
    assert len(row['payload_sha']) == 16
    # Two identical payloads must correlate
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        audit('partner_clinic', 'check_stock', 'KSM-01', True,
              'national id 12345678 fever two days')
    assert json.loads(buf2.getvalue())['payload_sha'] == row['payload_sha']
    print('audit_log OK', row['action'], row['payload_sha'])