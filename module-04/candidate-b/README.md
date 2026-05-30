# Notes API

A simple Notes API with FastAPI and SQLite persistence. All data is stored in `notes.db` and the schema initializes at startup.

## Run

```bash
pip install fastapi uvicorn pydantic
python notes.py
```

API runs on `http://localhost:8000`. View interactive docs at `/docs`.
