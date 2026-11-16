# Review input and feedback

The renderer accepts UTF-8 JSON, uses only Python's standard library, and produces one offline HTML file. All supplied text is displayed as text, including Markdown and transcript URLs. No remote scripts, fonts, analytics, or comment service are loaded.

## Required shape

```json
{
  "schema_version": 1,
  "review_id": "delivery-review",
  "revision": "candidate-2",
  "title": "Delivery support test review",
  "summary": "One recorded check failed. Review the highlighted turn before changing the guidance.",
  "date": "16/11/2026",
  "limitations": ["External calls were blocked. Actual delivery to a person was not tested."],
  "history": [{"label": "Baseline", "result": "1/2 passed", "note": "Same saved criteria"}],
  "sources": [{"label": "Test dashboard", "url": "https://example.invalid/tests"}],
  "cases": [{
    "id": "delivery-1",
    "title": "Delivery is late",
    "run_id": "run-2",
    "status": "fail",
    "summary": "Support was offered before asking for delivery status.",
    "coverage": "Simulation with a known customer role. Greeting was not exercised.",
    "criteria": [{"id": "check-1", "text": "Ask for delivery status before offering support.", "status": "fail", "reason": "The first reply offered support without asking for status."}],
    "turns": [
      {"id": "message-1", "role": "user", "language": "en", "text": "My delivery is late."},
      {"id": "message-2", "role": "agent", "language": "en", "text": "Would you like to speak with support?"}
    ],
    "findings": [{"id": "finding-1", "kind": "failure", "turn_id": "message-2", "criterion_id": "check-1", "quote": "Would you like to speak with support?", "title": "Support offered before clarification", "observed": "The agent offers a person immediately.", "expected": "Ask whether the delivery is still in progress, then offer the relevant next step."}]
  }]
}
```

IDs use letters, digits, dots, colons, underscores or hyphens, starting with a letter or digit. Case IDs are unique. Turn, criterion and finding IDs are unique within their case. Use original source IDs when available. Keep IDs across regenerations of the same run. Change `revision` when evidence or interpretation changes. A content fingerprint also prevents importing feedback against altered evidence under the same revision.

Case and criterion `status` are `pass`, `fail` or `unknown`. Preserve the evaluator's literal result, including disagreement. Missing or incomplete evaluation is `unknown`, not a pass. Optional `conversation_id` links evidence identity. `run_id` is always present; use an explicit unknown label if unavailable. Empty `turns` is allowed when the transcript is unavailable; explain the missing evidence in `coverage`.

Turn `role` is `user`, `agent`, `system`, `human` or `tool`. Label tool traces and system events separately from customer-visible text. Supply `language` for each turn. Non-English messages need a faithful English `translation`; optional `translation_note` identifies review-only or approximate translations. Do not silently rewrite the original. Redact unnecessary contact and secret data before rendering, including in translations, criteria, findings and source URLs. Label redactions and any omitted non-text content.

`findings` anchor to a recorded `turn_id`. `quote`, if supplied, must be an exact substring of the original message and is highlighted. A `failure` defaults to `basis: "evaluator"` and must reference an actually failed `criterion_id`. A failure with `basis: "reviewer"` instead requires a nonempty `rule` naming the person's acceptance requirement violated by the recorded turn. It can coexist with a saved pass or unknown result. Do not rewrite the saved case or criterion status. The HTML displays and filters reviewer failures separately, alongside the preserved saved result. Use reviewer failure for a clear acceptance breach, including a judge miss; use `concern` for uncertain interpretation or a question needing review. `limitation` describes missing proof, blocked integrations or harness constraints. Every finding has `title`, `observed` and `expected`; expected is a proposed experience, never a fabricated observed response. Findings explain evidence and do not prove root cause unless a trace supports it.

Only include supplied runs and full available transcripts. History is optional; make cohorts, denominators and limitations explicit. Test pass counts are not production containment. Source links accept HTTP(S) only; do not embed credentials or private tokens.

## Feedback round trip

The HTML offers a decision and comment on every case and turn. Drafts use browser storage scoped to review, revision and evidence fingerprint. It reports storage or clipboard failure and offers a manual copy fallback. Downloaded JSON contains `schema_version`, `review_id`, `revision`, `fingerprint`, `exported_at`, and `comments`. Each comment has `case_id`, `case_title`, `run_id`, nullable `turn_id`, full original `quote` (empty for a case), `comment`, and `decision` (`agree`, `disagree`, `change`, `question`, or empty).

Import feedback in the HTML or render with `--feedback`. Imports reject changed evidence, unknown IDs and modified quotes. The browser refuses to overwrite conflicting drafts. Copy feedback produces human-readable text with review identity, revision, source run, turn and original quote. Download JSON is the structured handback for future tooling. Neither action sends feedback to the assistant automatically. Browser drafts are not shared between reviewers, browser profiles or machines.

On receiving feedback, reconcile the stable targets with the source, preserve disputes and requests as review input, summarize the proposed change, and route authorized edits and retests through the owning workflow. Exporting or agreeing with feedback does not authorize production changes. Keep the original review and generate a new revision after retesting. Cross-revision carryover is a deliberate reconciliation, not an automatic import.
