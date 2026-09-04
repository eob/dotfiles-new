---
name: workfu
description: >-
  Disciplined development execution workflow for AI coding agents. Enforces Red-first validation
  (proving absence or reproduction before implementing), dynamic planning, sub-agent fan-out,
  turning Red to Green, verifying full acceptability criteria, in-flight behavior pinning,
  concise documentation, and filing out-of-scope defects via ticketfu.
  Use when planning, implementing, debugging, or verifying features and fixes.
---

# Workfu: Disciplined Agent Execution Workflow

**Workfu** is the operating discipline for planning, implementing, and verifying changes in codebases. It ensures that every code change is proven necessary before it is written, verified through durable checks, executed systematically through structured plans and sub-agents, and kept free from scope creep.

---

## The Workfu Cycle

```text
[1. Red First] ──> [2. Plan & Track] ──> [3. Fan Out] ──> [4. Green + Criteria] ──> [5. Pin Invariants] ──> [6. Tidy & Document]
  Prove absence /     Decision-complete    Sub-agents for   Red turns Green;          Pin newly noticed       Concise docs;
  reproduce failure   dynamic plan         parallel work    satisfy all criteria      edge cases with tests   file out-of-scope
```

---

## 1. Red First: Validate Absence or Failure Before Implementing

When asked to implement a new feature, fix a bug, update a schema, or alter behavior: **never touch implementation code first.**

Begin by proving that the requested behavior is currently absent or failing:

### The Durable Proof Standard
- **Write a test first**: Create a unit test, integration test, or conformance check that asserts the desired functionality or exposes the defect.
- **Run the test and confirm it fails (RED)**:
  - Verify that it fails for the **expected reason** (e.g., missing method, incorrect return value, schema refusal), not because of a syntax error, broken import, or malformed fixture.
- **Why this is non-negotiable**:
  - Proves the problem actually exists.
  - Guards against writing tests that pass by coincidence (tautologies).
  - Establishes a concrete, unambiguous target for completion.

### Alternative Forms of "Red"
When automated unit tests are impractical (e.g., CLI exit codes, build configurations, wire protocol probes, daemon signals, infrastructure scripts):
- Formulate an explicit, reproducible check:
  - A CLI invocation asserting a non-zero exit code or missing flag output.
  - A `curl` or HTTP probe asserting a specific HTTP status or error payload.
  - A minimal standalone reproduction script.
  - An unanchored schema pattern or serialization check.
- Record the exact failure output before writing the solution.

---

## 2. Dynamic Planning & Continuous Progress Tracking

Once the Red case is established, construct a plan before executing:

1. **Decision-Complete Plan**:
   - Break the implementation into concrete, sequential steps.
   - Explicitly list:
     - The Red test / check.
     - The files requiring modification.
     - Any dependent regenerations, builds, or migrations.
     - The verification steps for all acceptability criteria.
2. **Check Back In Continuously**:
   - As each step completes, update the plan immediately (mark tasks done, note findings).
   - If an unexpected blocker or discovery alters the approach, update the plan explicitly before proceeding—never drift silently from the agreed design.

---

## 3. Sub-Agent Fan-Out & Role Selection

Leverage sub-agents strategically to maintain a clean context window and maximize velocity:

### When to Fan Out
- **Broad Codebase Exploration**: Use read-only research sub-agents (e.g., `research`) to survey architecture, trace call graphs, or find usages across large repositories without polluting the primary agent's context.
- **Parallel Validations**: When changes span multiple decoupled modules or target languages (e.g., TypeScript, Rust, and Swift conformance in multi-language projects), dispatch sub-agents to run checks in parallel.
- **Independent Task Execution**: When independent sub-tasks have clear boundaries, delegate to specialized sub-agents.

### Choosing the Right Agent
- Match the toolset to the task: read-only tools for exploration and research; write/command tools only when implementing or running builds.
- Always provide clear, bounded instructions and prompt the sub-agent to return concise, high-signal results.

---

## 4. Turning Red to Green & Meeting All Acceptability Criteria

Implement the changes cleanly:

1. **Turn the Red Case Green**:
   - Write the minimum viable, clean implementation to satisfy the Red test.
   - Re-run the Red test and confirm it now passes (**GREEN**).
2. **Satisfy Full Acceptability Criteria**:
   - Turning the initial Red test green is necessary, but rarely sufficient.
   - Verify all explicit and implicit requirements:
     - Edge cases and boundary conditions handled.
     - Backwards compatibility and wire contract guarantees preserved.
     - Full repository test suite passes with zero regressions.
     - Build succeeds with zero new compiler warnings or linter errors.

---

## 5. Behavior Pinning: Lock Down In-Flight Discoveries

As you pursue the work, you will inevitably uncover nuances, edge cases, or implicit invariants:

- **Pin Every Discovery**:
  - Whenever you notice a subtle assumption or bug fix in passing, write a dedicated test to **pin that exact behavior**.
  - Example: If fixing an arrival acknowledgment reveals that duplicate submissions must return HTTP 409 across daemon restarts, add an explicit integration test pinning that duplicate handling.
- **Do Not Leave Unpinned Assumptions**: Pinned tests prevent future agents and developers from accidentally unravelling your fix.

---

## 6. Concise, Direct Documentation

Any documentation, comments, or explanations generated during workfu must adhere to high standards:

- **Concise and Direct**: State facts, constraints, and architecture plainly.
- **Explain "Why", Not "What"**: Document non-obvious invariants and rationale. Do not narrate obvious code.
- **Zero Agentic Fluff**: Eliminate conversational filler, apologies, and narrations of internal tool execution.

---

## 7. Out-of-Scope Issues: File via `ticketfu`

While working, you will frequently notice unrelated bugs, outdated docs, missing tests, or technical debt:

### The Anti-Scope-Creep Rule
- **Never fix unrelated issues on the active ticket branch.**
- Mixing unrelated changes into a PR confuses reviewers, expands blast radius, and complicates rollbacks.

### The Ticketfu Protocol
- Immediately record the issue as a new ticket using **`ticketfu`**:
  1. Determine the repository's ticket location:
     - In-repo markdown tickets (e.g., `tickets/open/<ticket-name>.md` on `main`).
     - External issue tracker (e.g., Linear via MCP, assigned to **Edward Benson**).
  2. Document:
     - Kebab-cased ticket name with series prefix.
     - Goal / observed failure mode.
     - Evidence and reproduction steps.
     - Suggested plan or acceptance criteria.
  3. Resume work on your primary task immediately without getting distracted.

---

## Quick Reference Checklist

- [ ] **Red First**: Validated absence of functionality or reproduced failure with a failing test or recorded check.
- [ ] **Plan Created**: Decision-complete plan written with clear acceptance criteria.
- [ ] **Sub-Agents Deployed**: Researched or fanned out parallel tasks via appropriate sub-agents where helpful.
- [ ] **Green Verified**: Implementation completed; initial Red tests now pass.
- [ ] **Full Criteria Met**: Edge cases, performance, and regression test suite verified.
- [ ] **Behavior Pinned**: Added regression tests for newly noticed invariants and edge cases.
- [ ] **Documentation Clean**: Code comments and docs are concise, direct, and free of agent artifacts.
- [ ] **Out-of-Scope Tracked**: Unrelated bugs and debt filed as tickets using `ticketfu`—no scope creep.
