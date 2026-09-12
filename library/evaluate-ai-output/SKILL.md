---
name: evaluate-ai-output
description: Evaluate AI outputs with representative datasets, rubrics, checks, human judgment, and regressions.
---

# Evaluate AI Output

1. Define the decision the evaluation must support and the failure costs it should reveal.
2. Build a representative dataset with normal, boundary, adversarial, multilingual, and previously failing cases as appropriate. Keep a held-out set.
3. Turn vague quality goals into observable rubric dimensions with examples of pass, partial, and fail.
4. Use deterministic checks for facts that can be computed. Use blinded human or model grading only for subjective dimensions, and calibrate graders on shared examples.
5. Record model, prompt, tools, parameters, data version, grader revision, and environment for every run. Preserve failed and interrupted trials; do not silently retry them out of the denominator.
6. Compare the same task and repetition under the same conditions. Repeat stochastic trials and report task-level uncertainty, cost, critical failures, and slice-level regressions rather than one aggregate score.

For a skill or prompt comparison, read [the paired evaluation protocol](references/paired-evaluation.md). It defines a complete result format and a runnable comparison with `scripts/compare_runs.py`. The helper validates recorded artifacts and summarizes results; it does not call a model or verify that the runner isolated its environment.

Keep grader answers and held-out tasks out of the agent workspace. Calibrate subjective grading without revealing the condition. Establish the meaningful improvement and acceptable cost before examining final results. A small pilot is a smoke check; neither a valid JSON file nor a positive point estimate establishes broad superiority. Respect the user's deployment authorization separately from the evaluation result.
