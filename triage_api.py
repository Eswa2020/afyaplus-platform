# triage_api.py - the AfyaPlus triage service
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="AfyaPlus Triage API", version="1.0.0")

class TriageRequest(BaseModel):
    patient_message: str = Field(min_length=5, max_length=1000)
    county: str = Field(min_length=2, max_length=40)

class TriageResponse(BaseModel):
    urgency: str
    advice: str
    model_used: str

URGENT_WORDS = ["chest pain", "bleeding", "unconscious", "cannot breathe"]

def triage_model(message: str) -> dict:
    """Stand-in for the Week 5 LLM call. Same shape, no API cost."""
    text = message.lower()
    if any(word in text for word in URGENT_WORDS):
        return {"urgency": "high", "advice": "Please go to the nearest clinic now."}
    return {"urgency": "low", "advice": "Rest, drink fluids, and monitor your symptoms."}

@app.get("/health")
def health():
    return {"service": "triage-api", "version": "1.0.0", "status": "ok"}

@app.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest):
    try:
        result = triage_model(request.patient_message)
    except Exception:
        raise HTTPException(status_code=503, detail="The AI model is unavailable. Try again shortly.")
    return TriageResponse(urgency=result["urgency"], advice=result["advice"], model_used="triage-stub-v1")