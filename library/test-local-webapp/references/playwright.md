# Playwright execution and readiness

Use only when Playwright is an available, permitted interface. Identify whether the task needs an exploratory browser session or durable test files; use the environment's tool/CLI for the former and the repository's installed runner for the latter. Do not assume an external skill's shell wrapper works on every host.

## Reuse the actual environment

- Check the documented startup command and URL. Prefer the existing server when it is the intended instance; distinguish a port accepting connections from the correct app being ready.
- For Playwright Test, the configured `webServer` facility can own startup and shutdown. Check its installed-version options and CI reuse behavior. Otherwise track the process tree and terminate only processes started for this task.
- On PowerShell, use native quoting and process management or an explicitly available Bash environment. Do not paste a POSIX shell lifecycle wrapper into an incompatible shell.
- Use isolated contexts/test accounts and reset fixtures between scenarios. Preserve authorized user sessions when the environment's browser tools require them rather than replacing the browser interface arbitrarily.

## Wait for the claim being tested

For a saved setting, assert the visible saved state or a fresh server read after submission. Network silence does not prove that rendering or persistence finished; polling/analytics can also prevent silence indefinitely. Avoid blanket `networkidle` and fixed-delay readiness rules.

Illustrative Playwright Test assertions, using observed accessible names:

```typescript
await page.getByLabel("Display name").fill("Example team");
await page.getByRole("button", { name: "Save changes" }).click();
await expect(page.getByRole("status")).toHaveText("Changes saved");
```

Substitute the real labels and outcome; do not invent selectors from this example. This only verifies the displayed success state. If persistence is the requirement, reload or read through the appropriate boundary and assert the stored value too.

Playwright's awaited locator assertions retry until their condition or timeout. An immediate `expect(await locator.textContent()).toBe(...)` does not gain the same retry behavior. In a snapshot-reference CLI, refresh the snapshot after navigation or substantial DOM changes and use identifiers from observed state.

## Capture useful failures

Record the failing step, URL, viewport, screenshot/trace when supported, relevant console output, and failed requests with sensitive fields removed. A screenshot cannot establish keyboard behavior; exercise Tab, activation, dialogs, and focus restoration explicitly when in scope. Keep browser failures distinct from an app startup or test-runner error.

## Primary references

- [Playwright: retrying assertions](https://playwright.dev/docs/test-assertions)
- [Playwright: web server lifecycle](https://playwright.dev/docs/test-webserver)
- [Playwright: load-state caveats](https://playwright.dev/docs/api/class-page#page-wait-for-load-state)
- [Playwright: locators](https://playwright.dev/docs/locators)
