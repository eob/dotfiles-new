---
name: ticketfu
description: >-
  Standard workflow for multi-agent collaboration in shared repositories. Ensures seamless coordination,
  handoffs, and credit-exhaustion recovery across agent harnesses (Claude Code, Codex, Muse, Antigravity, OpenCode)
  through authoritative ticketing, traceable branch naming, worktree awareness, periodic WIP checkpoints,
  placeholder draft PRs, structured handoff memos, and safe merge closures.
  Use when starting, claiming, executing, or completing work alongside other agents.
---

# Ticketfu: Multi-Agent Collaboration Workflow

You are one agent working alongside many in the same repository. It is essential that you work well together so agents can collaborate, integrate code cleanly, and recover work if one agent runs out of credits, exhausts its context window, or abruptly disconnects.

**Ticketfu** is the operating discipline for organizing work in multi-agent environments. Every task leaves an authoritative, public paper trail so that any agent or human can inspect progress, locate logs, or seamlessly take over without stranded local work.

---

## The Ticketfu Lifecycle

```text
[1. Ticket] ──> [2. Claim & Branch] ──> [3. Draft PR] ──> [4. Implement & WIP] ──> [5. Sync & Test] ──> [6. Review/Merge] ──> [7. Safe Teardown]
  Authoritative    In Progress state       [In Progress]      Periodic pushes,         Re-sync main,        Strip prefix,       Verify on remote,
  Markdown/Linear  Worktree conventions    Placeholder        prevent stranded work    verify tests         gh pr ready         delete LOCAL only
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

## 3. The Placeholder Draft PR

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
   - Follow the `write-pr-description` skill guidelines for structure and tone.
   - Summarize the high-level scope and intended solution.
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

## 4. Execution & Periodic Checkpoints (Preventing Stranded Work)

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

## 5. Context Depletion & The Structured Handoff Memo

If an agent is running low on context (or before intentional agent transitions), write a concise **Handoff Memo** in the ticket before stopping:

1. **What works**: Passing tests, verified endpoints.
2. **What is broken / unfinished**: The exact blocker or next uncompleted step.
3. **Reproduction command**: Exact command to test current state (e.g., `pytest tests/test_auth.py::test_jwt`).
4. **Next suggested action**: 1–2 sentences on what file or function to edit next.

Ensure all local WIP is committed and pushed before exiting.

---

## 6. Strict Takeover Protocol ("Trust But Verify")

- **Never take over another agent's ticket unless explicitly instructed by the user.**
- When instructed by the user to take over an existing ticket:
  1. Add an entry to the ticket's **Handoff & Takeover Log** recording your harness, machine, session ID, and timestamp.
  2. **The Verification Gate**: Run the test suite or reproduction command **first** before writing any new code. Verify the baseline state reported in the ticket rather than blindly assuming the previous agent's code is working.

---

## 7. Pre-Review Base Branch Sync & PR Finalization

When implementation is complete:

### Step 7.1: Re-Sync with `main`
In multi-agent repositories, other agents may have merged changes into `main` while you worked. Prevent stale merges:
```bash
git fetch origin main
git merge origin/main  # or git rebase origin/main
```
Resolve any conflicts and run the test suite to confirm compatibility with the latest `main`.

### Step 7.2: Finalize the PR
1. Push all clean, re-synced commits to the remote branch.
2. Remove the `[In Progress]` prefix from the PR title.
3. Mark the PR as ready for review:
   ```bash
   gh pr ready
   ```
4. Perform a pre-PR comment hygiene pass per `write-pr-description`.
5. Allow GitHub Actions / CI checks to pass.
6. Consult the human or merge according to repository instructions.

---

## 8. Safe Teardown, Cleanup, & Ticket Closure

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

---

## Quick Reference Checklist

- [ ] Ticket exists on `main` (markdown) or in Linear (assigned to Edward Benson).
- [ ] Ticket transitioned to `In Progress`.
- [ ] Repository worktree conventions checked (`git worktree list`).
- [ ] Branch (or worktree) created matching `<ticket-name>`.
- [ ] Ticket updated with branch, machine, harness, and session ID.
- [ ] Draft PR opened with `[In Progress]` title prefix and metadata in description.
- [ ] Ticket updated with PR link.
- [ ] Periodic WIP commits pushed to remote branch to prevent stranded work.
- [ ] If handed over: Handoff Memo written and all WIP pushed.
- [ ] If taking over: Baseline tests run and verified before writing code.
- [ ] Implementation executed using `workfu` (Red-first proof, dynamic planning, behavior pinning, gate matrix).
- [ ] Implementation complete; branch re-synced with latest `origin/main` and tested.
- [ ] PR title updated (stripped `[In Progress]`), marked ready for review (`gh pr ready`).
- [ ] Remote merge confirmed; local `main` pulled (and worktree removed if used).
- [ ] Ticket marked `Completed` with merged PR link.
- [ ] Local branch deleted; remote branch preserved.
