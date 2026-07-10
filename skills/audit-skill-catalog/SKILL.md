---
name: audit-skill-catalog
description: Audit agent skills for structural defects, unsafe instructions, routing, and portability.
---

# Audit Skill Catalog

## Establish scope

1. Identify the catalog root, supported agent runtimes, portability goals, licensing policy, and whether executable resources are allowed.
2. Read the repository's authoring and contribution guidance before applying generic rules.
3. Treat installed skills as third-party code: do not execute bundled scripts during an audit unless their behavior has been reviewed and execution is separately authorized.

## Run deterministic checks

Run the bundled auditor against the catalog root:

```bash
python "<skill-path>/scripts/audit_catalog.py" "<catalog-root>"
```

Run `--help` for JSON output, overlap thresholds, and warning-sensitive exit behavior. The script checks frontmatter, names, descriptions, duplicate identities, size, broken relative links, unused resources, risky instruction patterns, and lexical trigger overlap.

Treat warnings as investigation leads. Text similarity is not proof of conflicting activation, and a risky command may appear inside a prohibition or safety example.

## Review behavior and governance

1. Compare descriptions pairwise for requests that could activate multiple skills. Rewrite boundaries before adding more routing text to the bodies.
2. Check whether each skill represents one repeatable workflow with observable completion criteria.
3. Move optional variants and detailed knowledge into directly linked references; move repeated deterministic operations into reviewed scripts.
4. Verify that instructions preserve user authority, separate read and write paths, avoid secret exposure, and require approval for destructive or externally visible actions.
5. Trace copied or adapted material to its source and confirm license, attribution, modification notices, and redistribution terms.
6. Check current documentation for tool- or version-specific claims and label unsupported runtimes or dependencies.
7. Review evidence from real usage: misactivations, missed activations, repeated mistakes, unnecessary context, and failed verification.

## Report

Order findings by impact and confidence. For each finding, cite the skill and exact evidence, explain the failure scenario, and recommend whether to revise, split, merge, remove, or add a resource. Separate structural errors, security risks, routing conflicts, maintainability concerns, and speculative improvements.

Do not auto-fix a catalog during an audit-only request. A clean structural report does not prove that the skills improve agent behavior; recommend realistic forward tests for high-impact or heavily used skills.
