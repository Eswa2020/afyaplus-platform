import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError

app = FastAPI(title="AfyaPlus Guarded Hello", version="0.1.0")

class HelloResponse(BaseModel):
    message: str
    service: str

@app.get("/checked-hello")
def checked_hello():
    try:
        raw = httpx.get("http://127.0.0.1:8000/hello", timeout=5).json()
    except httpx.RequestError:
        raise HTTPException(503, "The hello service is unreachable. Try again shortly.")

    try:
        verdict = HelloResponse.model_validate(raw)
    except ValidationError:
        raise HTTPException(502, "The hello service answered with an unexpected shape.")

    return {"upstream_ok": True, "message": verdict.message}