# Artifact identity and partial publication

Use when a release publishes several artifacts, promotes between environments, or resumes after an uncertain result. Keep execution within the user's existing release and destination authorization.

## Release an identified artifact

Record source commit, version/tag, build inputs, artifact names, digests, and intended destinations. Promote the tested artifact where possible; rebuilding from the same commit may change dependency resolution, timestamps, or toolchain output. If rebuilding is required, verify the new artifact and identify it separately.

Before publishing, inspect existing tags and remote versions. An existing name is not evidence that it refers to the intended commit or bytes. Reconcile a mismatch rather than force-moving a release tag or replacing an artifact to make a retry succeed.

## Resume from observed remote state

| Observed state | Next action |
| --- | --- |
| Upload timed out | Inspect the destination and compare identity before retrying. The upload may have succeeded. |
| Version exists with matching artifacts | Verify remaining destinations and metadata; do not republish completed effects. |
| One platform artifact is missing | Resume only the missing compatible step if the registry permits it. |
| Published bytes differ from the intended release | Stop promotion and report the discrepancy; follow the ecosystem's repair or new-version procedure. |
| Application rollback crosses a schema/data cutover | Establish compatibility or choose a forward repair/restore plan; redeploying old code alone may fail. |

For GitHub immutable releases, stage the complete asset set in a draft before publication; published assets and the associated tag are then protected. Check the repository's actual immutability setting rather than assuming it. See [GitHub immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases).

Verify a consumer-visible download or installed package independently. Where supported, compare its provenance and digest to the recorded artifact; GitHub provides [release and asset verification](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/verify-release-integrity). Distinguish publication success from rollout health, and retain the previous compatible artifact until the agreed recovery window ends.
