---
name: maintain-brain
description: Capture, organize, synthesize, retrieve, and maintain durable knowledge in this brain repository while preserving provenance and link integrity. Use when asked to remember something, update context, organize notes, or file research.
---

# Maintain Brain: Knowledge Architecture Protocol

Use this skill to maintain high structural and epistemic quality across this repository.

## 1. Search Before Creating
Before creating a new note or concept, query the local brain index:
```sh
brain search "<topic or concept>"
```
If related material exists, prefer enriching and linking to existing notes over creating duplicate fragments.

## 2. File Placement Discipline
- Reusable mental models $\rightarrow$ `notes/concepts/kebab-case-name.md`
- External articles and RFC digests $\rightarrow$ `notes/references/kebab-case-name.md`
- Active investigations $\rightarrow$ `notes/questions/kebab-case-name.md`
- Persistent multi-session collaborations $\rightarrow$ `discussions/kebab-case-name.md`
- Claims and verified decisions $\rightarrow$ `agent/model/claims.md`

## 3. Keep the Vector Index Hot
Whenever you add or meaningfully edit a markdown document:
```sh
brain embed <path-to-file>
```
Before ending a session, synchronize the repository:
```sh
brain sync "[descriptive commit message]"
```
