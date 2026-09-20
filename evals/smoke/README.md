# Behavioral development smoke

These three small tasks exercise observable failure modes. They do not invoke a
model, measure native skill activation, or establish that one skill is generally
better. Prepare an independent directory for each task and condition, give the
runner only that directory and the selected skill, then grade the saved artifact.
Do not show the `private/` graders or their tests to a runner before submission.
That separation is procedural: agents sharing a filesystem are not isolated.

```bash
python evals/smoke/run.py prepare sql-grain /tmp/sql-trial
python evals/smoke/run.py grade sql-grain /tmp/sql-trial
python evals/smoke/run.py prepare pipeline-replay /tmp/pipeline-trial
python evals/smoke/run.py grade pipeline-replay /tmp/pipeline-trial
python evals/smoke/run.py prepare tool-write-recovery /tmp/tool-trial
python evals/smoke/run.py grade tool-write-recovery /tmp/tool-trial
python -m unittest discover -s evals/smoke -p "test_*.py"
```

Preparation refuses an existing destination. Grading prints JSON and exits zero
only when every case passes. SQL runs against two private in-memory datasets with
an authorizer that permits only reads. Pipeline cases report injected and
unreached faults: intermediate checkpoint writes are optional, so a valid batched
implementation need not encounter every proposed fault. Every actual checkpoint
is checked for missing data, and final durable state is checked after replay.
Python tasks use a deliberately small
no-import contract: ordinary functions, loops, exceptions and built-in data
structures; no private attributes, reflection, dynamic code or external I/O.
Artifacts run in a fresh subprocess with a five-second timeout, no shell, and a
temporary working directory. This limits accidental effects; it is not an OS
security sandbox. Grade trusted development artifacts only. On Unix the worker
also applies CPU and address-space limits when available; Windows uses the
wall-clock timeout and the restricted contract.

Use this request verbatim, substituting the prepared directory:

> Read TASK.md and fixture.json in DIRECTORY. Implement the requested artifact
> there, using only the public task contract. Do not inspect evals/smoke/private,
> test_smoke.py, other trials, or expected answers. Check your work against the
> visible example. Report the artifact path and any limitations.

For a skill condition, add the selected canonical skill path and ask the runner
to read it and any applicable package references. For a baseline condition, do
not provide that skill. Keep other settings fixed, use fresh contexts, preserve
failed outputs, and record actual model/harness identity and package digest.
These short tasks and public graders can become familiar to development agents;
use separate held-out tasks for claims of improvement. Grades count task
outcomes, not mentions of preferred terminology or instructions.
