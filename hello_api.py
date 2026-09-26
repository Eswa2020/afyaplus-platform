# hello_api.py - our very first API
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AfyaPlus Hello API", version="0.1.0")

@app.get("/hello")
def hello():
    return {"message": "AfyaPlus API is running", "service": "hello-api"}
class EchoRequest(BaseModel):
    text: str

@app.post("/echo")
def echo(body: EchoRequest):
    return {"you_said": body.text}