---
name: systematic-debugging
description: >-
  Investigate and fix software bugs using a disciplined, hypothesis-driven, four-phase root cause process.
  Use when encountering test failures, crashes, unexpected behavior, race conditions, or performance regressions.
  Never guess or apply superficial band-aids before proving the failure mechanism.
---

# Systematic Debugging

Debugging is an empirical investigation, not an exercise in trial and error. A bug occurs when an assumption embedded in the code diverges from operational reality. 

Never guess, patch symptoms, or modify production code until you have isolated the mechanism that causes the failure.

---

## 1. The Core Rule: Mechanism Before Modification

Superficial fixes (wrapping code in blanket `try/catch` blocks, adding ad-hoc null checks, or inserting arbitrary delays) mask defects and increase technical debt.

Follow this strict four-phase cycle:

```
[ Phase 1: Isolate ] ──> [ Phase 2: Observe ] ──> [ Phase 3: Prove ] ──> [ Phase 4: Remedy ]
  Minimal Repro             Raw Traces & State        Test Hypothesis           Fix & Regression Test
```

---

## 2. Phase 1: Minimal Reproduction (Isolate)

Before making any changes, establish a deterministic, minimal reproduction:

1. **Write a targeted test or reproduction script**:
   - Strip away non-essential components, network dependencies, or bulky test fixtures.
   - The test must reliably fail with the exact symptom observed in production or CI.
2. **Handle non-deterministic bugs (flakes, races, timing issues)**:
   - Loop the test under load (`for i in {1..100}; do ... done`).
   - Increase thread contention or mock async boundaries with controlled latencies.
   - Do not proceed until you can trigger the failure predictably.

---

## 3. Phase 2: Evidence Gathering & State Inspection (Observe)

Inspect raw evidence closest to the failure point:

- **Examine full stack traces and error objects**: Look for root exceptions, not just the top-level catch wrapper.
- **Trace variable state backwards**: Identify what state was *expected* vs. what state was *observed* at the exact moment of failure.
- **Inspect boundaries**: Check inputs/outputs across network, database, serialization, and filesystem boundaries.
- **Read diffs and commit history**: Check recent changes to the affected files (`git log -p -S <symbol>`).

---

## 4. Phase 3: Formulate & Test Hypotheses (Prove)

Never make speculative edits hoping one will work. Formulate clear, falsifiable hypotheses:

1. **State the hypothesis**:
   - *"The failure occurs because `TokenCache.get()` returns a stale token when the user refreshes within 50ms of expiration."*
2. **Predict the consequence**:
   - *"If this hypothesis is correct, disabling cache retrieval or manually invalidating the token before refresh will eliminate the failure."*
3. **Validate with targeted instrumentation**:
   - Use debug logs or breakpoints to verify that the suspect code path executes with the exact faulty parameters.
   - If the evidence contradicts your hypothesis, discard it and form another.

---

## 5. Phase 4: Targeted Fix & Defense in Depth (Remedy & Verify)

Once the mechanism is proven:

1. **Implement the minimal principled fix**:
   - Address the root cause at the correct abstraction layer.
   - Restore the broken invariant without introducing defensive clutter elsewhere.
2. **Verify the reproduction test**:
   - Run the reproduction test created in Phase 1: confirm it transitions from **RED** to **GREEN**.
3. **Run the full test suite**:
   - Run all existing tests to guarantee zero unintended regressions.
4. **Institutionalize the fix**:
   - Check the reproduction test into the repository test suite permanently.
   - Add defense-in-depth: add explicit invariant assertions, stricter types, or actionable error messages if the condition recurs.

---

## 6. Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Professional Alternative |
| :--- | :--- | :--- |
| **Shotgun Debugging** | Making multiple speculative code changes at once. You lose track of what actually fixed the issue or introduced new bugs. | Change one variable or code path at a time against a deterministic reproduction. |
| **Symptom Masking** | Adding `if (val != null)` or `try { ... } catch (e) {}` around an error without knowing why the value was null. | Trace where the invalid state originated and prevent it upstream. |
| **Sleep / Delay Band-Aids** | Inserting `sleep(100)` to fix a timing issue or race condition. | Synchronize on explicit conditions, events, promises, or mutexes. |
| **Unverified Victory** | Declaring a bug fixed without running the reproduction script or checking the return code. | Show the reproduction failing before the fix and passing after the fix. |
