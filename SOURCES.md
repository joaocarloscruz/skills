# Sources and inspiration

The skills in this repository are original syntheses informed by patterns observed in the following projects. No upstream skill is vendored verbatim.

- [Agent Skills specification](https://github.com/agentskills/agentskills) — Apache-2.0 code and CC-BY-4.0 documentation. Defines the portable `SKILL.md` format and progressive-disclosure model.
- [mattpocock/skills](https://github.com/mattpocock/skills) — MIT License. Inspired tight debugging feedback loops, explicit review baselines, primary-source research, handoffs, specifications, and issue workflows.
- [vercel-labs/skills](https://github.com/vercel-labs/skills) — reviewed discovery guidance and its [skills.sh directory](https://www.skills.sh/) to select widely installed comparison candidates. Adoption counts are not effectiveness evidence; no implementation was copied.
- [openai/skills](https://github.com/openai/skills) — licenses are supplied per skill. Informed concise skill structure, progressive disclosure, and validation.
- [anthropics/skills](https://github.com/anthropics/skills) — licenses are supplied per skill. Informed reconnaissance-before-action, reusable resources, and artifact-oriented workflows.
- [github/awesome-copilot](https://github.com/github/awesome-copilot) — community collection with license information per contribution. Informed catalog breadth, AI evaluation, supply-chain, documentation, and engineering workflow coverage.
- [MicrosoftDocs/Agent-Skills](https://github.com/MicrosoftDocs/Agent-Skills) — curated Microsoft and Azure examples. Informed portability and domain-specific progressive disclosure.
- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) — license information is supplied per skill. Informed React performance, scalable component composition, and current-rule references.
- [joshuadavidthomas/agent-skills](https://github.com/joshuadavidthomas/agent-skills) — MIT License. Informed the internal split between product and marketing interface guidance.
- [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) — Apache-2.0. Informed design-to-code verification, token extraction, and progressive workflow gates.
- [microsoft/skills](https://github.com/microsoft/skills) — MIT License. Informed AI integration, SDK grounding, governance, data, monitoring, and acceptance-test patterns.
- [elastic/agent-skills](https://github.com/elastic/agent-skills) — licenses are supplied by the project. Informed observability-oriented domain skills and evaluation-driven maintenance.
- [obra/superpowers](https://github.com/obra/superpowers) — MIT License. Informed independently reviewed workflow structure, debugging discipline, and behavioral skill testing. Mandatory gates and diagnostic snippets were not imported wholesale.
- [trailofbits/skills](https://github.com/trailofbits/skills) — CC-BY-SA-4.0. Reviewed for security specialization and testable property selection. No upstream text or code was copied; future adaptations require separate license review.
- [supabase/agent-skills](https://github.com/supabase/agent-skills) — MIT License. Informed PostgreSQL-specific review categories and conditional database references.
- [dbt-labs/dbt-agent-skills](https://github.com/dbt-labs/dbt-agent-skills) — Apache-2.0. Reviewed for domain-specific package boundaries and validation support.

- [benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench) — Apache-2.0. Informed paired no-skill versus with-skill evaluation principles; no result from this benchmark is attributed to this catalog.
- [GeniusHTX/SWE-Skills-Bench](https://github.com/GeniusHTX/SWE-Skills-Bench) — MIT License. Provides public software-engineering comparison artifacts; dataset membership is not treated as evidence that a specific skill or revision improves outcomes.
- [OpenAI: Testing Agent Skills with Evals](https://developers.openai.com/blog/eval-skills) — informed controlled trials, recorded artifacts, and separating routing checks from task outcomes.

Original technical references also cite the relevant primary documentation:

- [React](https://react.dev/learn) and [Next.js](https://nextjs.org/docs) for component behavior and framework-specific performance guidance.
- [PostgreSQL](https://www.postgresql.org/docs/current/) for query semantics, planning, concurrency, and migration constraints; check the deployed major version.
- [GitHub Actions](https://docs.github.com/en/actions) and [GitHub CLI](https://cli.github.com/manual/) for CI permissions, event trust, artifacts, and failure diagnosis.
- [Model Context Protocol](https://modelcontextprotocol.io/specification/2025-11-25) for tool schemas, pagination, errors, and protocol boundaries.
- [HTTP semantics (RFC 9110)](https://www.rfc-editor.org/rfc/rfc9110), [HTTP caching (RFC 9111)](https://www.rfc-editor.org/rfc/rfc9111), and [OpenAPI](https://spec.openapis.org/oas/latest.html) for API contract tests.
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) for concrete trust boundaries and security controls.
- [Hypothesis](https://hypothesis.readthedocs.io/) and [fast-check](https://fast-check.dev/docs/introduction/) for property-based testing and reproducible failures.
- [Ragas](https://docs.ragas.io/en/stable/) for retrieval and generation evaluation concepts.
- [Playwright](https://playwright.dev/docs/best-practices) for locator behavior, web assertions, and observable readiness.
- [Git manuals](https://git-scm.com/docs) for conflict stages, rebase side names, sequencer continuation, and targeted staging.
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) for accessibility success criteria and test limitations.
- [Google AIP-180](https://google.aip.dev/180) for API evolution and consumer compatibility, with conventions scoped to the service.
- [npm](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/) and [OSV Scanner](https://google.github.io/osv-scanner/output/) for dependency metadata, clean installation, advisory analysis, and reachability limits.
- [Martin Fowler: Bounded Context](https://martinfowler.com/bliki/BoundedContext.html) for language and translation across domain boundaries.
- [Python subprocess](https://docs.python.org/3/library/subprocess.html) and [Node.js child processes](https://nodejs.org/api/child_process.html) for process tests, streams, timeouts, and platform limits.
- [Prometheus histograms](https://prometheus.io/docs/practices/histograms/) and [OpenTelemetry messaging](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/) for aggregated distributions and causal span links.
- [Google SRE Workbook](https://sre.google/workbook/table-of-contents/) for SLO alerts and incident response.
- [Docker](https://docs.docker.com/) and [Kubernetes probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) for build secrets, process lifecycle, and health signals.
- [Kafka delivery semantics](https://kafka.apache.org/41/design/design/#message-delivery-semantics) and [Apache Beam](https://beam.apache.org/documentation/programming-guide/#windowing) for replay boundaries, windows, and late data.
- [pandas merge](https://pandas.pydata.org/docs/reference/api/pandas.merge.html) and [scikit-learn leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage) for analysis validity and preprocessing boundaries.
- [k6 load models](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/) and [Google Benchmark](https://google.github.io/benchmark/user_guide.html) for comparable workloads and measurement noise.
- [GitHub immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases) for staging complete artifacts and release recovery.

Specific supporting pages are linked inside each package. Documentation supports
technical guidance; it does not establish that the skill improves agent outcomes.
Reviewed candidate revisions and qualifications are recorded in
`evidence/skills.json`, [the structural review](docs/research-2026-09-12.md), and
[the latest comparison](docs/research-2026-09-20.md).

Review the linked upstream license before importing future material; a repository-level license may not cover every skill or contribution.
