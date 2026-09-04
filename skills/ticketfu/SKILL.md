---
name: ticketfu
description: >-
  Multi-agent collaboration lifecycle, authoritative ticketing, and expert Pull Request (PR) delivery.
  Enforces seamless coordination, traceable branch/worktree naming, draft PR beacons, periodic WIP checkpoints,
  handoff memos, pre-PR code comment hygiene, expert PR descriptions (zero context leakage), and safe merge closures.
  Use when starting, claiming, executing, or completing work across agent harnesses, or when drafting and finalizing PRs.
---

# ticketfu: Work Lifecycle, Multi-Agent Collaboration, & PR Delivery

You are one agent working alongside many in the same repository. It is essential that you work well together so agents can collaborate, integrate code cleanly, and recover work if one agent runs out of credits, exhausts its context window, or abruptly disconnects.

**Ticketfu** is the operating discipline for organizing work in multi-agent environments. Every task leaves an authoritative, public paper trail so that any agent or human can inspect progress, locate logs, or seamlessly take over without stranded local work. It unifies the entire delivery pipeline—from ticket inception, branch/worktree setup, and early draft PR beacons, to pre-PR comment hygiene, expert PR descriptions, and safe merge closures.

---

## The Ticketfu Lifecycle

```text
[1. Ticket] ──> [2. Claim & Branch] ──> [3. Draft PR] ──> [4. Workfu Execution] ──> [5. Handoffs] ──> [6. Comment Hygiene] ──> [7. PR Description] ──> [8. Sync & Merge] ──> [9. Safe Teardown]
  Authoritative    In Progress state       [In Progress]      Red-to-Green cycle,      Structured memo,     Audit diff comments,     TL;DR, Strategy,         Re-sync main,        Verify remote merge,
  Markdown/Linear  Worktree conventions    Beacon & Metadata  WIP checkpoint pushes    verify baseline      strip agent artifacts    Verification, Metadata   gh pr ready, merge   delete LOCAL branch only
```

---

## 1. Ticket Creation & Placement

Before writing code, verify whether an authoritative ticket already exists for the requested task. If none exists, write one immediately.

### Naming Convention
- Use **kebab-case** format.
- Include a short letter prefix and number prefix if part of a series (e.g., `feat-101-auth-jwt`, `eng-04-cache-layer`, `fix-12-null-check`).
- The ticket name becomes the canonical identifier for the branch and related references.

### Determining the Authoritative Location
Determine the ticket system from repository documentation (e.g., `AGENTS.md`, `README.md`, or repository structure):

