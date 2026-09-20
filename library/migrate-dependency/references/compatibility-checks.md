# Migration compatibility checks

## Resolve a compatible set

Record the installed versions from the lockfile, requested manifest ranges,
runtime/toolchain versions, and any host/plugin or peer requirements. A target
package can support the application API while requiring a newer runtime or a
different plugin generation. Upgrade the smallest compatible set and explain
necessary companion changes.

For npm packages, inspect `engines`, peer ranges, exports, and supported module
formats where relevant. Do not use `--force`, a blanket peer bypass, or an override
merely to silence a conflict. If a temporary override is justified, record the
compatibility evidence and a removal condition. Follow equivalent metadata and
resolver rules for the actual ecosystem; these are not universal npm commands.

After updating the manifest and lockfile with the repository's package manager,
verify a clean, frozen install in a disposable checkout or the normal CI job.
Do not delete the user's active dependency tree just to prove this. For npm,
`npm ci` verifies manifest/lock agreement and removes an existing `node_modules`;
use it in the appropriate workspace with the repository's required configuration.

## Test what consumers actually load

For a published library, use its built/packed artifact in a representative consumer
when exports, types, assets, or peer resolution change. Workspace source imports
can hide missing package files and invalid entrypoints. For an application, run
the production build/start path affected by the dependency; the dev server can
exercise different loading and optimization behavior.

Choose tests from the changed semantics: parser defaults, time zones, validation,
serialization, query results, generated code, or cache behavior. Run an official
codemod only for the applicable version transition, inspect its diff, and test
behavior it cannot infer. Do not substitute a long generic matrix for the
dependency's actual migration risks.

## Establish the rollback boundary

When the dependency writes files, schemas, queued messages, or stored data, check
whether the old version can read the new output. Code rollback is insufficient
after an incompatible write. Rehearse representative old/new reads in isolated
fixtures and document the reversible window, data backup/restore requirement, or
forward-repair plan. Do not run production data migrations merely to verify a
dependency bump.

Report the exact target set, evidence for required runtime changes, clean-install
result, semantic checks, and any rollout step that remains unexecuted.

## Primary references

- [npm package metadata: engines, peers, and package boundaries](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/)
- [npm ci: frozen installation and configuration](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

Check the actual package manager and dependency versions before applying commands.
The consumer and rollback checks above are original workflow guidance, not a claim
that npm validates runtime compatibility.
