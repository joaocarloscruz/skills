---
name: test-cli
description: Test CLIs across arguments, streams, exit codes, files, environment, signals, and interaction.
---

# Test CLI

1. Identify the installed artifact, supported platforms, shell assumptions, and documented command contract.
2. Run help and version behavior, then a minimal successful invocation in an isolated temporary directory.
3. Test argument combinations, quoting, stdin, binary or Unicode data, environment variables, config precedence, missing inputs, permissions, and interrupted execution.
4. Assert exit codes and stdout and stderr separately. Treat stable machine-readable output as a compatibility contract.
5. Verify filesystem and network side effects, cleanup, idempotency, and behavior when output is piped or non-interactive.
6. Avoid snapshots for volatile text unless normalized intentionally.

For packaged executables, subprocess harnesses, pipes, or interactive commands, read `references/process-contracts.md`. Test at least one invocation through the installed entrypoint when packaging or launch behavior is in scope; calling an internal command function cannot detect a broken wrapper, interpreter path, or exit status.

Report the exact command, environment, exit code, streams, and side effects for failures. Do not test against real user data when a disposable fixture is possible.