1. **In-Repository Markdown Tickets** (e.g., `tickets/`, `docs/tickets/`, `.tickets/`):
   - **CRITICAL**: The ticket file must exist on the **`main`** branch (committed and pushed to `main` or tracked centrally) so it remains globally visible across all worktrees and branches.
   - Use the template in [Ticket Markdown Template](#ticket-markdown-template).
2. **External Issue Tracker (e.g., Linear)**:
   - Use the Linear MCP tools to search for or create the issue.
   - Always assign **Edward Benson** to the ticket.

---

## 2. Claiming the Ticket, Workspace Setup, & Paper Trail

Transition the ticket to active work so no two agents collide:

### Step 2.1: Update State
Set the ticket status to `In Progress` (on `main` in the markdown store, or via Linear MCP).

### Step 2.2: Branch & Worktree Conventions
Follow the repository and local disk conventions:
- Check if the repository or workspace already uses git worktrees (e.g., run `git worktree list`).
- **If worktrees are used in the repository/project**: Create and switch to a dedicated worktree named identically to the ticket:
  ```bash
  git worktree add ../<repo>-<ticket-name> -b <ticket-name> main
  ```
- **If worktrees are NOT used**: Do not introduce them arbitrarily. Create and checkout the branch in place:
  ```bash
  git checkout -b <ticket-name>
  ```
Always name the branch **identically to the ticket**.

### Step 2.3: Record Recovery Metadata in the Ticket
Update the ticket with complete execution metadata:
- **Branch**: Exact branch name.
- **Machine**: Hostname or machine location (identifies where execution is occurring).
- **Harness**: The active agent harness (`claude-code`, `codex`, `muse`, `antigravity`, `opencode`).
- **Session ID**: Conversation or session UUID (critical for finding transcript logs in `~/.claude/`, `~/.codex/sessions/`, `~/.local/share/muse/sessions/`, or `~/.gemini/antigravity-cli/brain/`, or running `muse trace <id>` / `muse resume <id>`).

---

## 3. The Placeholder Draft PR (Coordination Beacon)

Early in the workflow, open a placeholder pull request on GitHub:

1. **Purpose**:
   - Provides an immediate, visible beacon for the human and other agents to monitor progress.
   - Serves as a central tracking anchor.
2. **Title**:
   - Prefix with `[In Progress]`:
     ```text
     [In Progress] <ticket-name>: <short imperative summary>
     ```
3. **Description**:
   - Summarize the high-level scope and intended solution using the [PR Description Standard](#7-crafting-the-expert-pr-description).
   - **Explicitly include the Agent Metadata block**:
     ```markdown
     ### Agent Metadata
     - **Harness**: <claude-code | codex | muse | antigravity | opencode>
     - **Machine**: <hostname or machine identifier>
     - **Session ID**: `<session-or-conversation-uuid>`
     - **Ticket**: <link to ticket or ticket filename>
     ```
4. **Draft Status**:
   - Open as a draft PR:
     ```bash
     gh pr create --draft --title "[In Progress] feat-101-auth-jwt: Add JWT validation" --body "..."
     ```
5. **Link Back to Ticket**:
   - Immediately update the ticket (in markdown on `main` or in Linear) with the URL of the created PR.

---

## 4. Execution Discipline & Periodic Checkpoints (Preventing Stranded Work)

Implement changes on your ticket branch with these multi-agent survivability habits:

### Execution Discipline: Follow `workfu`
- Follow the **`workfu`** skill for the disciplined development execution cycle:
  - Validate Red cases first (capturing verbatim failure evidence and proving reversibility).
  - Dynamic planning and sub-agent fan-out.
  - Turn Red to Green, run the validation gate matrix, and verify all acceptability criteria.
  - Pin newly uncovered invariants and symmetric failure modes with regression tests.
  - Record architectural decisions and durable findings in the ticket.
  - File any out-of-scope defects via `ticketfu`.

### Periodic WIP Checkpoint Commits & Pushes
- **Never accumulate large uncommitted diffs on local disk.**
- If an agent suddenly hits credit exhaustion, token rate limits, or crashes, dirty uncommitted files on one machine are invisible to other agents.
- Periodically make checkpoint commits and push them to the remote branch:
  ```bash
  git commit -m "wip: <ticket-name> checkpoint after auth middleware"
  git push origin <ticket-name>
  ```
- This guarantees that if the agent process dies, the successor agent can pick up directly from remote without manual file salvage.

### Dependency & Lockfile Hotspots
- If adding or updating dependencies (`package.json`, `Cargo.toml`, `pyproject.toml`), note it in the ticket.
- Avoid manual conflict resolution on large lockfiles (`pnpm-lock.yaml`, `Cargo.lock`). If merge conflicts occur later, re-generate lockfiles cleanly from `origin/main`.

---

## 5. Context Depletion, Handoff Memos, & Takeovers

### The Structured Handoff Memo
If an agent is running low on context (or before intentional agent transitions), write a concise **Handoff Memo** in the ticket before stopping:

1. **What works**: Passing tests, verified endpoints.
2. **What is broken / unfinished**: The exact blocker or next uncompleted step.
3. **Reproduction command**: Exact command to test current state (e.g., `pytest tests/test_auth.py::test_jwt`).
4. **Next suggested action**: 1–2 sentences on what file or function to edit next.

Ensure all local WIP is committed and pushed before exiting.

### Strict Takeover Protocol ("Trust But Verify")
- **Never take over another agent's ticket unless explicitly instructed by the user.**
- When instructed by the user to take over an existing ticket:
  1. Add an entry to the ticket's **Handoff & Takeover Log** recording your harness, machine, session ID, and timestamp.
  2. **The Verification Gate**: Run the test suite or reproduction command **first** before writing any new code. Verify the baseline state reported in the ticket rather than blindly assuming the previous agent's code is working.

---

## 6. Pre-PR Code Comment Hygiene Pass

Before drafting and finalizing the PR, **conduct a dedicated pass over all changed files to audit code comments**. 

AI coding agents tend to dump large, essay-like comments or narrative reports directly into code, severely impairing human readability. Enforce these rules across the diff:

- **Simple, concise, non-verbose**: Strip out paragraph-length explanations and deep reporting. Provide only essential, high-signal context.
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

## 7. Crafting the Expert PR Description

### 7.1 Tone & Core Philosophy
- **Simple, direct, active voice**: Use active verbs ("Adds", "Migrates", "Removes", "Fixes", "Refactors"). Avoid passive constructions ("This change was made in order to...").
- **Expert-to-expert communication**: Write for fellow technical peers. Speak plainly and directly. Do not over-explain basic programming concepts; clearly stated facts allow reviewers to immediately grasp the ramifications.
- **Zero conversational fluff**: Eliminate conversational filler, pleasantries, or preamble.

### 7.2 The Context Boundary (Agent Hygiene)
As an AI agent, you operate with a conversation history, system prompt, tool execution outputs, and internal chain of thought. **The PR reviewer has none of this context.** They only see the repository, git history, and the PR description.

- **The Zero-Leakage Rule**: Never mention or hint at ephemeral agent state, conversation steps, or prompt instructions (no *"As requested by the user..."*, *"In step 3 of the plan..."*).
- **Explicit Attribution**: Never use ambiguous pronouns ("it", "that thing", "the setting", "the issue"). Always specify whose setting, which module, or what exact error.

### 7.3 Mandatory Structure
Every PR description must follow this structure in order:

1. **TL;DR (Top Line)**: Exactly one sentence stating what the PR does.
2. **Current Behavior**: 1–3 concise sentences describing how the system behaved *before* this PR.
3. **Desired Change**: 1–3 concise sentences describing how the system behaves *after* this PR.
4. **Implementation Strategy**: **HIGH LEVEL ONLY: 2–4 sentences.** Describe the architectural approach. Do NOT provide a file-by-file laundry list.
5. **Correctness Verification**: Exact test commands run, outcomes, manual reproduction steps, and edge cases verified.
6. **Agent Metadata**: Harness, machine, session ID, ticket link.
7. **Supporting Media / Data Tables** *(if applicable)*: Benchmarks, latency tables, flamegraphs.
8. **Appendices** *(if applicable)*: Quarantine zone for verbose design rationale, raw logs, or alternative solutions evaluated.

---

## 8. Pre-Review Base Branch Sync, `gh pr ready`, & Merge Closure

When implementation and polish are complete:

### Step 8.1: Re-Sync with `main`
In multi-agent repositories, other agents may have merged changes into `main` while you worked. Prevent stale merges:
```bash
git fetch origin main
git merge origin/main  # or git rebase origin/main
```
Resolve any conflicts and run the test suite to confirm compatibility with the latest `main`.

### Step 8.2: Finalize the PR
1. Push all clean, re-synced commits to the remote branch.
2. Update the PR description with the final [PR Markdown Template](#pr-markdown-template).
3. Remove the `[In Progress]` prefix from the PR title:
   ```bash
   gh pr edit --title "<ticket-name>: <short imperative summary>"
   ```
4. Mark the PR as ready for review:
   ```bash
   gh pr ready
   ```
5. Allow GitHub Actions / CI checks to pass.
6. Consult the human or merge according to repository instructions.

---

## 9. Safe Teardown, Cleanup, & Ticket Closure

Follow this strict ordering to avoid lost state:

1. **Verify Remote Merge**:
   - Confirm that the PR is merged into `main`/`master` on the remote repository.
2. **Sync Local Main / Teardown Worktree**:
   - If a worktree was used, remove the worktree:
     ```bash
     git worktree remove ../<repo>-<ticket-name>
     ```
   - On the primary checkout, switch to `main` and pull:
     ```bash
     git checkout main && git pull origin main
     ```
3. **Close the Ticket**:
   - In Linear: mark the ticket as `Done`/`Completed` with the merged PR link.
   - In in-repo markdown (on `main`): mark status as `Completed` and record the final merged PR URL. Commit and push the updated ticket to `main`.
4. **Local-Only Branch Deletion**:
   - **Delete ONLY the local branch**:
     ```bash
     git branch -d <ticket-name>
     ```
   - **CRITICAL SAFETY RULE**: **Leave the remote branch intact** as a safety precaution and backup history. Do not delete `origin/<ticket-name>`.

---

## Reference Templates

### Ticket Markdown Template

Use this format when storing tickets in-repo:

```markdown
# <ticket-name>: <Short Summary>

- **Status**: In Progress | Completed | Blocked
- **Branch**: `<ticket-name>`
- **Machine**: `<hostname-or-location>`
- **Harness**: `<claude-code | codex | muse | antigravity | opencode>`
- **Session ID**: `<session-uuid>`
- **PR**: <PR URL or "Pending">
- **Assignee**: Edward Benson

## Goal
<Clear, 1-2 sentence description of the outcome>

## Context & Requirements
- <Requirement 1>
- <Requirement 2>

## Handoff & Takeover Log
- `YYYY-MM-DD HH:MM`: Started by `<harness>` on `<machine>` (Session `<session-uuid>`).

## Handoff Memo (If Paused / Handed Over)
- **Verified Working**: <e.g. Models migrated, unit tests pass>
- **Pending / Blocker**: <e.g. Integration test fails on token expiry>
- **Repro Command**: `<e.g. pytest tests/test_token.py>`
- **Next Action**: <e.g. Inspect refresh token rotation in auth.py>
```

### PR Markdown Template

Use this format when opening and finalizing pull requests:

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

### Agent Metadata
- **Harness**: <claude-code | codex | muse | antigravity | opencode>
- **Machine**: <hostname or machine location>
- **Session ID**: `<session-or-conversation-uuid>`
- **Ticket**: <link to ticket or ticket filename>

## Supporting Media / Data Tables <!-- Optional: delete if not applicable -->
| Metric | Before | After | Delta |
| :--- | :--- | :--- | :--- |
| P95 Latency | 142ms | 38ms | -73% |

## Appendix: <Topic> <!-- Optional: delete if not applicable -->
<Verbose context, alternative designs evaluated, extensive benchmark methodology, or raw logs.>
```

---

## Quick Reference Checklist

- [ ] **Ticket Exists**: Ticket exists on `main` (markdown) or in Linear (assigned to Edward Benson).
- [ ] **Ticket Claimed**: Ticket transitioned to `In Progress`.
- [ ] **Workspace Prepared**: Repository worktree conventions checked; branch created matching `<ticket-name>`.
- [ ] **Recovery Metadata Logged**: Ticket updated with branch, machine, harness, and session ID.
- [ ] **Draft PR Beacon Opened**: Opened draft PR with `[In Progress]` title prefix and Agent Metadata.
- [ ] **Ticket Linked**: Ticket updated with PR link.
- [ ] **WIP Checkpoints Pushed**: Periodic WIP commits pushed to remote branch to prevent stranded work.
- [ ] **Execution Disciplined**: Implementation executed using `workfu` (Red-first, gate matrix, pinned tests).
- [ ] **Comment Hygiene Audited**: Diff reviewed; obvious comments removed, non-obvious "why" retained, zero agent artifacts.
- [ ] **Code Simplified**: Accidental complexity and dead scaffolding audited (using `simplifyfu`).
- [ ] **Second Opinion Checked**: Optional adversarial review on diff (using `codex`).
- [ ] **PR Finalized**: Description formatted per template; `[In Progress]` stripped from title; marked `gh pr ready`.
- [ ] **Re-Synced & Tested**: Branch merged with latest `origin/main` and passes all validation gates.
- [ ] **Remote Merge Confirmed**: PR merged on remote; local `main` pulled (worktree cleaned up).
- [ ] **Ticket Closed**: Marked `Completed` with merged PR link.
- [ ] **Safe Cleanup**: Local branch deleted; remote branch preserved.
