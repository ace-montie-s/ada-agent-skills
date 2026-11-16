"""Generate offline Claude plugin eval cases from maintained scenario fixtures."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent
ENTRYPOINTS = ("test-and-fix", "author-playbook", "revise-playbook")


def build(output: Path, plugin: Path) -> int:
    fixtures = json.loads((ROOT / "cases.json").read_text())
    if not (plugin / "skills").is_dir():
        raise ValueError("--plugin must be a built plugin directory with skills/")
    if output.exists():
        raise ValueError("Output already exists. Choose a fresh directory to preserve results.")
    output.mkdir(parents=True)
    # Isolated fixture plugin: skills only, no hooks, servers, credentials or network tools.
    shutil.copytree(plugin / "skills", output / "skills", symlinks=False)
    metadata = output / ".claude-plugin"
    metadata.mkdir()
    (metadata / "plugin.json").write_text(json.dumps({
        "name": "shared-strategy-under-test", "version": "0.0.0"
    }, indent=2) + "\n")
    for fixture in fixtures:
        for entrypoint in ENTRYPOINTS:
            case = output / "evals" / f"strategy-{fixture['id']}-{entrypoint}"
            graders = case / "graders"
            graders.mkdir(parents=True)
            prompt = f'''---
tags: ["behaviour", "shared-implementation-strategy", "{entrypoint}"]
runs: 1
max_turns: 10
timeout_seconds: 240
allowed_tools: ["Read", "Glob", "Grep", "Skill"]
plugins: ["../.."]
---

Use the {entrypoint} skill for this offline implementation review. Work from
the supplied fictional evidence. Do not connect to an instance, run commands,
modify files, or claim live changes. This is a review exercise, so stop after
giving a concrete implementation decision and focused validation plan.

{fixture['scenario']}

Explain what should change, where it belongs, which existing steps should stay,
and how you would check the resulting behavior. Identify any unavailable evidence
or capability that prevents a stronger conclusion.
'''
            (case / "prompt.md").write_text(prompt)
            criteria = [
                "The reply provides an actionable design for the supplied facts, not only a plan to inspect later. Judge semantics and resulting behavior, not headings, keywords or exact phrasing.",
                *fixture["criteria"],
                "It does not claim execution, tool schemas, test results or live changes that the exercise did not supply. It does not raise all steps to High or add ASK/code/branches everywhere as a generic recipe."
            ]
            rubric = "---\ntype: llm\ncriteria: Chooses the smallest sufficient implementation from the evidence\n---\nPass only if ALL hold:\n"
            rubric += "\n".join(f"{i}. {text}" for i, text in enumerate(criteria, 1)) + "\n"
            (graders / "implementation-outcome.md").write_text(rubric)
    return len(fixtures) * len(ENTRYPOINTS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    count = build(args.output.resolve(), args.plugin.resolve())
    print(f"Generated {count} offline cases in {args.output}")


if __name__ == "__main__":
    main()
