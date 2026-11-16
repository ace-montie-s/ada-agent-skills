---
name: visualize-tests
description: Turn existing Ada test results and transcripts into an Ada themed HTML review, with evidence-linked findings and exportable case and turn comments for the next iteration.
---

# Visualize tests

Create a review of what the agent actually said and did. Use this when someone wants to inspect test conversations, understand a failure in context, or leave feedback for the next iteration. This skill reads existing evidence and creates review artifacts. Running tests or changing agent behavior is a separate task.

## Pick the runtime

- With a shell and adacli, read [runtime-cli.md](references/runtime-cli.md).
- With the Ada MCP, read [runtime-mcp.md](references/runtime-mcp.md). A host with file and shell tools can also render the HTML locally.
- With attached exports, use those directly. Follow the relevant runtime's rendering or artifact fallback instructions.

Read [review-spec.md](references/review-spec.md) before preparing the normalized JSON or importing feedback. It defines the renderer's input and feedback contract.

## Build the review

1. Establish the use case, selected cases and source runs. Prefer the person's supplied run IDs or exports. Preserve the original artifacts. State the evidence scope, run target, date and missing information. A selected sample is not whole-agent performance.
2. Retrieve the complete saved case, criteria, transcript and available evaluation rationale for each selected run. Retain baseline and candidate runs when provided. A list summary is not a transcript. If evidence is truncated or unavailable, label that limitation and keep the result unknown where needed.
3. Normalize without rewriting the evidence. Keep stable review, revision, case, run and turn identities. Use source message IDs when available; otherwise assign deterministic turn IDs once and retain them. Preserve transcript order, speaker, original wording and recorded tool outcomes. Include an English translation for every non-English message alongside the original. Mark uncertain translations explicitly.
4. Preserve each criterion's literal pass, fail or unknown status and original rationale. Keep reviewer interpretation separate from that result. Do not convert a missing result, interrupted simulation or tool error into an agent failure. Do not turn a passing criterion into a pass for an untested journey.
5. Add concise findings that explain the experience: what was expected, what happened, and why it matters. Use failure, concern or limitation as appropriate. Anchor findings to the relevant source run and evidence turn, with an exact quote when available. A missing or later step remains unverified. Never invent dialogue, a tool outcome, a criterion or evidence to fill a gap.
6. Render the normalized JSON with the bundled renderer and inspect the HTML. Confirm the transcript reads in order, findings point to the intended turns, translations appear, and case and turn comments can be exported. Include passing and unknown evidence in the review as well as failures.

Keep the review focused on the customer experience, with Ada styling, clear case navigation and failure reasons visible beside the relevant turns. Before sharing externally, remove secrets and unnecessary personal data from every artifact and check that internal notes or reasoning are appropriate for the audience. Keep private source files separate from the shareable output.

## Collect feedback and iterate

The HTML stores comment drafts in that browser's local storage. It is a local review artifact, with no shared backend, synchronization or automatic feedback delivery. Tell the reviewer to use Copy feedback or Download JSON and return that export. Browser storage can be cleared or unavailable, and another device or origin may not have the drafts.

Import returned feedback against its review ID, revision, case ID, source run and turn or case target. Retain the quoted source and reviewer text. Surface mismatches for reconciliation instead of silently attaching a comment to a newer run. Preserve prior results and comments; a new test run gets its own identity and a new review revision. If supported feedback is supplied, render it with the review so the next reviewer can see the imported comments.

Treat comments as review input. Summarize the requested changes, distinguish disputed grading from agent behavior, and propose the smallest evidence-backed fix. Feedback does not authorize edits, test execution or promotion. Continue into the appropriate change workflow only within the person's authorized scope, then review the new run alongside the retained evidence.

Deliver the real HTML file or supported artifact link, the evidence scope and any material limitation, plus a brief instruction to return exported feedback. If rendering or hosting is unavailable, say so and provide the normalized JSON or a clearly labeled transcript fallback. Never invent a rendered URL.
