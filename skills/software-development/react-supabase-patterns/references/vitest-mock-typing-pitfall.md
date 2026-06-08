# Vitest + Testing Library Mock Typing Pitfall

## Problem

When using `vi.fn()` with TypeScript, `ReturnType<typeof vi.fn>` doesn't match the expected function signature:

```typescript
// ❌ This causes TSC errors
let onChange: ReturnType<typeof vi.fn>
onChange = vi.fn()  // Type 'Mock<Procedure | Constructable>' is not assignable to type '() => void'
```

## Solution

Use the actual function type instead:

```typescript
// ✅ This works
let onChange: (val: CascadaValue) => void
onChange = vi.fn()
```

## Why

`vi.fn()` returns a `Mock` type that has additional methods (`.mock.calls`, `.mock.results`, etc.) that don't match the base function type. TypeScript's structural typing catches this mismatch.

The fix is to type the variable as the function signature you expect, not as the mock type. Vitest's `vi.fn()` is assignable to any function type, so the assignment works.

## Alternative (if you need mock methods)

If you need to access mock-specific methods (`.mock.calls`, `.mock.results`), use `Mock` type explicitly:

```typescript
import { type Mock } from 'vitest'

let onChange: Mock<(val: CascadaValue) => void>
onChange = vi.fn()
```

But for most test cases, the plain function type is sufficient and cleaner.
