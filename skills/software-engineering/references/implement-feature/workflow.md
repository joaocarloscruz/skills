<!-- Generated from library/implement-feature/SKILL.md; do not edit. -->

# Implement Feature

1. Restate the observable behavior, acceptance criteria, constraints, and non-goals.
2. Read repository instructions and trace the existing path where the behavior belongs.
3. Identify the smallest coherent change and a verification signal that can fail before implementation.
4. Add or update tests at the most faithful stable seam when behavior needs regression protection. For a reversible text or styling change, a focused inspection or rendered check may be sufficient; avoid tests that merely repeat the implementation.
5. Implement incrementally, reusing established abstractions and avoiding speculative generalization.
6. Handle validation, errors, authorization, compatibility, state transitions, and observability relevant to the feature.
7. Run focused checks first, then broader affected checks. Inspect the final diff for scope creep and temporary artifacts.

Report changed behavior, key design decisions, commands run, and remaining risk. Separate pre-existing failures and unavailable checks from regressions, continue independent work, and identify any acceptance criteria that remain unverified.
