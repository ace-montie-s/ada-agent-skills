# Refute pass

A fix judged by the session that wrote it reads its own evidence as success. The refute pass is a second reviewer whose only job is to break the fix. It runs after a round passes and before the hand-over.

## Contents

1. Run it
2. What the reviewer gets
3. Attack checks
4. Design checks
5. Report

## 1. Run it

- **Subagents available** (Claude Code, Codex): dispatch a fresh subagent with no history from this session. Give it this file and the inputs in section 2. In a workspace that defines a `playbook-adversary` agent, use that agent.
- **No subagents** (a chat assistant): start a separate pass in the same chat. Write "Refute pass" as a heading, reread only the inputs in section 2, and work through sections 3 and 4 as if someone else wrote the fix. Say in the hand-over that the pass ran in the same session, so it is weaker evidence.

The reviewer reads and runs tests only. It never stages, promotes or edits.

## 2. What the reviewer gets

Pass raw material, never your summary of it. A summary carries your conclusion.

- The changeset's platform diff, before and after.
- The live config of every playbook the change touches, and of every playbook that runs it or routes into it.
- The test runs from the passing round: case, result, conversation link, and the reasoning log of each changed step.
- The anchor: saved cases, sheet rows or the approved design board.
- The original failing conversation, when the loop started from one.

## 3. Attack checks

Hunt for each in the changed config. Name the exact turn, branch or string that breaks. "Could be risky" is not a finding.

1. **Permission beats prohibition.** A "never X" rule with an earlier permission for X in the same block gets averaged, and X still happens.
2. **Scoped rules vanish.** "Only do X when Y" can stop X entirely. A scoped behavior must be written as required when Y holds, not merely allowed.
3. **Overlapping items dilute each other.** Two coaching items or custom instructions on the same intent average out. The older one needs to go before the tighter rule can bite.
4. **Coaching leaks across topics.** Coaching is retrieved per turn for the whole agent, not per playbook. A rule meant for one playbook belongs in that playbook or in scoped instructions.
5. **The bad string came from config.** If the agent says something wrong, search the config for an example, SET or instruction that holds it before adding a rule against it.
6. **Double acknowledgement.** The agent already acknowledges the customer. An ASK, SET or SEND text that opens with a preamble ("I can check that for you. What is...") says it twice.
7. **Tool names must be literal.** An instruction that gates a tool must name the tool as configured, in backticks. A paraphrase does not bind.
8. **Knowledge search intercepts mid-playbook.** A topical customer turn inside a playbook can be answered from knowledge, so the step edit never runs. Check whether the changed step can be skipped this way.
9. **Branch coverage.** Walk every branch. Name one input that lands on an uncovered path, a wrong step, a silent exit, or a child playbook that does not hand back.
10. **The test never reached the change.** A run that never entered the changed step proves nothing. Confirm from each run that the changed step executed and that the case's variables match the playbook's trigger rules.
11. **The original failure still reproduces.** Rerun or replay the original failing conversation on the changeset. A fix that passes the cases but not the original complaint is not done.
12. **Collateral damage.** Name any nearby use case that shares a step, variable, instruction or knowledge article with the change, and say whether a control covers it.

If the workspace keeps an index of known platform bugs, scan the categories the change touches. A pass that misses a known trap is a false clear.

## 4. Design checks

These are not runtime breaks. They become breaks later.

13. **Duplicated logic.** Near-identical wording or conditions across branches or sibling playbooks drift apart when the next fix lands in one copy. Name the shared surface each should collapse into: a child playbook, one shared instruction, or one computed variable when the branches differ only by a value.
14. **Unverified branches.** A branch for a scenario no real conversation or test has hit is speculative coverage. Mark it "unverified" and ask for the evidence. Do not recommend deleting a clause that only looks redundant. An exclusion clause removed on instinct once dropped a sibling scenario from 68% to 29%. The fix is to test it alone first.

## 5. Report

```
## Refute pass: <changeset name>

Verdict: <BROKEN - N attacks land | HOLDS>

| # | Check | Failing input | What the agent does | Fix surface |
|---|-------|---------------|---------------------|-------------|

Highest risk: <the attack most likely to fire on live traffic>
Pre-existing: <issues the change did not introduce, kept separate>
Before trusting the next run: <what to confirm>
```

Look for at least one real attack. When the fix holds, say so and give one line per check on why it does not apply. Tag any issue the change did not introduce as pre-existing. It is reported but does not fail the round.
