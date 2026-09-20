# Paired evaluation protocol

Use this when comparing an existing skill, a candidate skill, or no skill on repeated tasks. For another AI-output task, retain its domain-specific grader and adapt the same pairing and evidence principles.

1. Define the population of tasks, executable acceptance criteria, critical failures and acceptable cost before collecting results. Create development and held-out task sets. Do not optimize on the held-out results.
2. Compare no skill, the existing revision and the candidate with the same model, parameters, tools, project snapshot and budget. Use fresh workspaces and reset external state. Pin tool versions and hash any uncommitted skill package, including references. Record how the runner disables unrelated global skills and prevents access to graders. The comparison script cannot enforce runner isolation.
3. Test natural discovery separately from explicitly loading a skill. Otherwise a missed trigger is indistinguishable from ineffective instructions. Include short requests, nearby intents, compound work and requests that should use no skill.
4. Freeze the task/repetition plan before collecting results and run every planned cell in every condition. Randomize execution order if environment drift matters. Retain timeouts, failures and refusals as outcomes; document harness faults and rerun all affected paired cells consistently. Extra repetitions reduce sampling noise but do not create additional independent tasks.
5. Grade executable acceptance checks first. Blind subjective graders to condition, calibrate them and inspect disagreements. Store transcripts, diffs, grader output and resource measurements. Grading instructions must not be visible to the agent being evaluated.
6. Compare paired results and examine regressions before choosing an outcome. Ten varied tasks with three repetitions per condition can screen a candidate; choose a larger sample based on observed variance and the decision's stakes. Do not present that pilot size as a universal statistical threshold.

The helper takes JSON containing these fields:

```json
{
  "schema_version": 2,
  "kind": "behavioral",
  "experiment": {
    "model": "exact-model-version",
    "harness": "runner-name@revision",
    "environment": "OS, project revision, isolation and reset procedure",
    "tools": ["tool@version"],
    "parameters": {"reasoning": "record actual setting", "budget": "record actual budget"},
    "dataset_revision": "task-set revision or content hash",
    "grader_revision": "grader revision or content hash"
  },
  "conditions": {
    "no-skill": {"skill_revision": "none", "description": "Same tools; target skill absent"},
    "candidate": {"skill_revision": "commit or full package content hash", "description": "Exact candidate package"}
  },
  "planned_tasks": [{"task_id": "example", "repeats": [1]}],
  "results": [
    {"task_id": "example", "repeat": 1, "condition": "no-skill", "success": false,
     "seconds": 12.5, "tokens": null, "artifact": "artifacts/baseline.json", "critical_failures": []},
    {"task_id": "example", "repeat": 1, "condition": "candidate", "success": true,
     "seconds": 13.2, "tokens": null, "artifact": "artifacts/candidate.json", "critical_failures": []}
  ]
}
```

This is a format example, not measured results. Use `kind: synthetic` for fabricated data used to test the helper. Each artifact must be an existing file beneath the result JSON's directory, with a canonical relative path and no symlink/junction traversal inside that directory. An artifact can be a structured record pointing to the transcript, grader checks and produced diff. The helper verifies the directly referenced file's existence, not nested pointers, its truth, or grading quality. Unknown duration or tokens are `null`, never zero. Successful trials cannot contain critical failures.

Schema version 2 requires unique `planned_tasks`, each with a non-empty list of unique positive integer `repeats`. Every condition must match that plan exactly, so even a task missing from all conditions is rejected. Preserve the original plan and its revision; rewriting the plan to match surviving results defeats this check. Legacy version 1 results remain readable but have unverified plan coverage and a warning about symmetric omissions.

Run the script from this skill's directory, or use its absolute path:

```text
python scripts/compare_runs.py /path/to/results.json --baseline no-skill --candidate candidate --output /path/to/comparison.json
```

Success rates weight each task equally, average its repetitions, and bootstrap whole task clusters with a fixed seed. The descriptive 95% interval is omitted for one task and may be unstable or degenerate with small or homogeneous samples. It does not cover systematic bias, grader error or nonrepresentative tasks. Cost averages weight observed paired trials equally, use only pairs with both measurements, and report coverage; tasks with more repetitions therefore contribute more to cost averages. Inspect every candidate critical failure and lost success. Output may replace an earlier comparison file but cannot overwrite the input experiment or a directly referenced trial artifact. The script never declares a winner, changes the evidence registry, calls a model, or authorizes deployment.

Primary methodology reference: [OpenAI's skill evaluation guide](https://developers.openai.com/blog/eval-skills) separates outcome, process, style and efficiency checks. The repository's actual experiments must establish their own evidence.
