"""Week 9 setup verification: imports, env, and service health stubs."""
import importlib
import os
import sys
import urllib.request

from dotenv import load_dotenv

load_dotenv()


def check_imports() -> None:
    for name in ('hashlib', 'hmac', 'secrets', 'json', 'yaml', 'cryptography'):
        importlib.import_module(name)
    print('imports OK')


def check_env() -> None:
    print('JWT_SECRET set:', bool(os.getenv('JWT_SECRET')))
    print('OPENAI_API_KEY set:', bool(os.getenv('OPENAI_API_KEY')))


def check_triage_health(url: str = 'http://127.0.0.1:8000/health') -> None:
    """Service check. If offline, print stub guidance rather than faking green."""
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            print('triage /health status:', resp.status)
    except Exception as exc:
        print('triage /health unreachable:', type(exc).__name__)
        print('STUB: start the triage API from Weeks 6 to 8, then re-run verify_setup.py')
        print('If the service is intentionally offline today, note it in README fallbacks.')


def main() -> int:
    check_imports()
    check_env()
    check_triage_health()
    print('Week 9 verify_setup finished')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())