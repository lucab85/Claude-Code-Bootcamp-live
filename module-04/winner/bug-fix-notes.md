# Bug Review: module-04/winner Notes API

Bugs ranked by severity.

---

## 1. HIGH — LIKE wildcard injection in search (`notes.py:99`)

`q` is wrapped in `%…%` with no escaping. A caller passing `q=%` matches every row; `q=_` matches any single character. Search semantics are silently broken for any user input containing `%` or `_`.

**Smallest fix:** escape before building `like`:
```python
like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
```
and append `ESCAPE '\\'` to the SQL predicate.

---

## 2. MEDIUM — TOCTOU race → 500 in `update_note` (`notes.py:121–131`)

The existence check (SELECT, no lock) and the write (UPDATE, acquires write lock) are on different implicit transactions within the same connection context. A concurrent DELETE on a second connection can slip in between the two: the UPDATE runs against a now-deleted row (`rowcount = 0`), the final SELECT returns `None`, and `row_to_note(None)` raises `TypeError` → HTTP 500 instead of 404.

**Smallest fix:** check `rowcount` after the UPDATE and raise 404 if it is 0, eliminating the need for the re-fetch-or-die path.

---

## 3. LOW — Connection never explicitly closed (`notes.py:20–23`)

`get_conn()` opens a connection; `with conn:` only commits/rolls back — it does **not** close. The file handle is released only on GC. Fine for CPython (reference counting), but can exhaust file descriptors under load or on PyPy.

**Smallest fix:** use `contextlib.closing` or add `conn.close()` in a `finally` block, or switch to a context-manager wrapper that both commits and closes.

---

## 4. LOW — README documents PUT, code exposes PATCH (`README.md:4`)

Any client following the README will get a `405 Method Not Allowed`.

**Smallest fix:** change `PUT /notes/{id}` → `PATCH /notes/{id}` in the README.

---

## 5. INFO — SQLite LIKE is case-insensitive for ASCII only (`notes.py:101`)

`test_search_case_insensitive_like` passes because it uses ASCII. For non-ASCII titles/bodies (e.g. `"Über"` searched as `"über"`), SQLite's LIKE won't match. This is a latent correctness gap, not a crash.

**Smallest fix:** call `conn.create_function("LOWER", 1, str.lower)` and use `LOWER(title) LIKE LOWER(?)` — or accept the limitation and document it.
