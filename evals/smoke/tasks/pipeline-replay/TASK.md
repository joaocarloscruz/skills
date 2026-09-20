# Restartable event delivery

Implement `sync(events, sink, checkpoints)` in `solution.py`. Return `None` after
all events are durably delivered. `events` is an ordered list of dictionaries
with strictly increasing positive integer `sequence`, unique string `id`, and a
JSON `value`. Sequence numbers may have gaps. The complete feed is replayed on
every call; an empty feed is valid.

The collaborators provide these methods:

- `checkpoints.load()` returns the last acknowledged sequence, initially zero.
- `sink.put(event_id, value)` durably stores that value by ID. Repeating the same
  ID and value is idempotent. It returns `None`.
- `checkpoints.save(sequence)` durably advances the acknowledged sequence.
  Every event at or below it must already be durable in the sink.

Either write may raise `TimeoutError` immediately before or immediately after
its durable effect. Let the error escape; the caller will restart `sync` with
the same feed and durable sink/checkpoint state. Recovery must neither lose
events nor create additional logical records. Do not modify input events. Skip
events covered by the loaded checkpoint; calling sync on a fully acknowledged
feed must perform no writes. Do not reset, delete, or bypass durable state.

Use ordinary Python and the provided objects only: no imports, external I/O,
private attributes, reflection, dynamic code, or decorators. Built-ins available
are `dict`, `list`, `tuple`, `set`, `len`, `range`, `enumerate`, `zip`, `sorted`,
`min`, `max`, `sum`, `str`, `int`, `float`, `bool`, `isinstance`, `all`, `any`,
`Exception`, `TimeoutError`, `RuntimeError`, `ValueError`, and `KeyError`.

For `fixture.json`, a successful run from checkpoint zero stores both event IDs
with their given values and acknowledges sequence 4.
