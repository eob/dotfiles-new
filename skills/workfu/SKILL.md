---
name: workfu
description: >-
  Disciplined development execution workflow for AI coding agents. Enforces Red-first validation
  (capturing verbatim failure evidence and verifying reversibility), dynamic planning, sub-agent fan-out,
  turning Red to Green, structured validation gate matrices, A/B control testing for flakiness,
  symmetric failure pinning, durable findings capture, and filing out-of-scope defects via ticketfu.
  Use when planning, implementing, debugging, or verifying features and fixes.
---

# workfu: Disciplined Development Execution

**Workfu** is the operating discipline for planning, implementing, and verifying changes in production codebases. It ensures that every code change is proven necessary before it is written, verified through durable checks and verifiable gate matrices, guarded against pre-existing flakiness through A/B control tests, and documented with durable architectural findings.

---

## The Workfu Cycle

```text
[1. Red First] ──> [2. Plan & Track] ──> [3. Fan Out] ──> [4. Green & Gate] ──> [5. Pin Invariants] ──> [6. Polish & PR]
  Verbatim failure   Decision-complete    Sub-agents for   Red turns Green;          Pin symmetric edge      simplifyfu, codex,
  evidence captured  dynamic plan         parallel work    pass gate matrix          cases with tests        prfu, durable findings
```

---

## 1. Red First: Validate Absence or Failure Before Implementing

When asked to implement a new feature, fix a bug, update a schema, or alter behavior: **never touch implementation code first.**

Begin by proving that the requested behavior is currently absent or failing:

### 1.1 The Durable Proof Standard
- **Write a test first**: Create a unit test, integration test, or conformance check that asserts the desired functionality or exposes the defect.
- **Run the test and confirm it fails (RED)**:
  - Verify that it fails for the **expected causal reason** (e.g., missing method, incorrect return value, schema refusal, wrong status code), not because of a syntax error, broken import, or malformed test fixture.
- **Why this is non-negotiable**:
  - Proves the problem actually exists.
  - Guards against writing tests that pass by coincidence (tautologies).
  - Establishes a concrete, unambiguous target for completion.

### 1.2 Capture Verbatim Red Evidence
Do not simply report that the test failed. **Record the verbatim failure output** directly in the ticket or planning notes:
```text
---- poisoning_run_thread_panic_finalizes_the_session ----
assertion `left == right` failed: a panicked native session must stay visible at the front
  left: 404
 right: 200
test result: FAILED. 0 passed; 1 failed; 168 filtered out
```
This failure trace serves as auditable proof of the original failure mode.

### 1.3 Pin Against Symmetric & Boundary Failure Modes
Avoid superficial, one-sided checks (e.g., merely testing `assert result is not None` or `assert status == 200`):
- **Test the symmetric inverse**: If testing that an item is preserved across restarts, test that it is consumed **exactly once**, not twice (testing duplication and starvation).
- **Test refusal of invalid inputs**: If asserting valid data decodes, test that invalid tags or missing fields are explicitly refused rather than silently defaulting.
- **Test anchor boundaries**: If validating regex or JSON Schema patterns, test that unanchored prefixes or suffixes are rejected.

### 1.4 Alternative Forms of "Red"
When automated unit tests are impractical (e.g., CLI exit codes, build configurations, wire protocol probes, daemon signals, infrastructure scripts):
- Formulate an explicit, reproducible check:
  - A CLI invocation asserting a non-zero exit code or missing flag output.
  - A `curl` or HTTP probe asserting a specific HTTP status or error payload.
  - A minimal standalone reproduction script.
- Record the exact failure output before writing the solution.

### 1.5 Elusive Failure Mechanisms: Invoke `debugfu`
If the failure mechanism or root cause of a bug is non-deterministic, intermittent, or unknown (e.g., race conditions, memory corruption, subtle state desynchronization), invoke **`debugfu`** (`Isolate → Observe → Prove → Remedy`) to isolate the root cause mechanism before attempting to write the Red test.

---

## 2. Dynamic Planning & Continuous Progress Tracking

Once the Red case is established, construct a plan before executing:

1. **Decision-Complete Plan**:
   - Break the implementation into concrete, sequential steps.
   - Explicitly list:
     - The Red test / check.
     - The files requiring modification.
     - Any dependent regenerations, builds, or migrations.
     - The verification gates for all acceptability criteria.
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

## 4. Turning Red to Green & Structured Gate Matrices

Implement the changes cleanly:

### 4.1 Turn the Red Case Green
- Write the minimum viable, clean implementation to satisfy the Red test.
- Re-run the Red test and confirm it now passes (**GREEN**).

### 4.2 The Reversion Check (Proving Causality)
Before concluding that the fix is complete, perform a temporary reversion check:
- Revert or stash the implementation change while keeping the new test in place.
- Verify that the test immediately fails again with the identical Red failure signature.
- Re-apply the implementation and confirm it returns to Green. This eliminates any possibility that an ambient environment change or stale artifact caused the test to pass.

### 4.3 Structured Validation Gate Matrix
Do not simply say "all tests pass". Record an auditable **Validation Gate Matrix** in the ticket:

| Gate / Command | Base Commit | Result / Metrics |
| :--- | :--- | :--- |
| `cargo test -p daemon --test native_host` | `585b08acf` | **ok. 177 passed; 0 failed** (44s) |
| `cargo test -p daemon --lib --test process` | `585b08acf` | ok: lib 128; process 1 — 0 failed |
| `npm run generate:check` | `585b08acf` | In sync; zero drift |
| `cargo fmt --check -p daemon` | `585b08acf` | Clean (0 diffs introduced) |

