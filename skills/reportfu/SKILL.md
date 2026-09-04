---
name: reportfu
description: >-
  Global protocol for filing research, technical reports, and durable knowledge into a context-specific
  brain repository. Use whenever the user asks to "show me", "report on", or "research" something whose
  scope is too large for the chat transcript, or when asked to record durable knowledge in the brain repo.
  Resolves $BRAIN_REPO, follows $BRAIN_REPO/AGENTS.md, and notifies the user with the report's file path.
---

# reportfu: Global Brain Repository Protocol

**Reportfu** is the global protocol for publishing reports, research briefs, technical evaluations, and durable knowledge into a context-specific **brain repository** (`$BRAIN_REPO`).

This skill is intentionally thin, generic, and public across all environments (personal machines, work machines, open-source projects). It contains **zero personal data or private schemas**. It establishes the medium-sizing boundary between chat and durable artifacts, resolves the local brain repository via environment variables, reads the brain's internal `AGENTS.md`, and delegates to private context-specific skills.

---

## 1. When to Trigger `reportfu` (The Medium Sizing Threshold)

Chat transcripts are ideal for active dialogue, quick alignment, command status, and concise decision-making. They are the **wrong medium** for large, multi-faceted research documents, architectural evaluations, deep code audits, or reference guides.

### Trigger Criteria
Use `reportfu` whenever:
1. **User Request Phrasing**: The user asks you to *"show me..."*, *"give me a report on..."*, *"research..."*, or *"write up a doc/memo about..."*.
2. **Scale & Depth Threshold**: The findings, evidence, or explanation are so detailed, structured, or extensive that presenting them in chat would flood the conversation history and degrade context efficiency.
3. **Durable Value**: The information has lasting value beyond the current pull request or immediate task (e.g. system models, technology comparisons, incident post-mortems, durable design decisions).

> [!TIP]
> **Pairing with `researchfu`**: If the user's question requires answering an unknown or investigating a complex system, execute the investigation using **`researchfu`** (answering briefs, gathering primary evidence, verifying mechanisms). Once synthesized, use **`reportfu`** to publish the resulting artifact into `$BRAIN_REPO`.

---

## 2. The Two-Repository Mental Model

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

## 3. Dynamic Orientation Flow

Whenever you interact with a brain repository, follow this sequence:

### Step 3.1: Resolve `$BRAIN_REPO`
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

### Step 3.2: Read `$BRAIN_REPO/AGENTS.md` First
Every valid brain repository contains an **`AGENTS.md`** file at its root. 

**Reading this file is mandatory upon activation.** It serves as the local constitution for that specific brain, orienting the agent to:
- **Taxonomy & Directory Structure**: Where reports, concepts, journal entries, or references belong.
- **Agent Stance & Voice**: How to interact with the human collaborator in this specific context (e.g., personal life vs. employer/work project vs. open source).
- **Placement Rules**: Which subdirectories receive new or unclassified material (e.g., an intake inbox, specific topic folders, or dated journals).
- **Private Skills**: Pointers to local, context-specific skills located within the brain repository or user's local config.

### Step 3.3: Defer to Private Brain Skills
If `$BRAIN_REPO` or the local environment defines private skills (e.g., in `$BRAIN_REPO/.agents/skills/`, `$BRAIN_REPO/skills/`, or local harness directories):
- **Private skills supersede global defaults**: For domain-specific formatting, schema validation, profile updates, or ingestion pipelines, defer entirely to the rules established by those local skills.
- `reportfu` acts only as the universal entry point; the private skills govern the specialized domain logic.

---

## 4. Filing Discipline for Reports & Research

When generating reports, research summaries, or architectural briefs to file into `$BRAIN_REPO`:

### 4.1 Naming and Format Conventions
- **Format**: Durable plain-text Markdown (`.md`).
- **Placement**: Follow the placement rules declared in the local `$BRAIN_REPO/AGENTS.md`.
- **Filename**: Kebab-case, prefixed with ISO date if chronological (`YYYY-MM-DD-<topic>.md`) or descriptive topic name (`<system>-<topic>-evaluation.md`).
- **Header Metadata**: Include standard frontmatter or a top block:
  ```markdown
  # <Title of Report>
  - **Date**: YYYY-MM-DD
  - **Originating Context**: <Repo name or project identifier>
  - **Reference**: <Ticket name, branch, or commit SHA if applicable>
  - **Status**: Draft | Final | Archived
  ```

### 4.2 Clean Grounded Citations
- Connect the report back to reality: cite exact repositories, file paths, issue IDs, or external references.
- Never duplicate large chunks of product source code into the brain repo. Store the synthesis, findings, trade-offs, and citations; let the source code remain in the active project repo.

### 4.3 Atomic Commits in `$BRAIN_REPO`
Keep modifications to `$BRAIN_REPO` isolated, clean, and reviewable:
```bash
# Verify changes inside the brain repository
git -C "$BRAIN_REPO" status

# Stage and commit the specific report
git -C "$BRAIN_REPO" add <path-to-new-report>
git -C "$BRAIN_REPO" commit -m "docs(report): add <topic> evaluation"
```
Follow the brain repository's own git workflow (branches vs. direct commits) as specified in its `AGENTS.md`.

---

## 5. The User Delivery Protocol

Once the report is filed and committed in `$BRAIN_REPO`:

1. **Do NOT dump the entire report into the chat transcript.** The user chose or triggered a report specifically to avoid chat clutter.
2. **Provide a concise executive summary** in the chat response (1-3 paragraphs or bullet points highlighting the bottom-line findings or decisions).
3. **Present the exact path to the filed report**:
   Always tell the user where the report has been placed using a clear file link:
   ```markdown
   I've left a report for you here: [/path/to/report.md](file:///path/to/report.md)
   ```
   (Alternatively, cite the relative path within `$BRAIN_REPO`, e.g., `notes/reports/YYYY-MM-DD-<topic>.md`).

---

## 6. Integration with the `-fu` Suite

`reportfu` connects seamlessly with the other craftsmanship skills:

- **`researchfu` → `reportfu`**: Deep technical investigations executed under `researchfu` publish their full, auditable briefs to `$BRAIN_REPO` via `reportfu`.
- **`workfu` → `reportfu`**: While implementation details and bug repros stay in project tickets, durable architectural insights or cross-cutting lessons route to `$BRAIN_REPO`.
- **`ticketfu` ↔ `reportfu`**: Tickets track active delivery in the codebase; brain reports link to tickets for traceability without cluttering the project repo with long-form reflections.

---

## Quick Reference Checklist

- [ ] **Threshold Checked**: Request is large/detailed enough that chat is the wrong medium; durable report is warranted.
- [ ] **Resolved `$BRAIN_REPO`**: Confirmed `$BRAIN_REPO` environment variable is set and directory exists.
- [ ] **Read `AGENTS.md` First**: Read `$BRAIN_REPO/AGENTS.md` to discover local taxonomy, stance, and intake paths.
- [ ] **Checked Private Skills**: Identified any local brain skills (in `$BRAIN_REPO/.agents/skills/` or similar) and followed their conventions.
- [ ] **Clean Separation Preserved**: Active code/tests kept in project repository; durable synthesis routed to `$BRAIN_REPO`.
- [ ] **Standard Report Structure**: Markdown file created with kebab-case naming, date, and originating context references.
- [ ] **Atomic Brain Commit**: Committed cleanly in `$BRAIN_REPO` with an informative commit message.
- [ ] **User Notified Cleanly**: Provided concise summary in chat and explicitly shared the file path (`"I've left a report for you here: ..."`).
