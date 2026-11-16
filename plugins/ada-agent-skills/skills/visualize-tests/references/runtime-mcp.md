# Ada MCP runtime

Discover the connected Ada server's tools and inspect their live input schemas before calling them. Tool prefixes, parameters, pagination and available detail vary by host and server version. Ada MCP tools were not available in the authoring session, so this reference does not claim their current schemas were verified.

## Retrieve existing evidence

Look for read-only capabilities that retrieve saved test cases, existing test runs and conversation evidence. Common capability names include `get_test_cases`, `get_test_runs` and `get_conversation`; use them only if discovery confirms their presence and supported inputs.

- Start with the person's selected run IDs or exports. If discovery is needed, use the supported case or changeset filters and follow the returned pagination cursor until complete before claiming a scope count.
- Read each selected run in detail, including transcript, original criteria, outcomes and evaluator rationale. Check whether a list returns only the latest run. Retrieve the requested historical IDs directly when supported.
- Read the full saved case where the result omits its scenario or criteria. If a response advertises truncation, use a supported detail read and retain any remaining limitation.
- Retrieve additional conversation evidence only using the conversation ID supplied by the run and the discovered schema. Request tool evidence only through a supported read capability. Missing records are unknown evidence.

Do not guess a tool's arguments or invoke a mutation tool to discover read behavior. Do not create runs, update cases, change behavior or promote as part of visualization. If a required read tool is absent or refuses access, name that observed limit. The person can open the selected test run in the Ada dashboard and supply its transcript, criteria and results as an export or attachment. Continue with that evidence where possible.

## Render with host tools

The Ada MCP supplies source evidence; HTML rendering depends on the host. Normalize retrieved evidence using [review-spec.md](review-spec.md). If the host has a shell and file access, resolve the installed skill folder and run from it:

```sh
python3 scripts/render.py review.json --output review.html
```

For returned feedback whose review and source identities match:

```sh
python3 scripts/render.py review.json --output review.html --feedback feedback.json
```

Write files with the host's file tool. Inspect the generated HTML in an available browser or artifact viewer, including comment export. Share the actual file or artifact link the host returns. A local HTML file is not a hosted site.

If no supported execution surface exists, state that the renderer could not run. Provide the normalized JSON and an evidence-linked transcript fallback, or create an HTML artifact only if the host can safely support it. Describe any observed script or storage restriction and provide a plain-text feedback route using the same case, run and turn IDs. Do not fabricate an HTML file, a rendered URL, shared comments or successful feedback export.

Returned feedback is review input only. Preserve original test outcomes, reconcile stale revision or source references, and propose the next change. It does not authorize a configuration write, test run or promotion.
