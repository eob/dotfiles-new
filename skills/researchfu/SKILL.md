---
name: researchfu
description: Plan, conduct, and present evidence-backed technical research that answers a consequential question and makes the reasoning auditable. Use for investigations, architecture exploration, incident analysis, comparisons, unfamiliar systems, and decision support; not for simple factual lookups.
---

# researchfu: Evidence-Backed Technical Research

Good research reduces uncertainty for a purpose. It learns enough of the right
things to change what the reader can believe, predict, or do, while keeping the
evidence, reasoning, limits, and consequences open to inspection.

## Begin with an answerable brief

Before searching, record:

- the question, in a form evidence could answer;
- the audience and the decision, explanation, or action the answer enables;
- the boundary, time range, source baseline, and neighboring questions outside
  scope;
- the leading hypotheses, including the boring one, and what would support or
  falsify each;
- the stopping condition: what must be known for the answer to become useful.

Scope and baseline are parts of the claim. One version, run, dataset,
environment, or sample does not silently generalize to the whole system. Update
the brief as evidence changes; do not let the investigation drift.

## Build an auditable evidence base

Prefer evidence closest to the phenomenon: direct observation, raw artifacts,
source code, configuration, measurements, first-party records, and
authoritative documentation. Use summaries to discover primary evidence, not
as substitutes. Check a current source for changeable facts.

For each material source, record its identity, revision or date, the question
it informs, the relevant observation, and its limits. Capture ephemeral logs,
traces, outputs, and experimental conditions before they disappear.

Read underlying evidence, not only its label. A dashboard status, assertion
diff, search snippet, or document title is an interpretation; raw output and
the mechanism that produced it may tell a different story.

## Keep evidence states distinct

Classify important claims while working:

- **Verified:** directly supported by a named source or controlled observation.
- **Reported:** stated by a person or document but not independently checked.
- **Inferred:** the best explanation, with the missing check named.
- **Refuted:** contradicted by stronger evidence; retain it when useful.
- **Unknown:** unanswered. Mark the gap instead of completing the pattern with
  a plausible guess.

Observation is not causation. “These occurred together” and “this produced
that” require different evidence. Explain conflicting measurements or leave
the conflict visible; do not blend them into a confident average.

## Research mechanisms, not mentions

Finding every mention is reconnaissance. Understanding requires a model that
predicts behavior. For a system, investigate boundaries, contracts, state
ownership, control versus data flow, invariants and enforcement, ordering and
feedback loops, dependency failures, scaling limits, and extension seams.

Trace one realistic operation end to end. For deeper work, also trace a failure
and a change. If a load-bearing step is missing, return to evidence rather than
writing around the gap.

## Search broadly and triangulate deliberately

Include web search when external context, current behavior, prior art, or
public documentation could change the answer. Skip it only when the question is
wholly local, the material is confidential, or web access is out of scope.
Search several formulations, follow claims to the most primary source
available, and record URL, publisher, publication or revision date, and access
date. Search snippets and AI summaries are leads, not evidence.

Use genuinely different lenses: implementation, runtime observation, history,
documentation, measurement, operator experience, user experience, and a
comparable system. Several pages repeating one upstream assumption still count
as one source.

Use workflows and subagents to keep lanes independent. Give each a bounded
question, baseline, permitted sources, expected artifact, and falsifiers.
Useful lanes include discovery, mechanism tracing, measurement, history,
comparison, and a challenger constructing the strongest alternative explanation
or counterfactual. Do not tell the challenger which conclusion to reach.
Require claims with citations, counterevidence, gaps, and confidence.

Subagent output is not evidence. Reconcile lanes against underlying sources and
observations. Resolve disagreement by evidence quality, not majority vote, and
keep consequential conflicts visible.

## Try to defeat the emerging answer

Search for counterexamples as actively as support. Passing cases, negative
results, neighboring implementations, failed hypotheses, and earlier versions
often isolate a mechanism better than the original failure. Ask what would
make the favored explanation impossible, then look for it.

Before an experiment, define the expected signal. Record environment, inputs,
controls, output, confounders, and reproduction status. Change one explanatory
variable at a time when possible. A green exit does not prove the intended path
executed; verify the path and sample count. One run is a case, not a rate.

## Synthesize throughout, then stop

Maintain a claim–evidence map. For each finding, record its strongest support,
counterevidence, confidence, remaining gap, and consequence. Cluster evidence
by mechanism rather than collection order or surface symptom. Separate “what
happened” from “why we think it happened.”

Periodically write the best current answer in one sentence. If it cannot be
stated plainly, the model is probably still a catalog. Find the mental model
that predicts behavior and show how the parts constrain one another.

Stop when more research is unlikely to change the decision: the main mechanism
is supported, decision-changing contradictions are resolved, material
uncertainties are explicit, and the brief is answered. Do not keep reading to
avoid committing to an answer.

## Present the reasoning for challenge and use

Presentation is part of the research. Lead with the answer, scope, baseline,
and confidence—not the chronology of the investigation. State findings as
assertions someone could dispute. Then give the mental model, decisive
evidence, counterevidence, limitations, implications, and unresolved questions.
Keep exhaustive artifacts off the main path.

Place evidence beside its claim. Use tables for exact mappings, diagrams for
relationships, and prose for causation and judgment. Quantify from the source.
Label uncertainty directly instead of hiding it in hedged prose.

Recommendations must follow from findings. Name the action, owner or change
locus, evidence, expected signal, and consequence of delay. For a non-obvious
choice, state what is traded, who pays, the strongest alternative, why this is
right now, and what observation should reverse it.

Before delivery, ask whether a skeptical reader can tell what is known, how it
is known, what remains unknown, what could overturn the conclusion, and what to
do next. When practical, include a few fast, read-only checks with expected
results and falsifiers so the reader can see whether the research is still true.

## Publishing Durable Research via `reportfu`

When research briefs, evidence catalogs, or architectural comparisons are too extensive for the chat window or carry durable value across projects, publish the complete artifact to `$BRAIN_REPO` using **`reportfu`**. Orient using `$BRAIN_REPO/AGENTS.md`, commit cleanly, provide a concise executive summary in chat, and point the user directly to the filed document (`"I've left a report for you here: ..."`).
