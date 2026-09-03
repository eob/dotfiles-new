---
name: write-pr-description
description: >-
  Guidelines and template for writing clear, concise, expert-level Pull Request (PR) descriptions,
  including a pre-PR code comment hygiene pass. Use whenever preparing, drafting, or reviewing code
  changes and PR descriptions.
---

# Writing a PR Description

This skill defines the standard for drafting pull request descriptions. Follow these guidelines to produce PR descriptions that are immediately clear, technically rigorous, and respect the reviewer's time.

---

## 1. Tone and Core Philosophy

- **Simple, direct, active voice**: Use active verbs ("Adds", "Migrates", "Removes", "Fixes", "Refactors"). Avoid passive constructions ("This change was made in order to...").
- **Expert-to-expert communication**: Write for fellow technical peers. Speak plainly and directly. Do not over-explain basic programming concepts; clearly stated facts allow reviewers to immediately grasp the ramifications.
- **Zero conversational fluff**: Eliminate conversational filler, pleasantries, or preamble (e.g., "In this PR, I have decided to...", "Hope this looks good!").

---

## 2. The Context Boundary (Agent Hygiene)

As an AI agent, you operate with a conversation history, system prompt, tool execution outputs, and internal chain of thought. **The PR reviewer has none of this context.** They only see the repository, git history, and the PR description.

### The Zero-Leakage Rule
Never mention or hint at ephemeral agent state, conversation steps, or prompt instructions:
- ❌ *"As requested by the user..."*
- ❌ *"In step 3 of the plan, we noticed an issue..."*
- ❌ *"Fixed the bug we talked about earlier."*
- ❌ *"Running the test command revealed that..."*

### Explicit Attribution (No Phantom Pronouns)
Never use ambiguous pronouns or vague pointers ("it", "that thing", "the setting", "the issue") where the referent is not 100% explicit in the PR text itself. Always specify **whose** setting, **which** module, or **what** exact error.

- ❌ *"Changes that foo setting."* (Whose foo setting? What file? What was it changed from/to?)
- ✅ *"Increases `nginx.client_max_body_size` from 10MB to 50MB in `docker/nginx.conf`."*

- ❌ *"Fixes the issue where it failed."*
- ✅ *"Prevents a `KeyError` in `BillingService.process_invoice()` when the billing address lacks a postal code."*

---

## 3. Pre-PR Code Comment Hygiene Pass

Before drafting and posting the PR, **conduct a dedicated pass over all changed files to audit code comments**. 

AI coding agents tend to dump large, essay-like comments or narrative reports directly into code, severely impairing human readability. Enforce these rules across the diff:

- **Simple, concise, non-verbose**: Strip out paragraph-length explanations and deep reporting. Provide only the essential, high-signal context.
- **Never comment on the obvious**: Do not narrate what clean code already says. Comments like `// instantiate service`, `// loop through items`, or `// return false if null` are pure noise—delete them.
- **Explain the "Why", not the "What"**: Reserve comments for non-obvious rationale, hidden constraints, edge cases, workarounds, or domain invariants.
- **Zero agentic artifacts**: Remove any conversational traces, debugging notes, or agent self-narration (e.g., `// Added as requested`, `// Fixed bug seen in test output`, `// TODO: agent check`).

### Code Comment Anti-Patterns

| Bad Comment (Verbose / Obvious / Narrative) | Good Comment (Concise / High-Signal) |
| :--- | :--- |
| `// This function takes the user id, queries PostgreSQL to fetch the row, and returns null if the user is not found or deleted.` | *(None needed — function signature `getUser(id)` is self-documenting)* |
| `// Increment retry count by 1` | *(Delete — explains the obvious)* |
| `// Added 5000ms timeout here because we noticed the test was hanging when the upstream server took too long to respond.` | `// 5s timeout prevents hung sockets on stalled upstream keep-alives.` |
| `// We need to lock here so two threads don't write at the same time and cause race conditions.` | `// Serializes writes to prevent concurrent buffer corruption.` |

---

## 4. Mandatory Structure

Every PR description must follow this structure in order:

### 1. TL;DR (Top Line)
- Exactly one sentence at the very top of the description.
- Actively and precisely states what the PR does.
- *Example:* `Migrates session storage from local memory to Redis to allow multi-instance deployments.`

### 2. Current Behavior
- 1–3 concise sentences describing how the system behaved *before* this PR.
- Focus on the operational reality, bug, or limitation that existed.

