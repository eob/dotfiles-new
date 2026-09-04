---
name: codex
description: >-
  Invoke OpenAI Codex CLI (`codex`) for independent code reviews, second opinions, adversarial checks,
  or non-interactive task delegation. Use when asked to get a second opinion from Codex, run a codex review,
  or execute tasks with Codex.
---

# Codex CLI Integration Skill

This skill enables agents to invoke the local **OpenAI Codex CLI** (`codex`) to obtain an independent second-opinion review, run adversarial stress tests, or delegate execution tasks across model families.

---

## 1. When to Invoke Codex

- **Second-Opinion Code Review**: Run an independent review of uncommitted diffs or feature branches before submitting or merging a PR to catch blind spots.
- **Adversarial / Vulnerability Challenge**: Actively probe critical code paths (concurrency, auth, data migrations) for edge cases and failure modes.
- **Multi-Model Consultation**: Compare architectural decisions or implementation designs between models.
- **Task Delegation**: Execute bounded coding tasks non-interactively using `codex exec`.

---

## 2. Environment & Binary

- **Binary**: `/home/ted/.local/bin/codex` (available directly on `PATH` as `codex`).
- **Configuration**: `~/.codex/config.toml`.
- **Session Data**: `~/.codex/`.

---

## 3. Core Commands & Workflows

### A. Independent Code Review (`codex review`)

Use `codex review` to analyze git diffs non-interactively:

1. **Review Uncommitted Changes (Working Tree)**:
   ```bash
   codex review --uncommitted
   ```

2. **Review Against Base Branch (Feature Branch)**:
   ```bash
   codex review --base origin/main
   ```

3. **Review a Specific Commit**:
   ```bash
   codex review --commit <SHA>
   ```

4. **Review with Custom Prompt / Focus**:
   ```bash
   codex review --uncommitted "Focus specifically on race conditions, memory leaks, and error handling in network timeouts."
   ```

### B. Non-Interactive Task Execution (`codex exec`)

Use `codex exec` to delegate tasks or request focused analysis:

1. **Read-Only Inspection / Analysis** (safest):
   ```bash
   codex exec -s read-only "Analyze the schema migration in db/migrations/ and identify any breaking changes for Postgres 15."
   ```

2. **Workspace-Write Execution** (when Codex is authorized to edit files):
   ```bash
   codex exec -s workspace-write "Generate unit tests for auth/token.py covering expired and malformed tokens."
   ```

3. **Save Last Message to File**:
   ```bash
   codex exec -s read-only -o /tmp/codex-output.md "Summarize the architectural trade-offs between Redis and SQLite for session storage."
   ```

4. **Ephemeral Run** (avoid persisting session history to disk):
   ```bash
   codex exec --ephemeral -s read-only "Check if packages/core conforms to TypeScript strict mode."
   ```

---

## 4. Best Practices for Calling Agents

1. **Preserve Sandbox Boundaries**:
   - Prefer `-s read-only` whenever only feedback, analysis, or review is needed.
   - Use `-s workspace-write` only when the user explicitly requests code modification from Codex.

2. **Synthesize Findings (Do Not Blindly Echo)**:
   - Compare Codex's findings against your own context and code knowledge.
   - Filter out false positives or suggestions that conflict with project conventions.
   - Clearly delineate:
     - **Consensus**: Issues identified by both agents (high confidence).
     - **Unique Insights**: Valid bugs caught solely by Codex.
     - **Disagreements / False Positives**: Feedback that doesn't apply to the codebase.

3. **Active Voice & Grounded References**:
   - Maintain the standard established in `ticketfu`: cite exact filenames, symbols, and line numbers when reporting Codex review findings to the user.
