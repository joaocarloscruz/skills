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

When a profile depends on an account but preferences do not, start preferences and the account together; chain the profile to the account instead of waiting for both initial reads:

```javascript
const accountTask = readAccount(accountId);
const preferencesTask = readPreferences(accountId);
const profileTask = accountTask.then(account => readProfile(account.profileId));
const [account, preferences, profile] = await Promise.all([
  accountTask, preferencesTask, profileTask,
]);
```

These are illustrative function names, not framework APIs. Only parallelize independent, authorized operations; preserve required ordering for mutations. Handle cancellation and partial failure according to the page's contract.

Do not treat React `cache` as a persistent application cache: its documented server-rendering scope differs from a shared process cache or a framework data cache. Before sharing cached data across requests, establish tenant/user keys, authorization, invalidation, lifetime, memory bounds, and deployment behavior.

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

Do not move an input change into a transition: keep the controlled input update immediate and defer the expensive derived view when the installed React version supports it. For a filtered list, derive `visibleItems` from items and the filter; use an Effect only for synchronization with an external system, not to maintain a redundant copy of that derived list.

Prefer documented package exports. A deep import that reduces modules but loses type declarations or violates the package's export map is not a valid optimization. Check the framework's existing import optimization before rewriting imports.

## Verify

Test behavior through user-visible roles and interactions. Include server and client rendering paths, navigation, mutation success and failure, cache invalidation, and hydration. Profile actual renders and bundles before claiming a performance improvement.

## Primary references

- [React: effects and derived state](https://react.dev/learn/you-might-not-need-an-effect)
- [React: cache scope and limitations](https://react.dev/reference/react/cache)
- [React: useTransition restrictions](https://react.dev/reference/react/useTransition)
- [Next.js: optimizePackageImports](https://nextjs.org/docs/app/api-reference/config/next-config-js/optimizePackageImports)

Check the documentation for the installed versions before using version-specific APIs. These examples are original guidance, not imported upstream rules or measured performance claims.
