<!-- Generated from library/write-sql/SKILL.md; do not edit. -->

# Write SQL

1. Confirm the SQL dialect, environment, schemas, table grain, keys, relationships, time zones, and the exact output grain.
2. Inspect authoritative schema and representative values instead of guessing table or column names.
3. Translate the question into explicit metrics, dimensions, filters, denominators, inclusion rules, and boundary dates.
4. Build in stages with readable common table expressions when they clarify grain or logic.
5. Prevent accidental row multiplication by validating join cardinality before aggregation.
6. Handle nulls, duplicate events, slowly changing dimensions, late data, inclusive date bounds, and time-zone conversion deliberately.
7. Parameterize untrusted values and avoid dynamic identifier construction unless safely allowlisted.
8. Run read-only samples, row-count checks, reconciliation totals, and edge cases. Use explain or dry-run facilities before expensive scans.
9. Optimize only after correctness: reduce scanned columns and partitions, filter early where semantics allow, and verify plan changes.

Return the query, assumptions, expected columns and grain, validation performed, and performance considerations. Never execute writes, DDL, or destructive statements without explicit authorization.
