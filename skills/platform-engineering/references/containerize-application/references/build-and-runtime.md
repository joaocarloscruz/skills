# Verify the image's runtime contract

Use for Docker builds and container lifecycle work. The process examples concern Linux containers; use the target platform's signal and filesystem behavior for Windows containers.

## Build inputs and secrets

Keep dependency metadata and lockfiles in stable early layers, then copy application inputs. Separate build-time credentials from runtime credentials. With BuildKit, use a secret or SSH mount for a credential needed during a build step; never copy it into a layer and delete it later. A mounted secret can still leak if the invoked command prints it or copies it into an output. Check both the resulting files and logs. See [Docker build secrets](https://docs.docker.com/build/building/secrets/).

Check native libraries, libc, certificate stores, and CPU architecture when copying a build result into a smaller runtime image. A successful cross-platform build alone does not verify that every target can start and load native dependencies. Preserve the repository's supported architectures and report unavailable runtime checks.

## Signals, identity, and writable paths

Use an exec-form entrypoint or a shell wrapper ending in `exec` so the application receives stop signals. For example, a wrapper that prepares configuration can finish with `exec /app/server "$@"`. Add an init process only if subprocess reaping or forwarding requires it. Verify the actual entrypoint under the configured stop timeout; a fast forced kill is not graceful shutdown. See the [Dockerfile entrypoint reference](https://docs.docker.com/reference/dockerfile/#entrypoint).

Run with the final UID, mounted volume ownership, read-only root setting, and resource limits during smoke verification. Exercise cache/temp writes and persistence after replacement. A non-root build test that relies on a developer-owned bind mount may hide deployment permission failures.

## Health is a control input

For Kubernetes, readiness controls traffic eligibility, liveness may restart the process, and a startup probe protects slow initialization. A shared database outage is usually a poor liveness signal: restarting every healthy process can amplify it. Decide dependency effects on readiness from whether the instance can serve useful requests. See [Kubernetes probe semantics](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

For Compose, distinguish startup ordering from readiness and runtime reconnection; dependencies can fail again after startup. See [Compose dependency conditions](https://docs.docker.com/compose/how-tos/startup-order/). A Dockerfile health check also does not automatically create Kubernetes probes. Test cold startup, dependency loss/recovery, and an in-flight request during shutdown using the target runtime configuration.
