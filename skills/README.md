# Agent Skills

A collection of portable, modular skills for AI agents (Claude Code, Google Antigravity, OpenAI Codex CLI, OpenCode, Cursor, etc.) managed within dotfiles.

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

| Skill | Description |
| :--- | :--- |
| [`write-pr-description`](./write-pr-description/SKILL.md) | Standard guide and template for writing clear, concise, expert-level PR descriptions and pre-PR comment hygiene. |
| [`do-good-research`](./do-good-research/SKILL.md) | Plan, conduct, and present evidence-backed, auditable technical research. |
| [`codex`](./codex/SKILL.md) | Invoke OpenAI Codex CLI (`codex`) for second opinions, adversarial reviews, and task delegation. |
| [`opencode`](./opencode/SKILL.md) | Invoke OpenCode CLI (`opencode`) for headless execution, multi-model agent runs, and PR checkouts. |

## Integration & Discovery

Running `make install` or `install.d/shared/08_agent_skills.sh` ensures each agent's skills directory exists and **copies** the shared public skills into place:

- **Claude Code**: `~/.claude/skills/`
- **Google Antigravity**: `~/.gemini/config/skills/`
- **OpenAI Codex CLI**: `~/.codex/skills/`
- **OpenCode**: `~/.config/opencode/skills/`

> [!NOTE]
> Skills are copied rather than symlinked to allow you to maintain private or work-specific skills locally in your agent directories without exposing them to this public dotfiles repository. Re-running the script safely updates the public skills without touching any private skills.
