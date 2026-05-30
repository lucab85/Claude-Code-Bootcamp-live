from datetime import datetime, timezone
from contextlib import contextmanager
import sqlite3

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

DB_FILE = "notes.db"

def init_db() -> None:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

class NoteCreate(BaseModel):
    title: str
    body: str

class NoteUpdate(BaseModel):
    title: str | None = None
    body: str | None = None

class Note(BaseModel):
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str

app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.on_event("startup")
def startup():
    init_db()

@app.post("/notes", status_code=201)
def create_note(note: NoteCreate) -> Note:
    now = get_utc_timestamp()
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, body, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (note.title, note.body, now, now)
        )
        conn.commit()
        note_id = cursor.lastrowid

    return Note(id=note_id, title=note.title, body=note.body, created_at=now, updated_at=now)

@app.get("/notes")
def list_notes(q: str | None = Query(None)) -> list[Note]:
    with get_db() as conn:
        if q:
            cursor = conn.execute(
                "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY created_at DESC",
                (f"%{q}%", f"%{q}%")
            )
        else:
            cursor = conn.execute("SELECT * FROM notes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [
            Note(id=row["id"], title=row["title"], body=row["body"],
                 created_at=row["created_at"], updated_at=row["updated_at"])
            for row in rows
        ]

@app.get("/notes/{note_id}")
def get_note(note_id: int) -> Note:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="not found")

    return Note(id=row["id"], title=row["title"], body=row["body"],
                created_at=row["created_at"], updated_at=row["updated_at"])

@app.put("/notes/{note_id}")
def update_note(note_id: int, note: NoteUpdate) -> Note:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="not found")

        title = note.title if note.title is not None else row["title"]
        body = note.body if note.body is not None else row["body"]
        now = get_utc_timestamp()

        conn.execute("UPDATE notes SET title = ?, body = ?, updated_at = ? WHERE id = ?",
                     (title, body, now, note_id))
        conn.commit()

    return Note(id=row["id"], title=title, body=body, created_at=row["created_at"], updated_at=now)

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="not found")
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
