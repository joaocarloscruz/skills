---
name: build-frontend-interface
description: Implement production web pages, components, forms, responsive layouts, and client behavior.
---

# Build Frontend Interface

## Understand the implementation contract

1. Read repository instructions, manifests, routes, design tokens, component libraries, tests, and nearby implementations.
2. Identify supported browsers, rendering model, data sources, authentication boundaries, localization, and accessibility requirements.
3. Translate the request into observable states and interactions, including loading, empty, error, disabled, success, offline, and permission behavior.
4. Preserve an existing visual system. If no direction exists and design judgment is material, establish it before implementation.
5. For React or Next.js, read `references/react.md` after confirming the installed versions and rendering model.

## Build the smallest coherent structure

1. Start with semantic document structure and content order.
2. Reuse established tokens, primitives, and components when their behavior fits; do not force reuse that breaks the requested contract.
3. Split components at meaningful behavior or reuse boundaries, not arbitrary line counts.
4. Keep data fetching, server state, URL state, form state, and transient UI state in the narrowest appropriate owner.
5. Prefer explicit variants and composition over growing collections of boolean props.
6. Treat responsive behavior as content adaptation: define what reflows, wraps, collapses, scrolls, moves, or becomes progressively disclosed.

## Implement complete behavior

- Use native semantics before custom roles and preserve keyboard operation and focus behavior.
- Connect labels, descriptions, errors, and status announcements to the controls they explain.
- Prevent duplicate submissions and define cancellation, retry, optimistic updates, and stale data behavior where applicable.
- Keep secrets and trusted authorization decisions out of client code.
- Avoid layout shifts, unnecessary client JavaScript, request waterfalls, unbounded rendering, and heavy media without a loading strategy.
- Use real representative content instead of placeholder text that hides wrapping and overflow failures.

## Verify the rendered result

1. Run type, lint, and focused tests using repository commands.
2. Exercise the primary journey and important failures in a real browser.
3. Inspect narrow and wide viewports, keyboard navigation, focus visibility, zoom, reduced motion, console errors, and failed requests.
4. Compare against the approved design or neighboring product surfaces using screenshots when possible.
5. Inspect the final diff for duplicated styling, dead code, debug artifacts, and scope creep.

Report implemented behavior, component and state decisions, commands run, browser evidence, and remaining risk. Do not claim visual or interaction completion from compilation alone.
