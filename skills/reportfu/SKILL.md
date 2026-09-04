---
name: reportfu
description: >-
  Global protocol for filing finished research, technical reports, and durable knowledge into a
  context-specific brain repository. Use whenever the user asks to "show me", "report on", or "research"
  something whose scope is too large for the chat transcript, or when asked to file/publish a report.
  Resolves $BRAIN_REPO, reads $BRAIN_REPO/AGENTS.md and local overlays for repository-supplied commands,
  holds the line on sourced claims and frozen dates, and notifies the user with the report's path or link.
---

# reportfu: Global Brain Repository Protocol

**Reportfu** is the global filing discipline for publishing finished investigations, research briefs, technical evaluations, and durable knowledge into a **brain repository** (`$BRAIN_REPO`) — a single-author research repository whose reports exist to teach their author and preserve institutional memory.

This skill is intentionally thin, generic, and public across all environments (personal machines, work machines, open-source projects). It contains **zero personal data, private schemas, or hardcoded toolchain commands**. It states the universal obligations of a durable report; the resolved repository's own `AGENTS.md` and local overlays supply the exact commands, folder paths, and publishing pipelines.

```text
[1. Trigger & Scope] ──> [2. Resolve One Repo] ──> [3. Read AGENTS.md / Overlay] ──> [4. File & Deliver]
  Chat vs. durable       Strict 4-probe table      Repository commands, specs,       Draft, verify, commit,
  Medium sizing check    No cross-contamination    prohibitions, & private skills    publish, link to user
```

---

## 1. When to Trigger `reportfu` (The Medium Sizing Threshold)

Chat transcripts are ideal for active dialogue, quick alignment, command execution, and iterative decisions. They are the **wrong medium** for multi-faceted research documents, architectural evaluations, deep code audits, or reference guides.

### Trigger Criteria
Use `reportfu` whenever:
1. **User Request Phrasing**: The user asks you to *"show me..."*, *"give me a report on..."*, *"research..."*, *"write something up"*, or *"turn this into a report"*.
2. **Scale & Depth Threshold**: The findings, evidence, or explanation are so detailed, structured, or extensive that presenting them in chat would flood the conversation history and degrade context efficiency.
3. **Durable Value**: The information has lasting value beyond the current pull request or immediate task (e.g. system models, technology comparisons, incident post-mortems, durable design decisions).

> [!TIP]
> **Pairing with `researchfu`**: If the user's question requires answering an unknown or investigating a complex system, execute the investigation using **`researchfu`** (answering briefs, gathering primary evidence, verifying mechanisms). Once synthesized, use **`reportfu`** to publish the resulting artifact into `$BRAIN_REPO`.

---

## 2. The Two-Repository Mental Model & Content Isolation

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

### The Non-Contamination Rule
Several brain repositories exist (e.g., work vs. personal), and their contents must **never mix**:
- **Stop and ask if the material mismatches the root**: Work material must never enter a personal repo, and personal material must never enter a work repo. A stale environment export is likelier than an intentional cross-over; `$BRAIN_REPO` alone is not proof of intent if the context clearly diverges.
- **Content never crosses brain repositories**: Not a report body, a baseline, an evidence file, or a quoted paragraph. The workflow is shared; the material stays put. A finding needed in a second repo must be re-derived there from sources that repo is authorized to see.
- **Write only under the resolved root**: Every other checkout on the machine is read-only reference: read it, cite it by path and pinned commit SHA, but put nothing in it. Filing into the wrong tree is a severe failure mode.

---

## 3. Resolve Exactly One Repository

Walk this probe table top to bottom, stop at the first match, and **write nothing until a root is confirmed**:

| Probe | Condition | Action |
| :--- | :--- | :--- |
| **1. Explicit Env Var** | `$BRAIN_REPO` is set, and that path is a valid git root holding `AGENTS.md` | Use it as the root. |
| **2. Broken Env Var** | `$BRAIN_REPO` is set, but missing, not a git root, or contains no `AGENTS.md` | Report the invalid path and stop. Do not guess or search for a substitute. |
| **3. CWD Candidate** | Unset, and the current working directory sits inside a brain repository | Name the root and the evidence for it, ask for confirmation, and write nothing until confirmed. |
| **4. Unset / Ambiguous** | Unset with no candidate, or multiple candidates | Ask which repository this belongs in. Do not guess a path, do not sweep the home directory, and do not create a repo. |

