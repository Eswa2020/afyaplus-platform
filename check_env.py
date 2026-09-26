import os
from dotenv import load_dotenv

import fastapi, httpx, openai  # noqa: F401  (just proving they import)

try:
    import redis
    print("redis: OK")
except ImportError:
    print("redis: not installed (dict cache fallback is fine)")

print("Week 7 base imports OK")

load_dotenv()
print("OPENAI_API_KEY:", bool(os.getenv("OPENAI_API_KEY")))
print("JWT_SECRET:", bool(os.getenv("JWT_SECRET")))