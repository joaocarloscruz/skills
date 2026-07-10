---
name: design-frontend-interface
description: Define or improve the visual direction, information hierarchy, interaction behavior, responsive experience, motion, and interface copy for a web UI. Use when designing or redesigning product screens, dashboards, landing pages, marketing sites, or frontend prototypes before or alongside implementation.
---

# Design Frontend Interface

## Establish intent

1. Identify the actual person, their immediate context, the task they must complete, and what happens before and after this interface.
2. State the interface's single primary job and the feeling appropriate to it. Reject empty descriptions such as "clean and modern."
3. Inspect existing brand guidance, design tokens, components, content, screenshots, and neighboring screens before proposing a new direction.
4. Classify the surface:
   - Read `references/product-ui.md` for applications people operate repeatedly, including dashboards, settings, forms, and internal tools.
   - Read `references/marketing-ui.md` for landing pages, campaigns, launches, and public narrative experiences.
   - Read both when a product combines acquisition and application surfaces.

## Define the direction

Produce a compact design brief containing:

- content hierarchy and the primary action;
- domain concepts, materials, vocabulary, and imagery that belong specifically to the subject;
- a restrained color, typography, spacing, and depth system;
- one signature visual or interaction idea that supports the task;
- navigation and responsive behavior;
- loading, empty, error, disabled, success, and permission states;
- motion purpose, reduced-motion behavior, and performance constraints;
- three likely generic defaults and the specific alternatives replacing them.

Every choice must connect to the audience, content, brand, or task. Do not use novelty as a substitute for usability.

## Critique before delivery

1. Check whether the design remains identifiable when the product name is removed.
2. Inspect hierarchy at a glance and at narrow widths.
3. Verify real content lengths, keyboard focus, contrast, touch targets, zoom, and reduced motion.
4. Remove decoration that does not encode meaning, reinforce identity, or improve comprehension.
5. When implementation exists, inspect rendered screenshots rather than judging code alone.

Deliver the direction, key decisions, responsive rules, state coverage, and unresolved product questions. Leave component architecture and framework implementation to a frontend-building workflow; leave reusable token and component governance to a design-system workflow.
