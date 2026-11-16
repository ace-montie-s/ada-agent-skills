# Command line runtime

Use read-only commands to retrieve existing evidence. Check the installed command help before use; flags and output can vary by version. The command shapes below were checked against installed help on 16/11/2026. Replace angle-bracket placeholders with the selected instance and source IDs.

```sh
adacli <instance> testing runs list --help
adacli <instance> testing runs get --help
adacli <instance> testing cases get --help
adacli <instance> conversations log --help
```

## Retrieve existing evidence

```sh
adacli <instance> testing runs list --changesets baseline --page 1 --limit 25 --json
adacli <instance> testing runs list --changesets <changeset-id> --page 1 --limit 25 --json
adacli <instance> testing runs get <run-id> --json --calls
adacli <instance> testing cases get <case-id> --json
adacli <instance> conversations log <conversation-id> --json
```

Skip discovery when the person supplied the run IDs. Otherwise page the selected scope to completion before claiming a count. The list returns the latest run per case and changeset, so it does not establish all historical runs. Retrieve each selected run by ID, including older IDs provided by the person. Use the conversation ID returned by the source when additional conversation evidence is needed; do not substitute a run ID.

Inspect the actual JSON before normalizing it. Retain per-criterion results, rationale, simulated calls and transcript where present. Do not assume field names from another CLI version. Call evidence may expire; missing records are a limitation, not proof that no call occurred. Report incomplete reads and authentication or access errors honestly. Do not create a test run, change a case or log in to another instance as part of this review.

## Render

Prepare a normalized JSON file following [review-spec.md](review-spec.md). Resolve the installed skill folder first, then run its renderer from that folder:

```sh
python3 scripts/render.py review.json --output review.html
```

To include returned comments, validate their source identities against the review, then run:

```sh
python3 scripts/render.py review.json --output review.html --feedback feedback.json
```

Use the host's file writing tool to create input files. Preserve raw exports separately. The renderer uses Python's standard library and creates a standalone HTML file. Open that file in the available browser or artifact viewer and inspect the result before sharing it. Hosting is optional and needs a real supported publishing route; local rendering alone does not produce a public URL.

If Python, the renderer or file access is unavailable, state that no HTML was rendered. Provide the normalized JSON and a concise transcript review using the same case and turn IDs, or use an available artifact tool that can run the bundled HTML safely. Do not claim comment export works in an untested artifact host.

## Inside Ada Architect

Use the same read-only commands and renderer when shell and file access are available. No Architect helper or deployment permission is required. If the host exposes only an artifact viewer, use the fallback above and describe its observed limits. This skill does not use a promotion gate or modify agent configuration.
