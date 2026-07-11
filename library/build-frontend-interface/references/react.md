# React and Next.js

Read this reference only after confirming the project's React, framework, router, and data-library versions. Follow repository conventions and installed APIs over remembered defaults.

## Choose boundaries deliberately

- Keep server-capable rendering and data access on the server when it reduces client code and preserves security.
- Add a client boundary only where browser APIs, local interaction, or client state require it.
- Pass minimal serializable data across server and client boundaries.
- Authenticate server actions and mutations as independently as API endpoints.

## Avoid request waterfalls

- Start independent work together and await it near the point of use.
- Fetch at the owner that can coordinate dependencies rather than in deeply nested components by default.
- Use streaming boundaries for independently useful regions when supported.
- Deduplicate repeated reads with the project's supported cache mechanism and understand its request, process, and deployment scope.

## Place state by meaning

- Derive values during rendering instead of synchronizing redundant state with effects.
- Use URL state for shareable navigation, filters, sorting, and pagination.
- Use the established server-state library for remote caching and invalidation.
- Keep transient interaction state local; lift it only to the nearest shared owner.
- Reserve broad context or global stores for genuinely cross-cutting state with clear update behavior.

## Design component APIs

- Prefer children, slots, compound components, and explicit variants over many boolean switches.
- Keep providers responsible for state implementation and expose a small stable interface.
- Avoid defining component types inside render functions.
- Preserve ref, focus, event, and controlled or uncontrolled contracts when wrapping primitives.

## Control rendering and bundles

- Measure before adding memoization. Remove expensive repeated work or over-broad subscriptions first.
- Keep effect dependencies truthful and move user-triggered work into event handlers.
- Import directly when barrel files pull large module graphs into the bundle.
- Defer heavy optional features and non-critical third-party scripts.
- Prevent hydration mismatches by making server and initial client output agree.

## Verify

Test behavior through user-visible roles and interactions. Include server and client rendering paths, navigation, mutation success and failure, cache invalidation, and hydration. Profile actual renders and bundles before claiming a performance improvement.
