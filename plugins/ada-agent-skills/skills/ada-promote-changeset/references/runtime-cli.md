# ada-promote-changeset on the command line

For anyone with `adacli` logged in to the instance, and for Ada Architect. The
instance comes first in every command, and there is no `--instance` flag.

| Step | Command |
|---|---|
| Status | `adacli <instance> changesets get <id> --json` |
| Find a changeset | `adacli <instance> changesets list --json` |
| Cases that touch the playbook | `adacli <instance> testing cases list --json`, keep those whose scenario reaches the changed playbook |
| Cases from real chats | `adacli <instance> testing cases from-conversation <conversation id> --json` prints a screened draft and saves nothing. Follow its `instructions`, and `author-playbook/references/test-cases.md` section 8. Needs adacli 1.1.7 or later |
| Run on draft and on live | `adacli <instance> testing runs create --cases <ids> --changeset <id>`, then again without `--changeset`. Read each with `testing runs get <run id> --json`: `did_pass`, `criteria_results[].rationale` |
| The real diff | `adacli <instance> changesets get <id> --diff --json` for the full before and after of each field. The table view (`--diff` alone) shows IDs and can cut long fields short. See `readable-diff.md` |
| Name an entity from its ID | `adacli <instance> playbooks get <id> --json` for a playbook. Other types: the same `get` on their command group (`knowledge`, `coaching`, `handoffs`, `glossary`, `variables`) |
| Direct promote | `adacli <instance> changesets promote <id>` returns a preview. Applying it needs `--yes` and the `--token` from that preview, which only the person's go-ahead permits. Add `--json` and check that `status` is `promoted`. If live changed after the preview, the call returns `confirmation_required` with exit 0 and applies nothing |
| Preview deletion of an eligible obsolete draft | `adacli <instance> changesets delete <id> --json` |

## Post-promotion cleanup

First inspect the installed CLI's changeset help and the `list`, `get` and
`delete` subcommand help. Confirm available pagination, full-detail output,
rollout fields and deletion confirmation flags rather than assuming this
reference matches the installed version. Do not guess an export command or a
changeset cap.

Use `changesets list --json`, following the returned pagination through all
testing drafts. Retrieve each candidate with `changesets get <id> --json` and
`changesets get <id> --diff --json`. Save the exact outputs to restricted local
files before deletion. Check that these responses contain the complete staged
entity snapshots, not just truncated field summaries. If not, retain the draft
and report the missing backup capability. Apply step 6's eligibility checks.

For each eligible candidate, re-fetch and compare the saved payload and state,
then preview with `changesets delete <id> --json`. Show the IDs, reasons and
backup paths covered by the cleanup authorization. Only when that authorization
and the preview permit it, confirm with `changesets delete <id> --yes --json`,
using any additional token required by the installed CLI. Check the JSON result,
not just the exit code. A new warning or changed preview requires review, not a
blind retry. Re-list all testing drafts and record the result required by step 6.

## Promote needs the person

Run the preview and show it. Apply only after the person says yes in chat, then
use the token from that same preview. If a second call asks for confirmation
again, live config moved between the two calls: stop and show the new diff.

## If the instance is read-only

Run `adacli <instance> status --json` once at the start. If `read_only` is
`true`, say so before you plan any change: this skill's writes will be
refused. Offer a writable instance, or the steps that only read. A write that
exits with code 7 means the same. Stop, name the change, and leave
`~/.adacli/config` alone. `setup-adacli` has the full rule.

## Inside Ada Architect

Architect has helpers: `ada-test <instance> --cases <ids> --changeset <id>` for
the run table, and `ada-changeset <instance> <id> --emit` for the diff panel.
Promote there only when the gateway sends a message that starts
`PROMOTE-AUTHORISED <token>`, and run exactly the command it gives, once. Relay
a blocked message as written. Without that message, do not promote.