Once confirmed, if `$BRAIN_REPO` was unset, advise the user to export it in their shell profile (`~/.zshrc.local`):
```bash
git -C <confirmed-root> rev-parse --show-toplevel    # export BRAIN_REPO="<that path>"
```

---

## 4. Precedence & Orientation: Read That Repository First

Before drafting and again before publishing, read:
1. The root agent instructions at **`$BRAIN_REPO/AGENTS.md`**.
2. Any repository-specific overlay at **`$BRAIN_REPO/skills/reportfu/SKILL.md`** or **`$BRAIN_REPO/.agents/skills/`**.
3. Any authoring or taxonomy specs named by those files.

### Rules of Precedence
- **The repository beats this global file**: Its `AGENTS.md` and local overlay carry the filing specifics. Where either disagrees with this global skill on anything repository-shaped (paths, commands, front matter, markup, publishing endpoints, code standards) — **the repository wins**.
- **Code beats prose**: Confirm every command, front-matter key, component name, and CLI option against the repository toolchain's own help output or scripts before executing it.
- **A prohibition beats a permission**: Where a repository layer forbids what this global file allows, the prohibition strictly holds. Where all layers are silent on an obligation in §5, the obligation holds.

---

## 5. What Makes a Report "Done"

A report exists so a reader who was not present can act on the findings and verify them without asking the author.

- **Done Means Departed**: Built, verified, committed, pushed, and (if the repo uses a publishing pipeline) published to an accessible link or placed in the canonical archive directory. Work left dirty or uncommitted is a defect.
- **One Self-Contained Artifact**: Renders with no broken network fetches and no unpinned sibling assets. Diagrams ship rendered (or using standard markdown mermaid); images and tables stay within repository caps.
- **Sourced Claims**: Every load-bearing claim names a file path and line number, a command and its verbatim output, or a source pinned to a commit SHA or date. A claim whose only method is model recall is not evidence; pin the baseline while gathering.
- **Evidence Kept Apart from Interpretation**: Raw data, transcripts, test outputs, and measurements stay raw (committed in sibling evidence folders or appendix sections); synthesis and narrative live in the report body.
- **Unknowns Marked, Not Filled**: Explicitly state what the sources do not answer and what the reader must therefore not assume. One plausible guess devalues every verified claim beside it. Mark each claim's basis clearly; zero inferred claims or gaps across a long report is a red flag.
- **Actionable Ordering, Nothing Provisional**: Rank recommendations by consequence (what happens if each slips). Remove all boilerplate placeholders — a template still reading "TODO: fill in pins" advertises evidence that does not exist.

---

## 6. Global Obligation vs. Repository-Supplied Commands

Global `reportfu` enforces the obligations in the left column. The right column is repository-specific — look it up in `$BRAIN_REPO/AGENTS.md` or its local overlay rather than guessing:

| Universal Obligation (Global `reportfu`) | Repository Supplies (`AGENTS.md` / Overlay) |
| :--- | :--- |
| Single report unit with first-publication date frozen in it | The report tree layout, naming pattern, or scaffold command |
| Hand-authored source separated from generated deliverables | Source directory, build/verify commands, verifier vocabulary |
| Raw evidence and working synthesis cleanly demarcated | Sibling folder structure (`evidence/`, `raw/`, appendix conventions) |
| Claims carry provenance; gaps explicitly flagged | Specific marker syntax, callout styles, or confidence legends |
| Structure, voice, and taxonomy follow local standards | Placement directory (`notes/`, `reports/`, `inbox/`), authoring spec |
| Publication yields accessible link or durable file path | Publish command, hosting target, index/ledger file paths |
| A shipped version is never silently rewritten or deleted | Version bump command, versioned filename schema, changelog rules |
| Generated files and index registries are tool-owned | Which files/regions are generated and which tool owns them |

