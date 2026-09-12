# Properties and generated cases

Use when many valid inputs or operation sequences should obey the same contract. Choose the repository's existing property-testing library and check its version. Preserve explicit examples for important user scenarios.

## Pick an independent oracle

| Candidate property | Useful example | Important qualification |
| --- | --- | --- |
| Round trip | Decoding an encoded supported value preserves its meaning | Equality may require documented canonicalization; paired encode/decode bugs can still agree |
| Idempotence | Normalizing twice equals normalizing once | Only if repeated normalization is part of the contract |
| Conservation | Transfers preserve the total balance in a closed model | Include fees, rounding, failures, and currencies only as defined |
| Order independence | Permuting a set of independent inputs preserves a result | Invalid for order-sensitive events or floating-point sums unless tolerance is justified |
| Monotonicity | Adding a permission restriction cannot increase accessible objects | State the policy and compare independently computed sets |
| Model agreement | A real queue matches a small reference queue after each operation | The model must not call the same implementation helpers |

For sorting, checking only that output is sorted permits an implementation that returns an empty list. Also check length and element multiplicities. This illustrates why each property must exclude plausible incorrect implementations.

## Generate the difficult space deliberately

1. Define valid input structure and meaningful sizes; generate valid records directly where possible instead of rejecting almost everything.
2. Include empty/singleton collections, repeated values, boundary lengths, Unicode, nullability, numeric extremes, and malformed cases only when the contract accepts or rejects them explicitly.
3. For workflows, generate operations with preconditions and compare the observable state after each step. Include cancellation, retries, and failure transitions when relevant.
4. Preserve the minimal shrunk counterexample, seed/replay information, library version, and original failure reason. Promote important discoveries into named regression examples.
5. Keep an execution/time budget. A large generated case count with a weak oracle is not stronger assurance.

Use the actual implementation under test and an independently stated invariant. Do not calculate expected output by running the same algorithm a second time. Shrinking helps diagnosis; it does not establish that the model covers the user's full requirements.

## Primary references

- [Hypothesis: property-based testing](https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html)
- [Hypothesis: stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html)
- [fast-check: model-based testing](https://fast-check.dev/docs/advanced/model-based-testing/)

The design principles are library-independent; use the installed library's API for generators, shrinking, replay, and state-machine tests.
