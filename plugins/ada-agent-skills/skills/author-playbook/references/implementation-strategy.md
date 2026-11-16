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
| A step answers from Knowledge, finds nothing, and apologises or asks "did that help?" | Exit on no answer (section below) | Reasoning log shows the search ran, no SEND or ASK from the playbook, and one reasoner reply |

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

## Exit on no answer

Use this when a playbook step answers from Knowledge and a failed lookup
leaves the customer with "I can't find this" and a "did that help?" ask.
Tested on a sandbox agent on 16/11/2026.

1. SET one variable in reasoning mode, with no fallback. Instruction:
   `Answer the customer's question using {{ search:knowledge }}. Write an
   answer only if Knowledge states it.`
2. IF the variable is null, RUN exit. Put no SEND before it.
3. ELSE SEND the answer with `{{ variable:<id> }}`, then ASK if it helped.

The reasoner then handles the turn with every playbook and article in reach.

- Use one variable per SET. A SET that writes two or more variables never
  searches and clears all of them.
- Give it no fallback. A fallback makes the variable non-null, so the branch
  never exits.
- Use an explicit RUN exit. A playbook that runs to its last step is hidden
  from the reasoner for one turn. An explicit exit is not.
- The model decides "no answer". Near-miss results still wrote nothing, so
  null means Knowledge does not state it.
- The query reads the step instruction and the last 10 messages. Add
  `{{ variable:<id> }}` to carry an earlier answer.
- Three searches run per turn, shared with SEND steps. A fourth writes null.
- Modular reasoner v2, headless runs and escalation playbooks never search,
  so every run exits.
- The flag `pb-v2-set-step-search` must be on. With it off the step writes
  null every time. adacli cannot read the flag, so the test is the check.
- After the exit the reasoner may answer, decline or start another playbook.
  Promise the customer no route.

Test three cases and read the reasoning log, not only the reply. Confirm the
playbook ran, since another playbook can take the first turn. Run the
unanswerable case more than once.

| Case | Expect |
|---|---|
| Question Knowledge answers | Search, answer, then the ask |
| In-scope question Knowledge cannot answer | Search, then no SEND or ASK from the playbook, and one reasoner reply |
| Question another playbook owns | Exit, then that playbook's first step. Not yet tested |

In author-playbook, use it instead of a scripted "can't find" line. In
revise-playbook, use it when the diagnosis is an apology after an empty
lookup. In test-and-fix, treat that failure as a known fix and run the three
cases.

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
