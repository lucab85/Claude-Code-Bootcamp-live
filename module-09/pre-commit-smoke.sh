#!/usr/bin/env bash
# Pre-commit smoke-test hook for module-09/notes.py
# Invoked by Claude Code PreToolUse on every Bash call.
# Reads CLAUDE_TOOL_INPUT (JSON) and exits 0 immediately if the command is
# not a git commit, then runs the notes-api-smoke check and blocks on FAIL.

set -uo pipefail

TOOL_INPUT="${CLAUDE_TOOL_INPUT:-{}}"
CMD=$(python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('command',''))" <<<"$TOOL_INPUT")

if [[ "$CMD" != *"git commit"* ]]; then
  exit 0
fi

echo "==> pre-commit hook: running notes-api-smoke for module-09 ..."

APP_DIR="module-09"
APP_MODULE="notes:app"
PORT=8766
BASE="http://localhost:${PORT}"

uv run --with fastapi --with uvicorn \
  uvicorn "${APP_MODULE}" --app-dir "${APP_DIR}" \
  --port "${PORT}" --log-level warning &
SERVER_PID=$!
trap 'kill "${SERVER_PID}" 2>/dev/null; wait "${SERVER_PID}" 2>/dev/null' EXIT

READY=0
for i in $(seq 1 20); do
  curl -sf "${BASE}/docs" >/dev/null 2>&1 && { READY=1; break; }
  sleep 0.5
done

if [ "${READY}" -eq 0 ]; then
  echo "FAIL  server did not start within 10 s"
  exit 1
fi

PASSED=0
FAILED=0

check() {
  local label="$1" expected="$2" actual="$3"
  if [ "${actual}" = "${expected}" ]; then
    echo "PASS  ${label}"
    PASSED=$((PASSED + 1))
  else
    echo "FAIL  ${label}  (expected ${expected}, got ${actual})"
    FAILED=$((FAILED + 1))
  fi
}

BODY_FILE=$(mktemp)
STATUS=$(curl -s -o "${BODY_FILE}" -w "%{http_code}" -X POST "${BASE}/notes" \
  -H "Content-Type: application/json" -d '{"title":"smoke","body":"test"}')
check "POST /notes → 201" 201 "${STATUS}"
NOTE_ID=$(python3 -c "import json; print(json.load(open('${BODY_FILE}'))['id'])" 2>/dev/null || echo "0")
rm -f "${BODY_FILE}"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/notes")
check "GET /notes → 200" 200 "${STATUS}"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/notes/${NOTE_ID}")
check "GET /notes/${NOTE_ID} → 200" 200 "${STATUS}"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "${BASE}/notes/${NOTE_ID}" \
  -H "Content-Type: application/json" -d '{"title":"updated"}')
check "PATCH /notes/${NOTE_ID} → 200" 200 "${STATUS}"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "${BASE}/notes/${NOTE_ID}")
check "DELETE /notes/${NOTE_ID} → 204" 204 "${STATUS}"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/notes/999")
check "GET /notes/999 → 404" 404 "${STATUS}"

echo ""
echo "Results: ${PASSED} passed, ${FAILED} failed."

if [ "${FAILED}" -gt 0 ]; then
  echo ""
  echo "COMMIT BLOCKED: smoke test found ${FAILED} failure(s). Fix the API before committing."
  exit 1
fi
exit 0
