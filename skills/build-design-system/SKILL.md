---
name: build-design-system
description: Create or evolve reusable frontend design foundations, including semantic tokens, themes, primitives, component APIs, variants, interaction states, accessibility contracts, documentation, versioning, and adoption. Use when building a shared UI library or standardizing inconsistent interfaces across products.
---

# Build Design System

## Establish scope and evidence

1. Inventory existing products, styles, tokens, components, duplicated patterns, supported platforms, and consuming teams.
2. Gather representative interface examples and identify where differences express real product needs versus accidental inconsistency.
3. Define the system's consumers, governance, compatibility promises, packaging constraints, and success measures.
4. Start with high-frequency, high-friction foundations and components rather than attempting an exhaustive catalog.

## Build foundations

1. Define primitive scales only where needed: color, type, spacing, size, radius, border, shadow, motion, and breakpoints.
2. Expose semantic tokens named by role and state rather than raw appearance, such as `text-danger` instead of `red-600`.
3. Model themes as semantic token substitutions. Verify contrast and state differentiation in every supported theme.
4. Document responsive, density, localization, reduced-motion, high-contrast, and platform behavior.
5. Keep token sources machine-readable and generate downstream formats when multiple platforms consume them.

## Build primitives and components

1. Implement accessible primitives for focus, overlays, keyboard interaction, labeling, and announcements before styled composites.
2. Define each component's purpose, anatomy, content rules, states, variants, responsive behavior, and composition boundaries.
3. Prefer a small set of explicit variants and slots over boolean-prop combinations.
4. Preserve escape hatches for valid composition without exposing internal DOM or styling as accidental public API.
5. Test default, hover, focus, active, disabled, loading, empty, error, selected, overflow, long-content, and localized states as applicable.

## Govern change

- Publish usage guidance with do, do-not, and selection examples; do not document props without explaining decisions.
- Add visual, interaction, accessibility, and API contract tests for supported variants.
- Version breaking changes, provide migrations or codemods when worthwhile, and define deprecation windows.
- Track adoption and exceptions. Feed recurring exceptions back into the system without turning every request into a variant.
- Keep application-specific composition in applications until repeated evidence justifies promotion.

Deliver the foundations, component priorities, public contracts, testing strategy, distribution plan, migration path, and unresolved governance decisions. A design system is successful when it improves consistency and delivery without blocking legitimate product differences.
