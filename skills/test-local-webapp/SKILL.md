---
name: test-local-webapp
description: Inspect, exercise, and verify local web applications with browser automation, screenshots, DOM checks, console and network evidence, and focused end-to-end scenarios. Use when testing localhost or file-based web UIs, reproducing frontend bugs, or confirming visual and interactive behavior.
---

# Test Local Web App

## Establish the target

1. Determine whether the app is already running and identify its local URL.
2. If startup is required, inspect the repository's documented development command and use a managed process that can be stopped reliably.
3. Read static HTML directly when sufficient. For dynamic apps, inspect the rendered page after the relevant load state.
4. Do not send credentials, private data, or destructive actions through a test flow without explicit authorization.

## Reconnoiter before acting

1. Open the target and capture the initial page, title, URL, and visible landmarks.
2. Inspect accessible roles, labels, test IDs, and stable DOM structure.
3. Check browser console errors and failed network requests.
4. Choose selectors from observed state. Prefer roles and labels over brittle CSS paths or coordinates.

## Exercise focused scenarios

1. Translate each requested behavior into setup, action, and observable assertion.
2. Wait on explicit UI or network conditions instead of arbitrary delays.
3. Capture evidence at the failure point: screenshot, DOM state, console message, request, response, or trace.
4. Keep scenarios independent and avoid mutating shared or production-like data.
5. Re-run failures to distinguish deterministic defects from timing or environment problems.

## Report

State the environment, scenarios run, observed results, and evidence locations. Separate product defects from test-harness failures. If asked to fix the app, preserve a failing check first and rerun it after the change; otherwise stop after diagnosis and reporting.
