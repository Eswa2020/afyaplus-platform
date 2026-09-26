# check_upstream.py - a response from another API is input too
import httpx
from pydantic import BaseModel, ValidationError

class HelloResponse(BaseModel):
    message: str
    service: str

class WrongExpectation(BaseModel):     # what a consumer with an outdated schema expects
    message: str
    service: str
    uptime_seconds: int                # the hello API promises no such field

raw = httpx.get("http://127.0.0.1:8000/hello", timeout=5).json()

verdict = HelloResponse.model_validate(raw)          # the happy path: checked and typed
print("Validated OK:", verdict.message)

try:
    WrongExpectation.model_validate(raw)             # the same data against the wrong schema
except ValidationError as e:
    print("Caught a broken agreement:")
    print(e.errors()[0]["loc"], "-", e.errors()[0]["msg"])