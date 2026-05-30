# AI-Generated Code Review Rubric

Quick yes/no checks — each should take ≤ 30 seconds. One "No" = investigate before merging.

---

## 1. Boundaries
**Does every loop, slice, and index account for the empty case and the last element?**
Look for `list[0]`, `range(len(...))`, and off-by-one in slice endpoints. Empty input and single-element input are the most common missed cases.

## 2. Error paths
**Does every failure branch return/raise something, not silently continue?**
Scan for bare `except:`, functions that fall off the end on error, and `if err` checks with no `else`. AI-generated code often handles the happy path completely and forgets the sad path entirely.

## 3. Type assumptions
**Does the code handle `None`, `0`, `""`, and `[]` wherever a value is consumed?**
Check every place a return value or argument is used without a guard. AI often assumes a function returns a non-None value because the happy-path docs say so.

## 4. Mutation of inputs
**Are inputs (lists, dicts, objects) ever mutated in-place when the caller likely expects them unchanged?**
Look for `.append()`, `.update()`, `.pop()`, `del` on parameters. Silent mutation is a common source of action-at-a-distance bugs.

## 5. Integer / numeric edge cases
**Does the code handle `0` as a divisor, negative numbers as counts, and overflow in arithmetic?**
Check division, modulo, and any place a user-supplied number is used as a size or index.

## 6. Resource cleanup
**Is every opened file, connection, or lock closed under all exit paths, including exceptions?**
Confirm `with` blocks or explicit `finally` clauses. AI often opens correctly but skips cleanup on early-return or exception paths.

## 7. Implicit ordering / uniqueness
**Does the code assume a collection is sorted, deduplicated, or non-empty without enforcing it?**
Look for `sorted_list[0]` or set-membership logic on plain lists. AI frequently inherits an assumption from the problem description that the actual data won't satisfy.

## 8. Untrusted input used directly
**Is any user-supplied or external value used in a file path, shell command, SQL query, or format string without sanitization?**
One-pass grep for `subprocess`, `open(`, `f"...{var}..."` inside formatted queries, and any string concatenation feeding an external system.

---

*If all eight pass: approve. If any fail: leave an inline comment at the exact line before merging.*
