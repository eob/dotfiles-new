---
name: reportfu
description: >-
  Global protocol for filing research, technical reports, and durable knowledge into a context-specific
  brain repository. Resolves $BRAIN_REPO, reads $BRAIN_REPO/AGENTS.md for local orientation,
  and delegates to private brain skills while keeping active codebase repositories clean.
  Use when asked to file reports, record research in the brain repo, consult brain context,
  or co-manage durable knowledge.
---

# reportfu: Global Brain Repository Protocol

**Reportfu** is the global "foot-in-the-door" protocol for filing reports, research summaries, technical memos, and durable knowledge into a context-specific **brain repository**.

This skill is intentionally thin, generic, and public across all environments (personal machines, work machines, open-source projects). It contains **zero personal data or private schemas**. Instead, it defines the high-level cognitive contract between the human, the active codebase, and whichever private brain repository is active in the current environment.

---

## 1. The Two-Repository Mental Model

Always maintain a strict separation between code execution and durable knowledge:

```text
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     Active Project Codebase     │       │     Brain Repository ($BRAIN_REPO)
│                                 │       │                                 │
│ - Source code & unit tests      │       │ - Durable research & reports    │
│ - Implementation plans (workfu) │ ────> │ - Architectural memos & briefs  │
│ - Task tickets (ticketfu)       │ cite  │ - Cross-project concepts        │
│ - Ephemeral bug repros          │       │ - Human+Agent co-management     │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

1. **Active Project Repository**: Where implementation happens. Follows `workfu` and `ticketfu`. Contains only code, tests, tickets, and operational artifacts strictly relevant to that project.
2. **Brain Repository (`$BRAIN_REPO`)**: Where durable insights, research briefs, architectural evaluations, and knowledge synthesis live across projects and time.

---

## 2. Dynamic Orientation Flow

Whenever you need to read from, consult, or write to a brain repository, follow this sequence:

### Step 2.1: Resolve `$BRAIN_REPO`
The path to the local checkout of the brain repository is supplied by the `$BRAIN_REPO` environment variable:

```bash
# Check if BRAIN_REPO is set in the environment
echo "$BRAIN_REPO"
```

- If `$BRAIN_REPO` is unset in the current shell, source `~/.zshrc.local` or prompt the user to define it:
  ```bash
  export BRAIN_REPO="/path/to/brain"  # Defined in ~/.zshrc.local
  ```
- If the directory does not exist or is inaccessible, inform the user and do not proceed with brain operations.

### Step 2.2: Read `$BRAIN_REPO/AGENTS.md` First
Every valid brain repository contains an **`AGENTS.md`** file at its root. 

**Reading this file is mandatory upon activation.** It serves as the local constitution for that specific brain, orienting the agent to:
- **Taxonomy & Directory Structure**: Where reports, concepts, journal entries, or references belong.
- **Agent Stance & Voice**: How to interact with the human collaborator in this specific context (e.g., personal life vs. employer/work project vs. open source).
- **Placement Rules**: Which subdirectories receive new or unclassified material (e.g., an intake inbox or specific topic folders).
- **Private Skills**: Pointers to local, context-specific skills located within the brain repository or user's local config.

### Step 2.3: Defer to Private Brain Skills
If `$BRAIN_REPO` or the local environment defines private skills (e.g., in `$BRAIN_REPO/.agents/skills/`, `$BRAIN_REPO/skills/`, or local harness directories):
- **Private skills supersede global defaults**: For domain-specific formatting, schema validation, profile updates, or ingestion pipelines, defer entirely to the rules established by those local skills.
- `reportfu` acts only as the universal entry point; the private skills govern the specialized domain logic.

---

## 3. Filing Discipline for Reports & Research

When generating reports, research summaries, or architectural briefs to file into `$BRAIN_REPO`:

### 3.1 Naming and Format Conventions
- **Format**: Durable plain-text Markdown (`.md`).
- **Filename**: Kebab-case, prefixed with ISO date if chronological (`YYYY-MM-DD-<topic>.md`) or descriptive topic name (`<system>-<topic>-evaluation.md`).
- **Header Metadata**: Include a standard frontmatter or top block:
  ```markdown
  # <Title of Report>
  - **Date**: YYYY-MM-DD
  - **Originating Context**: <Repo name or project identifier>
  - **Reference**: <Ticket name, branch, or commit SHA if applicable>
  - **Status**: Draft | Final | Archived
  ```

### 3.2 Clean Grounded Citations
- Connect the report back to reality: cite exact repositories, file paths, issue IDs, or external references.
- Never duplicate large chunks of product source code into the brain repo. Store the synthesis, findings, trade-offs, and citations; let the source code remain in the active project repo.

### 3.3 Atomic Commits in `$BRAIN_REPO`
Keep modifications to `$BRAIN_REPO` isolated, clean, and reviewable:
```bash
# Verify changes inside the brain repository
git -C "$BRAIN_REPO" status

# Stage and commit the specific report
git -C "$BRAIN_REPO" add <path-to-new-report>
git -C "$BRAIN_REPO" commit -m "docs(report): add <topic> evaluation"
```
Follow the brain repository's own git workflow (branches vs. main commits) as specified in its `AGENTS.md`.

---

## 4. Integration with the `-fu` Suite

`reportfu` connects seamlessly with the other craftsmanship skills:

- **`researchfu` → `reportfu`**: When deep technical research conducted under `researchfu` produces enduring insights or architectural decisions, file the resulting brief into `$BRAIN_REPO` using `reportfu`.
- **`workfu` → `reportfu`**: Operational implementation findings belong in the active ticket; cross-project architectural findings or generalizable lessons route to `$BRAIN_REPO`.
- **`ticketfu` ↔ `reportfu`**: Tickets track active delivery in the codebase; brain reports link to tickets for traceability without cluttering the project repo with long-form reflections.

---

## Quick Reference Checklist

- [ ] **Resolved `$BRAIN_REPO`**: Confirmed the environment variable is set and directory exists.
- [ ] **Read `AGENTS.md`**: Read `$BRAIN_REPO/AGENTS.md` to discover local taxonomy, stance, and intake paths.
- [ ] **Checked Private Skills**: Identified any local brain skills (in `$BRAIN_REPO/.agents/skills/` or similar) and followed their conventions.
- [ ] **Clean Separation Preserved**: Active code/tests kept in project repository; durable synthesis routed to `$BRAIN_REPO`.
- [ ] **Standard Report Structure**: Markdown file created with kebab-case naming, date, and originating context references.
- [ ] **Atomic Brain Commit**: Committed cleanly in `$BRAIN_REPO` with an informative commit message.
