# Bound the next action during an incident

Use during an active outage or handoff. Keep diagnosis moving while prioritizing a mitigation that reduces user impact; a complete explanation is not a prerequisite for recovery. See [Google SRE incident response](https://sre.google/workbook/incident-response/).

Before a consequential action, record its target, expected effect, observation window, and stop/reversal condition in the incident timeline. Reuse the commander's or user's existing authorization. If the action's outcome is uncertain, inspect the current state before repeating it; duplicate failovers or competing configuration changes can worsen the incident.

| Candidate mitigation | Check that changes the decision |
| --- | --- |
| Roll back a deployment | Is old code compatible with the current schema, data format, and already-completed jobs? |
| Fail over or add replicas | Does the destination have headroom and usable state, or will this amplify a shared bottleneck? |
| Increase retries | Will retries consume the remaining capacity? Bound attempts and consider shedding load instead. |
| Restart a process | Will it destroy needed evidence or trigger an expensive recovery? Capture readily available evidence without delaying necessary mitigation. |

Verify recovery using the affected user journey and remaining backlog, including delayed or duplicate work. A process returning healthy while jobs remain unprocessed is partial recovery. Define an observation period appropriate to the failure mechanism; do not invent a universal duration.

At handoff, record current impact, mitigation still in force, completed and pending actions, the next decision time, evidence links, and ownership. Prepare status updates with known impact and uncertainty; send them only through an authorized communication channel. Keep the causal hypothesis distinct from the confirmed mitigation outcome in the later incident account.