Always record the specific base commit each gate was executed on, especially when rebasing onto an evolving `origin/main`.

---

## 5. Differential A/B Control Testing for Flakiness

In large, concurrent, or load-sensitive suites, tests may occasionally flake or time out. **Do not panic and do not rewrite working implementation code.**

Follow the **A/B Control Testing Protocol**:
1. When a test in the wider suite fails unexpectedly:
   - Run the failing test in isolation.
   - Build a control binary from an unmodified checkout of `origin/main`.
   - Run the branch binary and the control binary **concurrently under identical machine load**:
     ```text
     branch  : test result: ok.     177 passed; 0 failed
     control : test result: FAILED. 174 passed; 1 failed (deadline exceeded)
     ```
2. If `origin/main` exhibits the same failure under the same load:
   - The failure is proven to be **pre-existing load sensitivity or environment flakiness**, not a regression introduced by your change.
   - Document this evidence in the ticket under a dedicated `Flakiness` section.
   - File an issue for the flake via `ticketfu`.
   - Do not modify your implementation to chase ambient flakes.

---

## 6. Behavior Pinning: Lock Down In-Flight Discoveries

As you pursue the work, you will inevitably uncover nuances, edge cases, or implicit invariants:

- **Pin Every Discovery**:
  - Whenever you notice a subtle assumption or bug fix in passing, write a dedicated test to **pin that exact behavior**.
  - Example: If fixing an arrival acknowledgment reveals that duplicate submissions must return HTTP 409 across daemon restarts, add an explicit integration test pinning that duplicate handling.
- **Do Not Leave Unpinned Assumptions**: Pinned tests prevent future agents and developers from accidentally unravelling your fix.

---

## 7. Scope Containment & Pre-Existing Drift Hygiene

Maintain strict hygiene over code modifications and formatting:

- **Isolate Diffs to the Change**:
  - Never allow auto-formatters or linters to reformat hundreds of lines of pre-existing drift across unrelated files.
  - If a file has pre-existing formatting drift on `main`, format your new or modified lines by hand to produce a clean, minimal diff.
- **Explicit Non-Goals**:
  - State explicitly in the ticket or PR what was deliberately **not** touched (e.g., *"Per scope note, lock acquisitions outside drive() were left alone"*).

---

## 8. Decisions & Durable Findings

Never bury critical architectural rationale solely in ephemeral conversation turns or code comments. Every completed ticket must record a **Decisions and durable findings** section:

- **Invariants & Ordering**: Explicitly record concurrency invariants, lock acquisition order (e.g., `lock order is journal → mailbox everywhere`), or state machine transitions.
- **Compatibility & Wire Contracts**: Note how wire format, migrations, or database checkpoints remain compatible with older versions.
- **Settled Trade-offs**: Document why an alternative approach was rejected so future agents do not re-litigate settled decisions.

---

## 9. Out-of-Scope Issues: File via `ticketfu`

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

## 10. Pre-Review Polish Pass: `simplifyfu`, `codex`, & `prfu`

Before finalizing changes and marking the PR ready for review:

1. **Anti-Bloat Audit (`simplifyfu`)**:
   - Audit all modified files using **`simplifyfu`**.
   - Inline single-use private helpers, flatten conditionals with guard clauses, enforce YAGNI, and strip out temporary scaffolding or dead code.
2. **Second-Opinion Diff Review (`codex`)**:
   - Optionally invoke **`codex`** (`codex review --uncommitted` or `codex review origin/main...HEAD`) for an independent adversarial second opinion on concurrency, security, and boundary edge cases.
3. **PR Description & Comment Hygiene (`prfu`)**:
   - Perform the pre-PR comment hygiene pass using **`prfu`** (explain "Why" not "What", remove obvious comments narrating code, eliminate agent artifacts).
   - Draft or update the PR description following the `prfu` template (including the `Agent Metadata` block).

---

## Quick Reference Checklist

- [ ] **Red First**: Validated absence of functionality or reproduced failure with a failing test or recorded check.
- [ ] **Verbatim Evidence Captured**: Recorded exact assertion failure output before implementing.
- [ ] **Symmetric Modes Pinned**: Tested boundary conditions, duplicates, leaks, or refusals (not just happy paths).
- [ ] **Plan Created & Tracked**: Decision-complete plan written and kept up to date.
- [ ] **Sub-Agents Deployed**: Researched or fanned out parallel tasks via appropriate sub-agents where helpful.
- [ ] **Green Verified**: Implementation completed; initial Red tests now pass.
- [ ] **Reversion Checked**: Temporarily reverted fix to confirm test flips cleanly back to Red.
- [ ] **Gate Matrix Recorded**: Documented command, base commit, and pass counts for all validation gates.
- [ ] **A/B Control Tested**: If wide suites flaked, verified identical failure on unmodified `origin/main`.
- [ ] **Diff Hygiene Preserved**: No unrelated pre-existing formatting drift included in diff.
- [ ] **Durable Findings Recorded**: Invariants, lock orders, and settled decisions documented in ticket.
- [ ] **Out-of-Scope Tracked**: Unrelated bugs and debt filed as tickets using `ticketfu`—no scope creep.
- [ ] **Code Simplified**: Audited diff with `simplifyfu` to remove YAGNI bloat and dead scaffolding.
- [ ] **PR Polished**: Comment hygiene pass and PR description completed using `prfu`.
