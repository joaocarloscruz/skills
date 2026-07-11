<!-- Generated from library/containerize-application/SKILL.md; do not edit. -->

# Containerize Application

1. Identify build and runtime commands, ports, persistent data, native dependencies, health signals, configuration, and supported architectures.
2. Create a minimal build context with an explicit ignore file; never include secrets, local caches, credentials, or unnecessary source artifacts.
3. Use trusted, appropriately pinned base images and multi-stage builds to separate compilation from runtime.
4. Order layers for stable dependency caching without allowing stale or non-reproducible installs.
5. Run as a non-root user, use a read-only filesystem where practical, set ownership deliberately, and avoid unnecessary packages and capabilities.
6. Pass configuration at runtime. Use secret mechanisms rather than image layers, build arguments, committed environment files, or logs.
7. Handle signals, graceful shutdown, health checks, temporary files, writable paths, and resource limits.
8. For multiple services, define networks, dependencies, volumes, readiness, and development-only conveniences explicitly.
9. Build from a clean checkout, inspect image contents and size, scan dependencies, run the container, exercise health and shutdown, and verify supported architectures.

Report build and run commands, image assumptions, exposed interfaces, persistent state, security decisions, and remaining operational requirements.
