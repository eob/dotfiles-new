# {{REPO_NAME}}

Welcome to {{USER_NAME}}'s cognitive knowledge base and shared human-agent memory system.

## Navigation

- [`agent/`](agent/README.md) — Agent-governed model of {{FIRST_NAME}}, active context routing, and atomic claims ledger.
- [`profile/`](profile/README.md) — Human-readable synthesis of working model, current priorities, and open questions.
- [`notes/`](notes/README.md) — Structured durable knowledge:
  - [`notes/concepts/`](notes/concepts/README.md) — Reusable domain insights and mental models.
  - [`notes/questions/`](notes/questions/README.md) — Open investigations and research threads.
  - [`notes/references/`](notes/references/README.md) — Summaries and digests of external resources.
- [`projects/`](projects/README.md) — Active and exploratory project contexts.
- [`discussions/`](discussions/README.md) — Persistent, multi-session collaborative thinking notes.
- [`cowork/`](cowork/README.md) — Daily cowork logs, agendas, and rolling reminders.
- [`journal/`](journal/README.md) — Chronological entries and milestone logs.
- [`inbox/`](inbox/README.md) — Fast capture queue for raw thoughts before processing.
- [`archive/`](archive/README.md) — Inactive or superseded notes.

## Operating System & CLI

This repository is powered by the `brain` CLI from your dotfiles:

```sh
brain inbox next             # Triage pending intake tickets
brain search "<query>"       # Semantic & keyword search
brain today                  # Initialize today's cowork agenda
brain doctor                 # Check link validity, vector cache, and git status
brain sync "[message]"       # Sweep index, validate links, and push to origin/main
```
