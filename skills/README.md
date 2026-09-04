# Agent Skills

A collection of portable, modular skills for AI agents (Claude Code, Google Antigravity, OpenAI Codex CLI, OpenCode, Muse, Cursor, etc.) managed within dotfiles.

## Organization

Each skill lives in its own directory with a standard layout:

```text
skills/
├── <skill-name>/
│   ├── SKILL.md          # Required: Main instruction file with YAML frontmatter
│   ├── examples/         # Optional: Reference implementations and examples
│   ├── scripts/          # Optional: Helper scripts and automation
│   └── references/       # Optional: In-depth documentation or notes
```

## Available Skills

### The Fu Suite (Autonomous Craftsmanship & Lifecycle)

| Skill | Description |
| :--- | :--- |
| [`ticketfu`](./ticketfu/SKILL.md) | Multi-agent collaboration & lifecycle: authoritative ticketing, traceable branch naming, worktree awareness, draft PRs, and safe merge closures. |
| [`workfu`](./workfu/SKILL.md) | Disciplined development execution: Red-first validation, dynamic planning, sub-agent fan-out, turning Red to Green, gate matrices, and behavior pinning. |
| [`debugfu`](./debugfu/SKILL.md) | Systematic root-cause debugging: Hypothesis-driven 4-phase diagnostic investigation (Isolate → Observe → Prove → Remedy). |
| [`simplifyfu`](./simplifyfu/SKILL.md) | Code simplification & anti-bloat: Post-implementation audit to strip accidental complexity, YAGNI bloat, and dead scaffolding. |
| [`prfu`](./prfu/SKILL.md) | Pull request descriptions & comment hygiene: Guide and template for expert-level PR descriptions and pre-PR code comment audits. |
| [`researchfu`](./researchfu/SKILL.md) | Evidence-backed technical research: Plan, conduct, and present auditable technical research for consequential decisions. |

### Harness CLI Connectors

| Skill | Description |
| :--- | :--- |
| [`codex`](./codex/SKILL.md) | Invoke OpenAI Codex CLI (`codex`) for independent code reviews, second opinions, adversarial checks, and non-interactive delegation. |
| [`opencode`](./opencode/SKILL.md) | Invoke OpenCode CLI (`opencode`) for headless task execution, multi-model agent workflows, and PR checkouts. |

## Integration & Discovery

Running `make install` or `install.d/shared/08_agent_skills.sh` ensures each agent's skills directory exists and **copies** the shared public skills into place:

- **Claude Code**: `~/.claude/skills/`
- **Google Antigravity**: `~/.gemini/config/skills/`
- **OpenAI Codex CLI**: `~/.codex/skills/`
- **OpenCode**: `~/.config/opencode/skills/`
- **Muse**: `~/.config/muse/skills/`

> [!NOTE]
> Skills are copied rather than symlinked to allow you to maintain private or work-specific skills locally in your agent directories without exposing them to this public dotfiles repository. Re-running the script safely updates the public skills without touching any private skills.
