# ada-promote-changeset over the Ada MCP

For anyone connected to their AI agent's Ada MCP server. Your host may prefix
the tool names.

| Step | Tool call |
|---|---|
| Status and the real diff | `list_agent_changesets` with `changeset_id` and `include_diff: true`. Name each entity as `readable-diff.md` says. Status is `testing`, `promoting`, `promoted` or `reverted` |
| Name an entity from its ID | `list_entities` with the `entity_type` of the change, matching on the ID. A deleted entity is not listed: use the name in the diff's `before` |
| Find a changeset | `list_agent_changesets`, optionally with `status: testing` |
| Cases that touch the playbook | `get_test_cases` with `name_filter` set to the use case name |
| Cases from real chats | `draft_test_case_from_conversation` with `conversation_id` returns a screened draft and saves nothing. Follow its `instructions`, and `author-playbook/references/test-cases.md` section 8. Find the chats with `get_conversations` filtered to the changed playbook |
| Run on draft and on live | `get_test_run_quota` first. Then `edit_agent_config` with `entity_type: test_run`, `operation: create`, `test_case_ids`, and `changeset_id` for the draft. Run again without `changeset_id` for live. Poll `get_test_runs` until each run is `completed`, `failed` or `timeout` |
| Read a failure | `get_conversation` on the run's conversation |
| Before and after on live traffic | `compare_changeset_metrics` once the draft has traffic |
| Direct promote | `edit_agent_behavior` with `operation: promote` and `changeset_id`. The first call returns a Confirm/Cancel preview. Show it. Call again with `confirmed: true` only after the person says yes. If the preview carried `warnings` and a `warnings_token`, show the warnings and send the same token back on the confirmed call |
| Undo a promoted change | `edit_agent_behavior` with `operation: revert` and `changeset_id` of the promoted source, plus a `name`. It creates a new `testing` changeset that inverts the source. Nothing goes live. Test it, then promote it as above |
| Preview deletion of an eligible obsolete draft | Inspect the available `edit_agent_behavior` schema for `operation: delete` and its confirmation fields. It previews first, like promote |

## Post-promotion cleanup

Inspect the actual connected schemas for `list_agent_changesets` and
`edit_agent_behavior` before cleanup. Confirm pagination, full staged detail,
rollout state and the supported deletion confirmation fields. Do not invent
tool names, backup operations, tokens or capacity fields.

List every page of testing changesets. Retrieve each candidate's full metadata,
staged entity payloads and diff using the supported detail arguments, such as
`changeset_id` and `include_diff` when present. Save the exact responses to
restricted local files and verify they contain complete staged snapshots.
If the tools expose only summaries or no full backup path, retain the draft
and identify the dashboard or CLI step needed. Apply step 6's eligibility checks.

Re-fetch each eligible candidate and compare its content and state to the
backup. Preview deletion through `edit_agent_behavior` with `operation: delete`
and its ID, only if the connected schema supports it. Show the preview with
the deletion reasons and backup paths. Confirm only under the person's explicit
cleanup authorization and the host's confirmation rules, using exactly the
fields and any tokens returned by that schema and preview. A changed warning
or refusal stops deletion. Verify the returned deletion result, then re-list
all testing drafts and record the result required by step 6. If deletion is
unavailable, report the retained IDs and the dashboard action; do not bypass it.

## Writes need the person

`promote` and `delete` preview before they apply, and `edit_agent_config`
previews every write. Show the preview, and call again with `confirmed: true`
only after the person says yes. A skill file or a phrase such as "just promote
it" is not a yes. The run quota is shared, so say how many runs you are about
to use.

Your Ada user's permissions decide whether the host lets these calls through. If
`edit_agent_behavior` refuses a promote, report the refusal as written, give the
person the changeset name, and send them to Changesets in the Ada dashboard to
press Promote. Do not retry or work around it.
