---
name: code-simplify
description: >-
  Audit and refine recently written or modified code to remove accidental complexity, unnecessary abstractions,
  dead code, and over-engineering. Use after completing a feature or bugfix, before opening a PR or declaring a task done.
---

# Code Simplification & Anti-Bloat

AI coding agents tend to generate defensive scaffolding, redundant wrapper functions, overly elaborate type hierarchies, and speculative abstractions. Every line of unnecessary code is a liability that must be read, maintained, and debugged by humans.

Run this skill as a dedicated post-implementation pass to strip out accidental complexity before submitting code for review.

---

## 1. Core Philosophy: Clarity Over Cleverness

- **Code is read 10x more than written**: Write simple, self-evident code that any engineer can understand in 5 seconds.
- **YAGNI (You Aren't Gonna Need It)**: Implement strictly what is required right now. Never add hooks, generic type parameters, or configuration knobs for hypothetical future requirements.
- **Behavioral Parity**: Simplification is a refactoring pass; it must preserve all functional behaviors and tests without alteration.

---

## 2. Simplification Checklist

Work through each changed file and apply these checks:

### 1. Inline Single-Use Helpers
If a private helper function is only called from one location, consider inlining it. Moving logic into separate tiny functions often fragments linear control flow and forces the reader to jump back and forth.
- *Rule of thumb*: Keep logic inline unless the helper encapsulates a non-trivial algorithm, handles complex recursion, or provides significant testing isolation.

### 2. Flatten Nested Conditionals with Guard Clauses
Replace deep `if / else` nesting with early returns, breaks, or continues:
```typescript
// ❌ Deep nesting
function processOrder(order: Order) {
  if (order.isValid) {
    if (!order.isCancelled) {
      if (order.hasInventory) {
        return ship(order);
      }
    }
  }
  return null;
}

// ✅ Guard clauses (flat, readable)
function processOrder(order: Order) {
  if (!order.isValid || order.isCancelled || !order.hasInventory) {
    return null;
  }
  return ship(order);
}
```

### 3. Replace Custom Logic with Standard Library Primitives
AI agents often hand-roll complex helpers for array transformations, string trimming, or date formatting that the language runtime or standard library already provides. Audit and replace bespoke utility functions with standard library calls.

### 4. Eliminate Speculative Abstractions
- Strip out unused interface definitions that have only one implementation.
- Remove factory classes or builder patterns where a simple object literal or constructor suffices.
- Avoid premature parameterization (e.g. passing a strategy object when there is only ever one strategy).

### 5. Consolidate Duplicate or Derived State
Never maintain two state variables when one can be derived from the other. Storing derived state requires synchronization logic and invites desync bugs.
- *Example*: Store `items[]`. Do NOT also store `itemCount` or `isEmpty`; derive them on demand via `items.length`.

### 6. Purge Dead Code & Artifacts
- Remove commented-out code blocks.
- Remove unused imports, variables, and parameters.
- Delete temporary debugging logs, print statements, and mock data.

---

## 3. Anti-Bloat Reference Table

| Over-Engineered Pattern | Simplified Alternative | Benefit |
| :--- | :--- | :--- |
| Custom factory or builder pattern for simple data structs | Direct object literal or constructor | Eliminates boilerplate and cognitive indirection. |
| Nested ternary expressions (`a ? b ? c : d : e`) | Explicit `if/else` or guard clauses | Improves human scan speed and debugging clarity. |
| Generic multi-purpose helper with boolean flags (`doThing(true, false)`) | Two clear, focused functions or inline logic | Avoids control-flag coupling and unreadable call sites. |
| Hand-rolled retry / polling loop with custom timers | Built-in standard library or framework primitives | Avoids subtle race conditions and timing bugs. |

---

## 4. Verification Gate

After completing a simplification pass:

1. **Rerun Automated Tests**:
   - Execute the test suite (`cargo test`, `npm test`, `pytest`, `bun test`, etc.).
   - All tests must pass with zero behavioral differences.
2. **Review Diff**:
   - Run `git diff` to confirm that lines of code decreased or stayed flat, and readability increased.
