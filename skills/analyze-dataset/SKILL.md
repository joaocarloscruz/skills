---
name: analyze-dataset
description: Inspect, clean, explore, summarize, and communicate findings from a structured dataset while preserving provenance and uncertainty. Use when analyzing CSV, tabular, database-export, Parquet, JSON-record, or similar data rather than merely formatting a spreadsheet.
---

# Analyze Dataset

1. Clarify the question, unit of analysis, population, time window, decision context, and acceptable uncertainty.
2. Preserve the source and create a reproducible working copy or query. Record file, table, extraction date, filters, and transformations.
3. Profile schema, types, ranges, missingness, duplicates, keys, category levels, timestamps, encodings, and suspicious sentinel values.
4. Determine the grain before joining or aggregating. Verify row counts and key uniqueness at every transformation.
5. Clean only with explicit rules. Keep raw values, document exclusions, and distinguish missing, zero, unknown, and not applicable.
6. Explore distributions, segments, trends, relationships, and outliers using statistics and visualizations appropriate to the data.
7. Check denominators, sampling, survivorship, seasonality, confounding, multiple comparisons, and whether associations are being mistaken for causes.
8. Validate important results through an independent calculation, reconciliation total, or alternative grouping.
9. Communicate the answer first, followed by evidence, method, uncertainty, limitations, and reproducible artifacts.

Do not manufacture precision or silently repair data. Separate observed facts, analytical choices, and interpretations.
