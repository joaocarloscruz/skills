---
name: respond-to-incident
description: Coordinate technical incident response from detection through mitigation, diagnosis, recovery, communication, and follow-up. Use during outages, severe degradation, security events, data integrity threats, or other time-sensitive production failures.
---

# Respond to Incident

1. Establish severity, user impact, start time, affected systems, incident lead, and communication channel.
2. Preserve a timestamped timeline and separate observations from hypotheses.
3. Stabilize first: stop harmful automation, shed load, fail over, disable a feature, or roll back when authorized and safer than continued impact.
4. Assign one owner per action and record expected signals, deadlines, and results. Avoid simultaneous uncoordinated changes.
5. Protect evidence and data integrity; do not expose secrets or sensitive customer information in updates.
6. Verify recovery through user-facing signals, not only internal green dashboards.
7. Continue monitoring, communicate status, and define follow-up owners.

After stabilization, produce a blameless account of contributing conditions, detection gaps, response quality, and prioritized prevention work. Never invent certainty during an active incident.
