# triage_api_v1.py - the first working triage service (version 1)
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="AfyaPlus Triage API", version="0.1.0")

class TriageRequest(BaseModel):
    patient_message: str = Field(min_length=5, max_length=1000)
    county: str = Field(min_length=2, max_length=40)

URGENT_WORDS = ["chest pain", "bleeding", "unconscious", "cannot breathe"]

def triage_model(message: str) -> dict:
    """Stand-in for the Week 5 LLM call. Same shape, no API cost."""
    text = message.lower()
    if any(word in text for word in URGENT_WORDS):
        return {"urgency": "high", "advice": "Please go to the nearest clinic now."}
    return {"urgency": "low", "advice": "Rest, drink fluids, and monitor your symptoms."}

@app.post("/triage")
def triage(request: TriageRequest):
    return triage_model(request.patient_message)