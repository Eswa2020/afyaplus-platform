# validate_api.py - a full mini API whose only job is checking input
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="AfyaPlus Validation Demo", version="0.1.0")

class EchoRequest(BaseModel):
    model_config = {"extra": "forbid"}
    text: str = Field(min_length=5, max_length=200)
    county: str = Field(min_length=2, max_length=40)

@app.post("/echo")
def echo(body: EchoRequest):
    return {"you_said": body.text, "from_county": body.county}