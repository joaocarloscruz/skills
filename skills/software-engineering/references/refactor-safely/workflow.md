<!-- Generated from library/refactor-safely/SKILL.md; do not edit. -->

# Refactor Safely

1. Define the structural problem and the behavior that must remain unchanged.
2. Establish a green baseline and add characterization tests where important behavior is not protected.
3. Choose one structural objective and identify the smallest reversible transformation toward it.
4. Separate moves and renames from semantic edits so diffs remain reviewable.
5. Keep the system runnable after each step; run focused checks frequently.
6. Preserve public contracts, serialization, data, timing assumptions, and error behavior unless explicitly in scope.
7. Remove obsolete paths only after all callers and runtime references are verified.

Report the structural improvement and evidence of preserved behavior. Avoid speculative abstractions and unrelated cleanup.
