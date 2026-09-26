# clinic_notes_api.py - one resource, every verb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AfyaPlus Clinic Notes API", version="0.1.0")

class Note(BaseModel):
    clinic: str
    text: str
    resolved: bool = False

# our "database" for this lesson: a dictionary in memory
NOTES: dict[int, Note] = {
    1: Note(clinic="Kisumu Central", text="Fridge repaired, vaccines restocked."),
}
NEXT_ID = 2

@app.get("/notes")
def list_notes():
    return {"count": len(NOTES), "notes": NOTES}

@app.get("/notes/{note_id}")
def get_note(note_id: int):
    if note_id not in NOTES:
        raise HTTPException(404, "No note with that id")
    return NOTES[note_id]

@app.post("/notes", status_code=201)
def create_note(note: Note):
    global NEXT_ID
    NOTES[NEXT_ID] = note
    NEXT_ID += 1
    return {"id": NEXT_ID - 1, "note": note}

@app.put("/notes/{note_id}")
def replace_note(note_id: int, note: Note):
    if note_id not in NOTES:
        raise HTTPException(404, "No note with that id")
    NOTES[note_id] = note
    return NOTES[note_id]

class NotePatch(BaseModel):
    clinic: str | None = None
    text: str | None = None
    resolved: bool | None = None

@app.delete("/notes/resolved")                 # must come BEFORE delete_note below
def sweep_resolved():
    ids = [i for i, n in NOTES.items() if n.resolved]
    for i in ids:
        del NOTES[i]
    return {"swept": len(ids)}

@app.patch("/notes/{note_id}/resolve")
def resolve_note(note_id: int):
    if note_id not in NOTES:
        raise HTTPException(404, "No note with that id")
    NOTES[note_id] = NOTES[note_id].model_copy(update={"resolved": True})
    return NOTES[note_id]