---

## 7. Version & Date Discipline

- **The date freezes at first publication**: It records when the world looked like this. A subsequent revision moves the version number or revision date, not the original publication date.
- **Tooling owns stamps**: If the repository provides a revision/bump command or generator script, rely on it to update version metadata, timestamps, and index registries. Never hand-edit tool-owned generated blocks.
- **A bump requires an informative note**: Explain what changed and why ("Replaced benchmark matrix after memory leak fix landed", never just "Updated").
- **Shipped versions remain permanent**: Once published or distributed, historical versions record what readers were told at the time. Never silently mutate historical claims.

---

## 8. Git Posture & Standing Push Authority

- **Pull before writing**: Run `git -C "$BRAIN_REPO" pull` at the start of the session and immediately before any write or publish. Pulling is safe and requires no confirmation.
- **Resolve merges yourself**: Read both sides and reconcile intent. Rebuild generated artifacts rather than attempting manual three-way diffs on compiled files.
- **Standing push authority**: Where the repository's `AGENTS.md` grants standing permission to commit and push (standard for single-author brain repositories), **take it**: make atomic commits and push directly to `main` without pausing for human confirmation. Work left unpushed or uncommitted on disk is stranded work. Where instructions are silent or require review, ask once.
- **Authority is strictly bounded**: Standing push authority applies **only** to `$BRAIN_REPO`. Every other codebase repository on the machine strictly retains its standard branching, worktree, and PR review rules (per `ticketfu`).
- **Interactive auth belongs to the human**: Never attempt interactive logins or credential prompts in automated runs; hand the exact command over to the user.

---

## 9. The User Delivery Protocol

Once the report is filed, committed, and pushed in `$BRAIN_REPO`:

1. **Do NOT dump the entire report into the chat transcript**: The user requested a report specifically because chat is the wrong medium for large artifacts.
2. **Provide a concise executive summary in chat**: 1–3 crisp paragraphs or key bullet points highlighting the bottom-line findings, architectural answers, or decisive evidence.
3. **Present the exact location to the user**:
   Always tell the user where the report has been placed:
   ```markdown
   I've left a report for you here: [/path/to/report.md](file:///path/to/report.md)
   ```
   If the repository has a publishing toolchain that generates a viewing URL, provide both the local repository file path and the published URL.

---

## 10. Integration with the `-fu` Suite

`reportfu` coordinates directly with the other craftsmanship skills:

- **`researchfu` → `reportfu`**: Deep technical investigations executed under `researchfu` publish their full, auditable briefs to `$BRAIN_REPO` via `reportfu`.
- **`workfu` → `reportfu`**: While project implementation details, test outputs, and bug repros stay in project tickets, cross-project architectural lessons and generalizable insights route to `$BRAIN_REPO`.
- **`ticketfu` ↔ `reportfu`**: Tickets track active delivery in codebases; brain reports cite tickets for traceability without cluttering code repositories with extensive conceptual documents.

---

## Quick Reference Checklist

- [ ] **Threshold Evaluated**: Request is large, detailed, or structured enough that chat is the wrong medium; durable report warranted.
- [ ] **Single Repo Resolved**: Followed 4-probe table; confirmed `$BRAIN_REPO` is a valid git root with `AGENTS.md`.
- [ ] **Content Non-Contamination Verified**: Checked that work material stays in work repos and personal stays in personal; no cross-pollution.
- [ ] **Read `AGENTS.md` & Overlays**: Read root `AGENTS.md` and any local overlay to acquire repo-supplied commands and placement paths.
- [ ] **Self-Contained & Sourced**: Load-bearing claims cite exact paths, lines, or commit SHAs; raw evidence kept distinct; unknowns explicitly flagged.
- [ ] **Git Sync & Standing Push**: Pulled latest changes before writing; committed and pushed to `$BRAIN_REPO` if standing authority granted.
- [ ] **Clean Delivery**: Did not flood chat; gave a concise executive summary and provided the file path/URL (`"I've left a report for you here: ..."`).
