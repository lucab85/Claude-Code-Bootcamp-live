# Production Readiness Review — module-04/winner

**Target:** `module-04/winner/notes.py` (FastAPI + SQLite Notes API)
**Date:** 2026-05-30

---

## 1. Security

**Would it hold up?** No — the search endpoint is exploitable and there is zero authentication.
**Biggest risk:** Unescaped `LIKE` wildcards (`q=%` matches every row; `q=_` fuzzes single chars) — documented in `bug-fix-notes.md:7` but unfixed.
**Smallest next step:** Escape `q` before building `like`: replace `\`, `%`, `_` and append `ESCAPE '\\'` to the SQL predicate (`notes.py:99`).

---

## 2. Observability

**Would it hold up?** No — there is no structured logging, no health endpoint, and no metrics; failures are invisible.
**Biggest risk:** A silent DB error (corrupt file, disk full) returns a 500 with no trace in any alerting system.
**Smallest next step:** Add a `GET /healthz` route that does `SELECT 1` against the DB and returns `{"status":"ok"}` or 503.

---

## 3. Deployment

**Would it hold up?** No — no `Dockerfile`, no `requirements.txt`, no process manager; the README instructs `uvicorn --reload` (dev mode) and SQLite in CWD breaks under any multi-worker setup.
**Biggest risk:** SQLite with a relative `DB_PATH` is not portable and explodes with multiple Uvicorn workers (concurrent write contention / wrong CWD).
**Smallest next step:** Add a `requirements.txt` pinning `fastapi`, `pydantic>=2`, `uvicorn[standard]` — one-minute change that makes the deploy reproducible.

---

## 4. Runbooks

**Would it hold up?** No — the README is 5 lines and documents the wrong HTTP verb (`PUT` instead of `PATCH`).
**Biggest risk:** No backup or restore procedure for `notes.db`; a corrupted file means permanent data loss with no recovery path.
**Smallest next step:** Add a one-paragraph ops note: how to back up the DB (`sqlite3 notes.db ".backup notes.db.bak"`), where it lives, and how to restart the service.

---

## 5. Rollback

**Would it hold up?** No — there is no migration tooling, no schema versioning, and `notes.db` data files are committed to git in `candidate-a/` and `candidate-b/`.
**Biggest risk:** Any schema change requires manual SQLite ALTER or a full DB drop; there is no way to roll back a bad migration without data loss.
**Smallest next step:** Add a `SCHEMA_VERSION` pragma (`PRAGMA user_version = 1`) at init time so future rollback scripts can gate on the DB version.

---

## Verdict

**NO-GO.** Bootcamp learning artifact with known unfixed injection, no auth, no deployment config, and no data recovery path.
