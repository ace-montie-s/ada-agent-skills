# Shared implementation strategy

Load this reference when authoring, revising or fixing a playbook. Choose the
smallest implementation that meets the approved conversation. More steps and
higher reasoning are options to test, not goals.

## Choose from evidence

First identify the owning surface from the conversation and trace. For each
relevant option below, record selected or rejected, why, and the observable
check that would prove it. Do not prescribe a tool before checking whether the
runtime supports it and whether an existing tool already does the job.

| Evidence or requirement | Implementation to consider | Acceptance check |
|---|---|---|
| Missing or incorrect answer content, with no workflow dependency | Knowledge or coaching correction | Correct answer and evidence of which article was retrieved |
| A fact is missing and affects the next action | ASK only for that fact, with retry and fallback | Indirect answers work, known facts are skipped, missing answers have a safe ending |
| Duration, completed checks or another fact must survive later turns | SET explicit saved state | Preserve confirmed facts, accept explicit corrections, avoid repeated checks |
| A fixed policy chooses the outcome | IF_ELSE on confirmed variables | Test below, at and above each boundary, plus unknown state |
| Exact dates, arithmetic, normalization, validation or structured lookup | Reuse or create a small code tool, then branch on its result | Deterministic sample inputs, boundary cases, missing output and executor failure |
| Language extraction or precedence rules produce wrong state | Simplify the extraction, then compare Normal and High if ambiguity remains | Same inputs and expected outputs at both levels, including latency |

A numeric comparison on an already confirmed number can use a supported branch
directly. It does not require a code tool. A knowledge-only gap does not require
new state, extra questions or higher reasoning.

## State and conversation control

Use exact SET operations for copying, clearing or setting known values. Use
reasoning SET only when interpreting language. Extract after new customer
input, not twice from unchanged text. Include saved confirmed context when
re-entering a flow, and require an explicit correction before overwriting it.

Separate facts that control different decisions, such as duration and checks
already completed. ASK only for missing facts. Do not repeat completed checks
or infer consent from an unrelated answer. Give unknown values an explicit
path rather than treating them as false or eligible. Keep branches shallow.

## Tools and knowledge

List existing tools first. Give a new tool one job and clear input and output
names. Verify the current runtime schema. Set inputs before RUN, which does
not populate code tool inputs itself. Reset outputs before execution so a
missing response cannot reuse an earlier result. Branch explicitly on success,
unavailable and error outcomes; test the resulting conversation as well as the
tool. An answer on a confirmed branch should use that state rather than
recomputing the eligibility in prose.

If execution or tooling is unavailable, state that limit and use only a
supported fallback. Never invent a schema, execution result or passing test.
For knowledge, follow the runtime's retrieval limits and knowledge-set rules.
A staged article is not evidence it was retrieved. Record its actual use.

## Reasoning level

Normal is the default. Preserve existing reasoning settings when rewriting.
For ambiguous extraction or several interacting precedence rules, load
ada-tune-reasoning-level and compare Normal and High on identical inputs.
Choose using correctness first and latency second, keeping Normal on a tie.
Do not use blanket High or substitute reasoning for exact computation.

## Scope and proof

Internal SET, branch and tool restructuring can preserve an approved
conversation without a new design approval. Changes to the questions, their
order, the outcome or policy return to design-conversation unless that exact
change is already approved. Preserve acceptance criteria and controls.

Show the chosen strategy and expected effect. Stage, confirm success and read
back the changed entities before testing. A rejected stage is not a candidate;
do not spend runs testing unchanged configuration. Retest the full anchor and
controls, inspect transcripts and traces, and distinguish saved judge verdicts
from reviewer findings. Report untested branches and limits explicitly.
