# Test the process contract

Use the project's test runtime and subprocess APIs. Build argv as separate arguments for direct execution; shell-string quoting is a separate test only when the documented interface actually requires a shell. Resolve the executable under test so an older global installation cannot satisfy the check.

## Choose the boundary that can expose the defect

| Failure risk | Focused check |
| --- | --- |
| Broken package entrypoint | Install/build into a disposable environment and invoke from outside the source checkout |
| User configuration masks defaults | Supply a temporary config/home location through supported overrides and a deliberate environment |
| Machine output polluted by logs | Parse stdout as the documented format and assert diagnostics stay on stderr |
| Paths misparsed as options | Include spaces, Unicode, and an option-looking filename; use the documented end-of-options syntax |
| Non-interactive prompt hangs CI | Close stdin or supply explicit EOF, enforce a deadline, and check the documented failure or default |
| Interactive prompts behave differently | Use a pseudo-terminal only for the TTY behavior; captured pipes do not simulate a terminal |
| Partial output damages existing data | Interrupt an isolated operation and inspect both the existing target and temporary files |

Do not assert identical signal codes across operating systems. Check each supported platform's documented termination behavior and observable cleanup. Test a pipe consumer that closes early when streaming output is part of the contract; distinguish the CLI's expected broken-pipe handling from a harness failure.

## Make the harness trustworthy

Capture stdout and stderr concurrently. Waiting for exit before draining a full pipe can deadlock the test harness. Bound execution time and output retention. After timeout, terminate the owned process tree using the platform's supported mechanism and reap it; killing only the immediate wrapper can leave a child holding a pipe or port open. Preserve partial streams and label a harness timeout separately from the program's exit status.

For Python, `subprocess.run` is suitable for bounded output; it captures both streams and waits with a timeout. With `Popen`, use `communicate` or concurrent bounded readers instead of `wait` followed by sequential pipe reads. `communicate(timeout=...)` does not itself kill the child; implement cleanup on that exception. These APIs do not by themselves guarantee descendant cleanup.

When environment isolation is needed, preserve OS variables required to launch the runtime instead of assuming an empty environment works everywhere. Report the overrides that affect the failure; redact secrets rather than dumping the entire environment.

## Primary references

- [Python: subprocess streams, timeouts, process behavior, and security](https://docs.python.org/3/library/subprocess.html)
- [Node.js: child process lifecycle and platform differences](https://nodejs.org/api/child_process.html)
