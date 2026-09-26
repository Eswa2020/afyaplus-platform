# agent_api.py - the logistics agent, behind an authenticated API
import logging
import time
from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from auth import current_user, check_password, create_token
from agent_langchain import build_agent

logging.basicConfig(filename="agent_api.log", level=logging.INFO,
                    format="%(asctime)s %(message)s")

app = FastAPI(title="AfyaPlus Logistics Agent API", version="1.0.0")

# ---------- Login ----------

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/token")
def login(body: LoginRequest):
    if not check_password(body.username, body.password):
        raise HTTPException(status_code=401, detail="Wrong username or password.")
    return {"access_token": create_token(body.username), "token_type": "bearer"}

# ---------- Ask the agent (sessions + tracing + cost) ----------

SESSIONS: dict[str, list] = {}          # session_id -> message history
MAX_TURNS = 10                           # cap: histories must not grow forever

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    session_id: str = Field(min_length=1, max_length=100)

@app.post("/ask-logistics")
async def ask_logistics(body: AskRequest, user: dict = Depends(current_user)):
    trace_id = uuid4().hex[:8]
    started = time.perf_counter()
    tokens_in = tokens_out = model_calls = 0
    try:
        history = SESSIONS.setdefault(body.session_id, [])
        agent = await build_agent()
        result = await agent.ainvoke(
            {"messages": history + [("user", body.question)]},
            {"recursion_limit": 8},
        )
        answer = result["messages"][-1].content

        for m in result["messages"]:
            usage = getattr(m, "usage_metadata", None)
            if usage:
                tokens_in += usage.get("input_tokens", 0)
                tokens_out += usage.get("output_tokens", 0)
                model_calls += 1

        history.append(("user", body.question))
        history.append(("assistant", answer))
        SESSIONS[body.session_id] = history[-MAX_TURNS:]

        return {
            "question": body.question,
            "answer": answer,
            "asked_by": user["sub"],
            "trace_id": trace_id,
        }
    finally:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logging.info(f"trace={trace_id} user={user['sub']} "
                     f"ms={elapsed_ms} question_chars={len(body.question)} "
                     f"tokens_in={tokens_in} tokens_out={tokens_out} model_calls={model_calls}")

# ---------- Reorder proposals (human-in-the-loop + idempotency) ----------

PROPOSALS: dict[str, dict] = {}          # lab-grade store; production would use a database

class ReorderProposal(BaseModel):
    clinic_id: str
    item: str
    units: int = Field(gt=0, le=500)

@app.post("/reorders/propose")
def propose_reorder(body: ReorderProposal, user: dict = Depends(current_user)):
    pid = str(uuid4())
    PROPOSALS[pid] = {"id": pid, "status": "proposed",
                      "proposed_by": user["sub"], **body.model_dump()}
    return PROPOSALS[pid]

@app.post("/reorders/{proposal_id}/confirm")
def confirm_reorder(proposal_id: str, user: dict = Depends(current_user)):
    if proposal_id not in PROPOSALS:
        raise HTTPException(404, "No proposal with that id")
    if user["role"] != "coordinator":
        raise HTTPException(403, "Only coordinators may confirm reorders.")
    p = PROPOSALS[proposal_id]
    if p["status"] == "confirmed":
        return p                          # the retry rail: same request, same result
    p["status"] = "confirmed"
    p["confirmed_by"] = user["sub"]
    return p