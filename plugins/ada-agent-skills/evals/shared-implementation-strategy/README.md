# Shared implementation strategy eval

Customer-free behavioral fixtures exercise the same six decisions through
`test-and-fix`, `author-playbook` and `revise-playbook`, producing 18 cases.
Edit `cases.json` and `build_cases.py`, not generated case directories.
The prompt contains evidence and desired behavior, while the separate grader
holds the acceptance criteria. It does not disclose the intended implementation.

Coverage includes duration state and repeated checks, selective Normal versus
High extraction based on matched evidence, exact date arithmetic and branching,
knowledge-only correction, unavailable tools, and reuse of already known facts.
Each semantic grader requires all criteria. Blanket High and unnecessary steps
fail, even when the reply repeats the shared strategy's wording.

Generate from a built plugin, then use the existing Claude plugin eval harness:

```sh
python3 evals/shared-implementation-strategy/build_cases.py \
  --plugin . \
  --output /tmp/shared-strategy-eval
claude plugin eval /tmp/shared-strategy-eval \
  --runs 1 --ablation none --no-publish --trust-plugin \
  --tag shared-implementation-strategy --judge-model sonnet \
  --max-cost-usd 10 \
  --json /tmp/shared-strategy-results.json \
  --report /tmp/shared-strategy-results.html
```

Run from the built plugin repository. The generator copies only its `skills/`
tree into an isolated fixture plugin, omitting hooks, MCP servers and credentials.
Only Read, Glob, Grep and Skill are allowed. No invented tool schema or live
instance is required. Use a fresh output directory for each generation.

Review all 18 case verdicts and responses. A clean result requires every case
to pass across all three entrypoints. Compare decisions across entrypoints:
they should choose the same implementation boundary for the same evidence.
For ablation, rerun with `--disallow-tools Skill` and separate result paths.
Repeat runs before treating an apparent improvement as stable.

These are offline design decisions, not proof of live tool execution, saved-test
outcomes, staging or promotion. A semantic judge can be wrong, so inspect failures
and disagreements. Generating cases validates the fixture layout only. A paid
model run is required to establish behavioral results.
