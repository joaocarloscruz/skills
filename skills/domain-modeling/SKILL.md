---
name: domain-modeling
description: Model domain concepts, language, rules, lifecycles, and boundaries before system design.
---

# Domain Modeling

1. Define the business capability and decisions the model must support. Exclude implementation details until the domain is understood.
2. Gather language from users, documentation, interfaces, data, and code. Treat existing names as evidence, not truth.
3. Identify actors, concepts, value objects, states, events, commands, policies, and external systems. Define each term in plain domain language.
4. Find synonyms, overloaded terms, and unnamed concepts. Choose one term per meaning and distinguish meanings that currently share a name.
5. Express invariants and lifecycle rules with concrete examples and counterexamples. State who may cause each transition, its prerequisites, and its observable result.
6. Draw boundaries around concepts that change together or enforce the same rules. Name ownership and the contracts between boundaries without inventing distributed services prematurely.
7. Test the model against normal journeys, edge cases, reversals, concurrency, historical corrections, and failure recovery. Record unresolved questions instead of hiding them in generic names.
8. Compare the resulting language with the code and data model. Identify drift, accidental coupling, and migration implications without forcing the domain to mirror the current implementation.

Produce the smallest useful model: a glossary, relationships and boundaries, lifecycle or state rules, invariants, representative scenarios, and open questions. Use diagrams only when relationships are clearer visually. Update domain documentation only when the user requested a change; otherwise report the proposed model for review.
