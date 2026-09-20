# Reconcile an ambiguous write

Implement `submit(remote, payload, key)` in `solution.py`. `payload` is a JSON
dictionary and `key` is the caller's nonempty idempotency key. Neither may change.
The remote exposes only:

- `remote.submit(payload, key)`: returns `{"state": "succeeded", "result": ...}`
  or `{"state": "pending"}`. May instead raise `TimeoutError` before accepting
  anything, after committing the effect, or after accepting pending work.
- `remote.status(key)`: returns `{"state": "absent"}`, `{"state": "pending"}`,
  or `{"state": "succeeded", "result": ...}`. May raise `TimeoutError`.

Return a succeeded response unchanged when its outcome is known. For pending
work return `{"state": "pending", "key": key}`. After an ambiguous submit,
query status before deciding whether to retry. If that first status confirms
absence, retry once with the original payload and key. Retry only after confirmed
absence. Make at most two submit calls
and at most two status calls in one invocation. If status is unavailable, or a
second submit times out and its status is absent, return
`{"state": "unknown", "key": key}` so a caller can reconcile later. Never claim
success without a returned or reconciled result. Do not retry pending work.

Use ordinary Python and the provided objects only: no imports, external I/O,
private attributes, reflection, dynamic code, or decorators. Built-ins available
are `dict`, `list`, `tuple`, `set`, `len`, `range`, `enumerate`, `zip`, `sorted`,
`min`, `max`, `sum`, `str`, `int`, `float`, `bool`, `isinstance`, `all`, `any`,
`Exception`, `TimeoutError`, `RuntimeError`, `ValueError`, and `KeyError`.

`fixture.json` shows an example input and a possible successful receipt. Other
payloads, keys, receipts, and timeout boundaries will be used when grading.
