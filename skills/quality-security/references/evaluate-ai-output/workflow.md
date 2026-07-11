<!-- Generated from library/evaluate-ai-output/SKILL.md; do not edit. -->

# Evaluate AI Output

1. Define the decision the evaluation must support and the failure costs it should reveal.
2. Build a representative dataset with normal, boundary, adversarial, multilingual, and previously failing cases as appropriate. Keep a held-out set.
3. Turn vague quality goals into observable rubric dimensions with examples of pass, partial, and fail.
4. Use deterministic checks for facts that can be computed. Use blinded human or model grading only for subjective dimensions, and calibrate graders on shared examples.
5. Record model, prompt, tools, parameters, data version, and environment for every run.
6. Compare paired outputs, report confidence and slice-level regressions, and inspect disagreements rather than relying on one aggregate score.

Prevent test leakage and rubric gaming. Recommend deployment only when gains are meaningful on relevant slices and critical regressions are understood.
