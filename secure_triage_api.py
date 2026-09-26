# minor comment edit for cache test
# secure_triage_api.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from auth import check_password, create_token, current_user
from rate_limit import check_rate_limit
import concurrent.futures
from datetime import datetime

app = FastAPI(title="AfyaPlus Secured Triage API", version="1.1.0")

executor = concurrent.futures.ThreadPoolExecutor()

def triage_model_stub(message: str) -> dict:
    return {"urgency": "low", "advice": "Rest, drink fluids, and monitor your symptoms."}

def call_model_with_timeout(message: str, seconds: float = 2.0) -> dict:
    future = executor.submit(triage_model_stub, message)
    try:
        return future.result(timeout=seconds)
    except concurrent.futures.TimeoutError:
        raise HTTPException(status_code=503, detail="The model took too long. Please try again.")

def write_audit_line(username: str, county: str, urgency: str) -> None:
    stamp = datetime.now().isoformat(timespec="seconds")
    with open("audit.log", "a") as f:
        f.write(f"{stamp} user={username} county={county} urgency={urgency}\n")

class LoginRequest(BaseModel):
    username: str
    password: str

class TriageRequest(BaseModel):
    patient_message: str = Field(min_length=5, max_length=1000)
    county: str = Field(min_length=2, max_length=40)

@app.get("/health")
def health():
    return {"service": "triage-api", "version": "1.1.0", "status": "ok"}

@app.post("/token")
def login(body: LoginRequest):
    if not check_password(body.username, body.password):
        raise HTTPException(status_code=401, detail="Wrong username or password.")
    return {"access_token": create_token(body.username), "token_type": "bearer"}

@app.post("/triage")
def triage(request: TriageRequest, background: BackgroundTasks, user: dict = Depends(current_user)):
    check_rate_limit(user["sub"])
    if user["role"] != "coordinator":
        raise HTTPException(403, "Your role may not use triage.")
    result = call_model_with_timeout(request.patient_message)
    background.add_task(write_audit_line, user["sub"], request.county, result["urgency"])
    return {**result, "handled_for": user["sub"]}