### 3. Desired Change
- 1–3 concise sentences describing how the system behaves *after* this PR.
- Focus on the observable technical outcome and capabilities unlocked.

### 4. Implementation Strategy
- **HIGH LEVEL ONLY: 2–4 sentences.**
- Describe the architectural approach, data flow changes, or key design decisions.
- **Do NOT provide a file-by-file laundry list** (the diff already shows which files were touched). Explain *how* the change works conceptually.

### 5. Correctness Verification
- State exactly how you know the PR works and doesn't cause regressions.
- Include specific automated test commands run and their outcomes (e.g., `cargo test -p auth -- --nocapture`).
- List manual reproduction or verification steps performed.
- Mention edge cases explicitly verified.

### 6. Supporting Media / Data Tables *(if applicable)*
- Include UI screenshots (before/after), terminal recordings, flamegraphs, or benchmark comparison tables when relevant.
- If not applicable, omit this section entirely (do not leave empty placeholders like "N/A").

### 7. Appendices *(if applicable)*
- Clearly marked with an `## Appendix` header.
- This is the designated quarantine zone for verbose content: deep design rationale, benchmark methodology, full debug logs, or alternative solutions evaluated.
- Keeping verbose details in the appendix preserves the scannability of the main description while keeping deep technical context accessible.

---

## 5. PR Description Examples: Bad vs. Good

| Anti-Pattern (Bad) | Professional (Good) | Why |
| :--- | :--- | :--- |
| *Changes that foo setting.* | *Sets `session.max_idle_seconds` to 900 in `config/auth.yaml`.* | Explicit attribution: names the exact config key, file, and value. |
| *Fixed the bug where it broke during tests.* | *Handles `None` return values from `UserCache.get()` in `auth/middleware.py`.* | Identifies root cause and exact failure mode rather than vague pronouns. |
| *This PR was opened in order to optimize query latency by creating an index.* | *Adds a composite index on `(tenant_id, created_at)` in `events` table to reduce query latency.* | Active voice, concise, specifies database artifacts. |
| *Refactored `foo.py`, updated `bar.py`, renamed `baz.py`, and added a test in `test_foo.py`.* | *Consolidates user token extraction into `TokenValidator` and wraps incoming HTTP handlers with authentication middleware.* | High-level architectural strategy instead of a redundant file list. |
| *As we decided in our earlier session, I reverted that commit.* | *Reverts commit `a1b2c3d` (`feat: experimental websocket compression`) due to high memory overhead under sustained load.* | Self-contained context; no conversational leakage. |

---

## 6. Template

Use this Markdown template when drafting descriptions:

```markdown
TL;DR: <Single active-voice sentence stating what this PR does>.

## Current Behavior
<1-3 concise sentences on how things behaved before this change.>

## Desired Change
<1-3 concise sentences on how things behave after this change.>

## Implementation Strategy
<2-4 sentences explaining the high-level approach and key technical mechanisms. Avoid file laundry lists.>

## Correctness Verification
- **Automated Tests**: `<test command or suite>` passed (<number of tests> passed, 0 failures).
- **Manual Verification**: <Steps taken to manually exercise the change>.
- **Edge Cases Tested**: <Specific boundary conditions verified>.

## Supporting Media / Data Tables <!-- Optional: delete if not applicable -->
| Metric | Before | After | Delta |
| :--- | :--- | :--- | :--- |
| P95 Latency | 142ms | 38ms | -73% |

## Appendix: <Topic> <!-- Optional: delete if not applicable -->
<Verbose context, alternative designs evaluated, extensive benchmark methodology, or raw logs.>
```

---

## 7. Pre-Submission Checklist

Before finalizing any PR description, verify:

- [ ] **Code Comment Hygiene**: Was a comment review pass performed across the diff? (No obvious comments narrating code, no essay-like reporting, only concise notes on non-obvious "why").
- [ ] **TL;DR**: Does the top line start with a clear, active-voice `TL;DR:` sentence?
- [ ] **Explicit Attribution**: Are all pronouns grounded? (No ambiguous "it", "that setting", "the issue" without an explicit owner or name).
- [ ] **Zero Context Leakage**: Is there zero conversational leakage from the agent session or internal chain-of-thought?
- [ ] **High-Level Strategy**: Is the Implementation Strategy high-level (under 5 sentences), omitting redundant file-by-file lists?
- [ ] **Concrete Verification**: Are the verification steps concrete, reproducible, and includes exact test commands/outcomes?
- [ ] **Clean Separation**: Is any bulky/verbose context relegated to an explicitly titled `Appendix` section?
