import os
import sys


def require(name: str) -> str:
    val = os.getenv(name) or ''
    if not val.strip():
        print('missing secret:', name)
        sys.exit(1)
    return val


if __name__ == '__main__':
    os.environ['DEMO_SECRET'] = 'a-real-value'
    assert require('DEMO_SECRET') == 'a-real-value'
    # Unset, empty and whitespace-only must all be the same failure
    for bad in ('', '   '):
        os.environ['DEMO_SECRET'] = bad
        try:
            require('DEMO_SECRET')
        except SystemExit as e:
            assert e.code == 1
        else:
            raise AssertionError('booted with a blank secret: ' + repr(bad))
    print('boot_guard OK, 1 accepted and 2 refused')