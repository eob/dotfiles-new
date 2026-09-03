---
name: opencode
description: >-
  Invoke OpenCode CLI (`opencode`) for headless task execution, multi-model agent workflows,
  GitHub PR checkouts, and automated testing. Use when asked to run opencode, delegate tasks
  to OpenCode, or checkout PRs with opencode.
---

# OpenCode CLI Integration Skill

This skill enables agents to invoke the local **OpenCode CLI** (`opencode`) to execute background coding tasks, run multi-model code generation, or interact with GitHub pull requests.

---

## 1. When to Invoke OpenCode

- **Headless Task Execution**: Run autonomous coding workflows or test suites non-interactively using `opencode run`.
- **Multi-Model Delegation**: Leverage alternative models and providers configured in OpenCode (e.g., Gemini, Claude, OpenAI) to test cross-model implementations.
- **GitHub PR Review**: Checkout and analyze pull request branches directly using `opencode pr <number>`.
- **Session Continuity**: Continue or fork existing agent sessions across tasks.

---

## 2. Environment & Binary

- **Binary**: `/home/ted/.bun/bin/opencode` (available directly on `PATH` as `opencode`).
- **Configuration**: `~/.config/opencode/opencode.jsonc`.
- **Data / Storage**: `~/.local/share/opencode/`.

---

## 3. Core Commands & Workflows

### A. Non-Interactive Execution (`opencode run`)

1. **Basic Execution**:
   ```bash
   opencode run "Run unit tests in packages/core and fix any deprecation warnings."
   ```

2. **Targeting a Specific Model**:
   ```bash
   opencode run -m anthropic/claude-3-7-sonnet "Refactor query builder in db/query.ts."
   ```

3. **Running in a Specific Directory**:
   ```bash
   opencode run --dir /path/to/project "Check for missing TypeScript definitions."
   ```

4. **Attaching Context Files**:
   ```bash
   opencode run -f schema.sql -f config.json "Generate database migration script."
   ```

5. **Structured JSON Output** (for machine parsing):
   ```bash
   opencode run --format json "Validate JSON schemas in specs/"
   ```

### B. Pull Request Checkout (`opencode pr`)

Fetch and check out a PR branch into the local repository:

```bash
opencode pr 42
```

### C. Session Management

1. **Continue the Last Session**:
   ```bash
   opencode run -c "Now add integration tests for the endpoint created above."
   ```

2. **Fork from Previous Session**:
   ```bash
   opencode run -c --fork "Try an alternative approach using in-memory caching."
   ```

3. **Inspect Models & Providers**:
   ```bash
   opencode models
   ```

---

## 4. Best Practices for Calling Agents

1. **Non-Interactive Permissions**:
   - For autonomous scripts requiring bash execution, use `--dangerously-skip-permissions` only when running trusted operations in safe or isolated environments.
2. **Directory Awareness**:
   - Always specify `--dir` when calling OpenCode from an external worktree or repository root.
3. **Verify Diffs**:
   - Inspect `git status` and `git diff` after an OpenCode execution run to verify all changes before presenting results to the user.
