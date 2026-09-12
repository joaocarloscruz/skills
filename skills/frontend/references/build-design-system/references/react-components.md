# React component contracts

Use after identifying the installed React version and existing primitive library. Preserve established APIs unless the requested migration includes changing them.

## Choose the smallest useful API

| Repeated problem | Candidate change | Verify before adopting |
| --- | --- | --- |
| Mutually exclusive display flags | A named variant or discriminated union | Impossible combinations cannot be requested; existing callers have a migration |
| Consumers need to arrange subparts | Children or named slots | Reading order, labels, focus, and required parts still work |
| Sibling controls coordinate one interaction | Lift state to their nearest shared owner | Independent component instances remain independent |
| A complex widget has cooperating subcomponents | A compound API with a scoped provider | Missing-provider errors are clear and nested instances do not share state |
| Every consumer passes the same implementation details | An internal adapter with a small public contract | The adapter does not hide important loading, error, or accessibility states |

A boolean such as `disabled` can express a real independent state. Do not replace all booleans or add providers to simple components merely to follow a pattern.

For example, an action contract can represent mutually exclusive destinations without accumulating `isLink`, `isDownload`, and `isSubmit` flags:

```typescript
type Action =
  | { kind: "navigate"; href: string; label: string }
  | { kind: "submit"; label: string; pending: boolean };
```

This models a decision; implementation must still select native link or button semantics, enforce URL policy, and handle submission behavior. Do not invent a new abstraction if the current library already provides this contract.

## Preserve behavior through wrappers

- Decide controlled versus uncontrolled ownership; never silently switch during an instance's lifetime. Document the default value, current value, and change notification contract.
- Preserve refs, focus restoration, native attributes, form submission, event cancellation, and accessible names. Test one realistic consumer instead of testing only the wrapper in isolation.
- React 19 supports passing `ref` as a prop to function components. Libraries supporting React 18 still need the appropriate compatibility approach; do not mechanically remove `forwardRef` without checking the supported range.
- Keep internal DOM and context details private unless consumers truly need a stable extension point. A context provider is not itself proof of a better architecture.
- Exercise two instances, nested usage where supported, keyboard-only use, and a long/localized label. These catch shared-state and composition failures that a default screenshot misses.

## Primary references

- [React: sharing state between components](https://react.dev/learn/sharing-state-between-components)
- [React: controlled and uncontrolled inputs](https://react.dev/reference/react-dom/components/input)
- [React: forwardRef and React 19](https://react.dev/reference/react/forwardRef)
- [WAI-ARIA Authoring Practices: patterns](https://www.w3.org/WAI/ARIA/apg/patterns/)
