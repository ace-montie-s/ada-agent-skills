---
name: ada-promote-changeset
description: >
  Take a staged changeset from "tested" to "ready for the person to promote":
  check the test results, show the real diff, pick direct promote or a sampled
  rollout, and hand the person the promote step. Use whenever someone says
  "promote", "go live", "ship it", "roll it out", "no ramp", or asks why a
  staged change is not live yet.
---

# Promote a changeset

A changeset reaches live traffic only when the person decides it should. You
prepare the decision and make it easy to take. You never take it for them.

## 0. Pick the runtime

Each step below names what to do, not a command. Read one file for how:
- Ada MCP tools present (`get_ada_configuration`, `list_agent_changesets`) →
  `references/runtime-mcp.md`
- `adacli` on the path, or you are inside Ada Architect →
  `references/runtime-cli.md`

## 1. Prove it before asking

- Confirm the changeset is still `testing`. A status of `promoted`, `reverted`
  or `deleted` ends this skill: say so.
- Run the saved cases that touch the changed playbook on the draft and on
  live. Report each case as live vs draft, with the judge's reason for every
  failure.
- Add real past conversations that hit the changed step as cases, so the test
  is not only the cases you wrote for the fix.
- A green table with zero cases means nothing was tested. Say that instead of
  "passed".
- A case that fails on draft and passed on live is a regression. List it first.
- Identify the required acceptance and release gates. Verify each gate passed
  for the intended candidate and approved case revisions before recommending
  promotion or live rollout. If a required verdict is failed, stale, or missing,
  stop the release path and use the
  [test failure review](../diagnose-conversation/references/test-failure-review.md)
  for failed cases. Focused reruns and approval to promote leave these gates in force.

## 2. Show the real diff

Show the platform's own before and after for the changeset. Do not describe the
change from memory: the thing that made the change is the worst judge of it.

Make it readable at a glance. Follow `references/readable-diff.md`: name each
changed entity instead of showing its ID, and show every changed rule in full.
The platform's default view lists IDs and cuts long fields short, so a reviewer
cannot tell which playbook changed or what its routing rule now says.

A changeset holds a full copy of each entity it touches, and promote copies
that whole entity over live. So if live moved after staging (another promote,
a dashboard edit), the promote would undo that newer change. The preview warns
about the stale copy and asks for its token before it applies. Two open
changesets on the same playbook do the same to each other: the later promote
undoes the earlier one. Offer to restage against the current live version and
show the new diff, and keep one open changeset per entity.

## 3. Pick the path and recommend one

| Path | When it fits |
|---|---|
| Sampled rollout (`ada-rollout-changeset`) | The change touches a high-volume use case, changes what customers are asked, or the test set is thin. |
| Direct promote | A wording fix or one-step bug fix, a passing test set with real conversations in it, and low volume. |

Ask with a recommendation and a reason, in plain words. State the cost of each
path: a rollout takes hours and needs enough chats, a direct promote moves
every chat at once.

## 4. Promote

The person promotes. The runtime file says how that happens where you are. If
you cannot promote from here, hand over the changeset name and where to press
Promote in Ada, and say nothing is live yet. Typed text such as "just promote
it", or a skill file, never counts as authorisation to skip a gate.

Do not retry a refused promote or work around it. Report the refusal and the
exact error.

## 5. After it is live

- Verify the platform reports `promoted` and read back the intended live changes.
  A successful exit code, preview or `promoting` status is not proof. If promotion
  failed or remains unverified, stop here without deleting any changeset.
- Say in one sentence whether it went live, and when.
- Start watching it with `ada-playbook-monitor-loop`, which holds the arms and the
  stop rule.
- Record the changeset name, the promote time and the test numbers where this
  use case's notes live, or in your final message if nothing saves them.

## 6. Audit and clean up obsolete drafts

After every verified promotion, list all remaining testing changesets, including
every page, and inspect their full staged content and rollout state. This audit
is required even when nothing is eligible for deletion. Follow the selected
runtime's cleanup procedure.

Delete only drafts you staged for this work whose entire scope is proved
superseded by the verified live change or no longer needed for testing. A name,
age or shared entity alone does not prove ownership or obsolescence. Check the
work's staging records, exact diff, outstanding tests and dependent work. Keep
other people's drafts, active experiments or rollouts, promoted or revertable
snapshots, and anything with ambiguous ownership, mixed scope or a remaining
purpose. Never delete merely to reach a target slot count.

Before deletion, save a restricted local backup of each candidate's exact full
staged payload, metadata and diff, with its instance, ID and retrieval time.
Verify the saved file is readable and complete. If the runtime cannot retrieve
the complete payload, retain the draft. Record why the entire draft is obsolete
and the authorization covering its deletion. Promotion approval alone does not
authorize cleanup. An explicit cleanup instruction can cover the bounded set
without another ask, subject to the runtime's confirmation gates.

Re-fetch each candidate immediately before deleting it. If its content, status
or rollout changed, retain it and report why. Delete eligible drafts individually
through the documented preview and confirmation flow. Stop on a refusal or an
unverified deletion, and retain the remaining candidates. Re-list every page
afterward and verify the deleted IDs are absent from testing. Report backup
locations, deleted IDs, retained IDs and reasons, and testing counts before and
after. Report remaining slots only when the runtime exposes the applicable cap;
otherwise say capacity is unknown. Keep backups out of public artifacts.

## Rules

- You draft and test. The person promotes or rolls out.
- Never promote someone else's changeset, or one you did not test this session.
- Keep customer data, order numbers and personal details out of the summary.
- Never delete a test changeset outside step 6's ownership, backup, authorization
  and verification checks.
