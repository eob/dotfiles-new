---
name: orient-agent
description: Orient an AI agent encountering this brain repository for the first time. Explains repository layout, epistemic rules, context loading discipline, and CLI tooling. Use when first starting work in this repository.
---

# Orient Agent: First-Time Guide to the Brain

This repository is a persistent human-AI cognitive system for {{USER_NAME}}. It stores durable memory, operating context, mental models, references, and daily cowork logs. It is designed to be plain Markdown, human-auditable, and collaborative.

When you enter this repository as an agent, follow this guide to understand your boundaries, avoid common mistakes, and load context responsibly.

---

## 1. Epistemic Stance & Person Model

{{USER_NAME}} is an active builder and thinker. Treat this repository as an extension of their cognition.

- **Respect the Evidence Hierarchy**: Distinguish direct statements (what {{FIRST_NAME}} said), direct observations (code/text changes), external corroborations, and agent inferences. See [`../../../agent/model/evidence-policy.md`](../../../agent/model/evidence-policy.md).
- **Never Fabricate or Over-infer**: Preserve contradictions instead of forcing premature coherence.
- **Sovereignty**: {{FIRST_NAME}}'s live instructions in conversation always supersede any prior model or stored note.

---

## 2. Repository Architecture & Layout

The directory structure separates agent-governed operations from human-first knowledge:

```text
{{REPO_NAME}}/
├── .agents/skills/      # Repository-local agent skills
├── agent/               # Agent-governed operational memory and tools
│   ├── context/         # core.md (compact bootstrap) and load-map.md (routing table)
│   ├── model/           # claims.md (atomic ledger), uncertainties.md, revisions.md
│   └── personalities/   # jarvis.md and behavioral stances
├── profile/             # Human-readable synthesis projections of the agent model
├── notes/               # Durable human knowledge (concepts/, questions/, references/)
├── journal/             # Chronological dated entries (journal/YYYY/YYYY-MM-DD.md)
├── projects/            # Project context, strategy memos, and roadmap
├── cowork/              # Daily cowork logs (cowork/YYYY/YYYY-MM-DD.md)
├── inbox/               # Fast, unclassified capture area
├── archive/             # Inactive notes (never silently deleted)
└── AGENTS.md            # Concise repository constitution for all agents
```

---

## 3. Tooling & CLI

Always leverage the unified `brain` CLI from your dotfiles:
- `brain search "<query>"`: Hybrid vector + keyword search. Run before answering open questions.
- `brain today`: Initialize or view today's daily cowork agenda.
- `brain doctor`: Run health check across Markdown links, vector store, and git status.
- `brain sync`: Sweep index, validate links, commit, and push to origin/main.
