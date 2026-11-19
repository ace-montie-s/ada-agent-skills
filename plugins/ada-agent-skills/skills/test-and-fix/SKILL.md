---
name: test-and-fix
description: >
  Run a test, fix, retest loop on an Ada AI agent use case, anchored on what
  good looks like: the saved test cases, a customer's requirements sheet or
  doc, or the approved design board. Runs
  every case, sends each failure to diagnose-conversation, stages fixes on a
  changeset, reruns the whole set, and stops at all-pass, after three rounds,
  when a case fails the same way twice, or when a fix changes the design.
  Use it for "test and fix this", "run the
  tests and sort out the failures", "keep fixing until it passes", "this
  playbook is built, get it working", or when someone with an existing
  playbook shares one bad conversation. Do not use it to find out why one
  conversation went wrong with no fix wanted (diagnose-conversation), to design
  a new use case (design-conversation), or to promote (ada-promote-changeset).
---

# Test, fix, retest against the design

Fixing against the last complaint drifts: each patch cures one chat and breaks
another. Anchor on what good looks like, run all of it every round, and let the
results, not the latest comment, say what to fix next.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_test_cases`, `get_test_runs`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

## 1. Find the anchor

The anchor is the set of cases that define "good". Look in this order and stop
at the first hit:
1. **Saved test cases** for the use case, named "<Use case>: <scenario>". They
   are the regression set, so they win.
2. **A requirements sheet or doc.** Many customers keep "what good looks
   like" as a Google Sheet or doc with one row per scenario: what the customer
   says and the expected outcome. Read it directly and do not retype it. Follow
   `references/anchor-from-sheet.md` for the read, the column mapping and the
   rows that go back to the person as questions. The person approves the
   mapping on the first rows, then each save.
3. **The design board**, the last round the person approved. The runtime file
   says where it lives. Turn each scenario into a case: the first customer
   turn is the opening message, `expect` becomes the success criteria, and
   each "must not" in the design becomes its own criterion. Follow
   author-playbook's test-case rules. The person approves each save.
4. **None of these.** Ask the person for three sample conversations of what good
   looks like, with a customer, a request and the outcome they want. Offer
   design-conversation as the better route and stop there if they take it.

Never invent expected behavior. Every success criterion comes from a saved
case, a sheet row, the board, or words the person wrote. A criterion you made up makes the
loop fix the agent toward your guess.

**One bad conversation, existing playbook.** Start here too. Draft that
conversation as a case before any fix, with the draft tool the runtime file
names, and follow `author-playbook/references/test-cases.md` section 8:
- Success criteria: the outcome the person states, in their words. If they
  have not stated one, ask "what should the customer have got?" Do not copy a
  generic default such as "resolves the inquiry", and do not copy what the
  agent did.
- Every field comes from the screened draft. Facts the customer gave later go in
  the scenario goal, so the simulated customer can give them.
- The case is a target. It must fail on live in step 3, or it is the wrong
  case.

Then treat it as a one-case anchor.

**Controls.** Every anchor path needs at least one control: a case from a
nearby use case that must not change, so a fix cannot quietly break its
neighbours. Ask the person for candidates or look for saved cases nearby. Run
each proposed control with the baseline in step 3. Add those that pass today.
Keep existing protected controls in the gate, including any that fail on the
baseline, and review their failures. If no control passes, report that in the
hand-over counts.

## 2. Check each case is safe and sound

Read `references/safe-to-run.md` before the first run. A test run is a
simulation, but some things in it still reach real systems.
- Read `../author-playbook/references/playbook-graph.md`. Map the persisted
  flow behind the anchor, including ASK retries, fallback consumers and child
  returns. Save the graph, node/edge tables and weak-node review. Use them to
  inspect reachable side effects and coverage gaps; graph risks do not
  authorize extra runs or override the all-pass stop.
- Walk each case's expected path. Name every tool it calls and every handoff
  it can reach.
- Do not run a case that would open a real handoff to a live queue, or call a
  live tool that writes (refund, cancel, send). Tell the person which case
  you held back and why. The file holds the exact rule, including the handoff
  platforms where this is not settled.
- A hold stops a run, not the diagnosis. If an earlier run already recorded a
  failure, diagnose it now (step 4.1), so the person sees the cause while they
  clear the hold. Stage no fix until that case has run today.
- A case needs the opening message, a goal for the simulated customer, and
  criteria the judge can find in the transcript. Reword nothing to make it
  pass. A wrong case is the person's call.
- Write the goal so the simulated customer does not ask for a person unless the
  case is about that. A customer who asks can reach a handoff in a later turn,
  which the walk above did not predict.

## 3. Run the baseline on live

Run every safe case on live before any change. State the number of runs and
the quota left, and run only when the person says yes.
- Keep each case's intended role. Review failed baseline runs before using them
  as evidence of an agent defect.
- If every baseline case passes and there is no known candidate failure,
  report that the baseline did not reproduce the issue and stop. If a candidate
  already failed, review its evidence against the baseline before a fix.
- More than half the cases the person called broken pass on live: the cases or
  the complaint are off. Stop and ask the person.

Judge verdicts vary on borderline conversations. A run that fails with a reason
that contradicts its own transcript gets one rerun before you act on it.

## 4. The loop (three rounds at most)

Each round:

1. **Diagnose.** Start every failure with the
   [test failure review](../diagnose-conversation/references/test-failure-review.md).
   Diagnose supported agent behavior with diagnose-conversation and record the
   owning surface, mechanism, and evidence. Draft test repairs for review. Keep
   an OPEN case visible and stop edits aimed at it until the evidence identifies
   what to fix. Group failures that share a cause, so one fix serves several cases.
   Mark the failing path on the graph with trace evidence. A suspected weak
   node is a diagnosis lead, not proof of a runtime failure or platform bug.
2. **Choose the implementation.** Read
   `../author-playbook/references/implementation-strategy.md`. Assess knowledge,
   SET state, missing-input ASK, branching, code tools and reasoning level. Log
   selected and rejected options with evidence and acceptance checks.

   **Fix on a changeset.** Never edit live. Keep all fixes of the loop on one
   changeset so they test and promote together.
   - Playbook steps, flow, exit or trigger: hand to revise-playbook and take
     back its staged changeset. It owns the redesign method.
   - Knowledge, coaching or custom instructions: stage a direct edit on the
     same changeset. Before you stage a knowledge article, search knowledge
     for two or three of its keywords. List any existing article that states a
     different fact and tell the person. Do not disable or delete it, because
     the person owns that call. After the rerun, say whether the new article
     was used.
   - Glossary, variables, topics or other settings: these go live at once and
     cannot be tested on a changeset. Say so and get the person's yes first.
   - Action or platform fault: report what the action returned and stop that
     item. A config change cannot fix a broken endpoint.
   Confirm staging succeeded and read back the changed entities before spending
   runs. A rejected stage must not be followed by testing unchanged configuration.
   Refresh the graph from that readback. After the authorized rerun, annotate
   exercised edges and report unresolved risks, untested edges and held paths.
3. **Show the diff and wait.** Show the platform's own before and after. The
   person approves each staged fix.
4. **Rerun the whole anchor on the changeset**: every case that failed and
   every case that passed before. A partial rerun hides regressions. Say the
   run count and quota, and run only on a yes.
5. **Read the results.** Sort each failure into one kind:
   - Observed regression: passed on live, fails now. Investigate first; trace
     evidence and a matched rerun establish whether the change caused it.
   - Same on live: fails on both. An anchored target remains a fix target.
     An unrelated pre-existing failure is recorded separately and does not expand scope.
   - Case wrong: the simulator, fixture, grader, or criterion undermines the
     run. Follow the test failure review for evidence, comparison, and approval.
   - Works in part: some turns, branches or criteria now pass. Say which part is
     missing and fix that part.
   - Not reached: the run never got to the changed step. Check routing and exits.

   Investigate a newly failing control first. Withdraw or rework an agent
   change when the comparison supports it as the cause.

   Compare each failure with the round before. A case that failed again after
   a fix aimed at it, with the same owning surface and the same missing
   behavior or judge reason, is **same twice**. It gets no third fix on that
   diagnosis: see "Same failure twice" in step 5.

   When a substantive answer fails a literal-word check, compare the criterion
   with the approved outcome before choosing a fix.

   Scan every finished transcript, baseline included, for a handoff or
   handoff-triage playbook that the simulated customer reached in a later turn.
   Note it in the round log and hold that case until the person confirms.
6. **Log the round** with the table in `references/round-log.md`: case,
   result, owning surface, fix, changeset. Post it in chat.
7. **Refute a passing round.** When every anchored case passes, run the refute
   pass in `references/refute-pass.md` before you stop. Hand over the raw diff,
   runs and reasoning logs, never your summary. A BROKEN verdict counts as a
   failed round: its attacks become the next round's targets. Do not argue a
   refutation down. A pre-existing issue goes in the hand-over and does not
   fail the round.

## 5. Stop

Stop at the first of these and say which:
- **All pass.** Every anchored case passes on the changeset and the refute
  pass returns HOLDS. Go to step 6.
- **Three rounds used.** Report what still fails, the cause for each, and what
  you would try next. Do not start a fourth round. Three rounds without a pass
  means the diagnosis or the design is wrong, and more patches will not help.
- **Same failure twice.** This stops that case, not the loop. The two fixes
  shared a premise and the evidence says it is wrong. Before any further fix
  on the case:
  1. Write the premise both fixes assumed in one sentence.
  2. Run one check that would come out differently if the premise were false:
     the reasoning log of the failing turn, the case on live without the
     changeset, or which surface produced the reply.
  3. Log the premise, the check and the result in the round log.
  4. If the check contradicts the premise, send the case back to
     diagnose-conversation with that evidence. If it confirms it, the fix
     itself is wrong: return the case to the person.

  Other cases continue under the three-round cap. If the
  principle-attack-the-premise skill is installed, follow it for this step.
- **A fix changes the design.** If the fix changes what the customer is asked,
  in what order, or what they get, or the use case's goal moved, stop. Return
  to design-conversation, so the person approves the new conversation. Internal
  SET, branching and tool changes that preserve the approved experience do not
  require a new design. Reuse authorization for behavior already approved. Then
  update the saved cases to the new board before the loop resumes.
- **A decision is the person's.** A wrong case, a goal conflict, a live-write
  fix or a held-back case waits for them.

## 6. Hand over a passing changeset

Never promote, even when the person asked you to. Every plan or status you
write ends at this hand-over, never at "then I'll promote", so the person
knows the last step is theirs. Give the person the changeset name, the final
round table, the counts by kind ("targets fixed 4 of 4, controls worse 0 of
6") and the refute verdict with any pre-existing issues it found. Hand the changeset to ada-promote-changeset, which checks it again, shows
the diff and offers a direct promote or a rollout.

If the loop stopped without a pass, leave the changeset in `testing`, say it
is not ready, and let the person choose: another round with a new idea, a
return to design, or delete the changeset.

## Rules

- You draft and test. The person approves every run, every staged fix and
  every promote.
- The person may approve a run budget once ("up to N runs this loop"). Runs
  inside it need no new yes. State the running total used and left at each
  round, and ask again before you pass the budget.
- Anchor first, fix second. No fix starts from a case you did not run.
- Keep customer data out of cases and tables. Use fakes of the same shape.
- Delete changesets you staged only for a test run, after asking.
