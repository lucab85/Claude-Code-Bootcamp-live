# Notes API
Install: `pip install fastapi 'pydantic>=2' uvicorn`
Run: `uvicorn notes:app --reload` (SQLite file `notes.db` auto-created in CWD).
Endpoints: `POST /notes`, `GET /notes?q=`, `GET /notes/{id}`, `PUT /notes/{id}`, `DELETE /notes/{id}`.
Status: 201 create, 200 read/update, 204 delete, 404 missing, 422 invalid body; timestamps ISO 8601 UTC.
