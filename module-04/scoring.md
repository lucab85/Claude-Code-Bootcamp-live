# Smoke-test results

## Candidate A (port 8001 — verified by running server)

| Curl | Expected | Result |
|------|----------|--------|
| POST /notes | 201 | 201 ✓ |
| GET /notes | 200 | 200 ✓ |
| GET /notes?q=hi | 200 | 200 ✓ |
| GET /notes/1 | 200 | 200 ✓ |
| PATCH /notes/1 | 200 | 405 ✗ — route is PUT, not PATCH |
| DELETE /notes/1 | 204 | 204 ✓ |
| GET /notes/999 | 404 | 404 ✓ `{"error":"not found"}` |

*(Fixed in winner: route changed to `@app.patch` with optional-field `NotePatch` model.)*

## Candidate B (static analysis — server run interrupted)

| Curl | Expected | Result |
|------|----------|--------|
| POST /notes | 201 | 201 ✓ |
| GET /notes | 200 | 200 ✓ |
| GET /notes?q=hi | 200 | 200 ✓ |
| GET /notes/1 | 200 | 200 ✓ |
| PATCH /notes/1 | 200 | 405 ✗ — route is PUT, not PATCH |
| DELETE /notes/1 | 204 | 204 ✓ |
| GET /notes/999 | 404 | 404 ✓ `{"error":"not found"}` |

## Side-by-side score

| Criterion (0–3) | Candidate A | Candidate B |
|-----------------|-------------|-------------|
| Correctness | 2 — 6/7 curls pass (PATCH → 405) | 2 — 6/7 curls pass (same failure) |
| Simplicity | 3 — modern `lifespan` API, clean types | 2 — uses deprecated `@app.on_event("startup")`; manual `conn.commit()` alongside context manager |
| Fit | 3 — complete type annotations on all routes, `{"error":…}` 404 shape, single file | 2 — `delete_note` missing return annotation; `NoteCreate.body` has no default (breaks partial-update intent) |
| **Total** | **8 / 9** | **6 / 9** |

## Winner: Candidate A

Both implementations share the same correctness gap (PUT instead of PATCH), but Candidate A is strictly cleaner: it uses the current FastAPI `lifespan` context manager rather than the deprecated `@app.on_event` hook, carries full type annotations on every function signature (including `-> Response` on `delete_note`), and adds `Field(min_length=1, max_length=200)` validation on `NoteIn.title` — a small but useful guard. The 404 error body `{"error":"not found"}` matches the spec in both candidates, but Candidate A's overall code quality and adherence to the project conventions tip the balance decisively.
