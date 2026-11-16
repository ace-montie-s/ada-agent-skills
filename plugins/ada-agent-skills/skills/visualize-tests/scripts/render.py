#!/usr/bin/env python3
"""Build a portable test review. Read references/review-spec.md for the input contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}$")
STATUSES = {"pass", "fail", "unknown"}
KINDS = {"failure", "concern", "limitation"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def identifier(value, label):
    require(isinstance(value, str) and bool(ID.fullmatch(value)), f"{label}: use a stable, nonempty identifier")


def validate(spec):
    require(isinstance(spec, dict), "review must be an object")
    require(spec.get("schema_version") == 1, "schema_version must be 1")
    for key in ("review_id", "revision"):
        identifier(spec.get(key), key)
    for key in ("title", "summary"):
        require(isinstance(spec.get(key), str) and bool(spec[key].strip()), f"{key} is required")
    require(isinstance(spec.get("cases"), list) and spec["cases"], "cases must be a nonempty list")
    case_ids = set()
    for case in spec["cases"]:
        identifier(case.get("id"), "case id")
        require(case["id"] not in case_ids, "duplicate case id")
        case_ids.add(case["id"])
        require(case.get("status") in STATUSES, "case status must be pass, fail or unknown")
        require(isinstance(case.get("title"), str) and case["title"].strip(), "case title is required")
        require(isinstance(case.get("run_id"), str) and bool(case["run_id"]), "run_id is required (use an explicit unknown label when unavailable)")
        require(isinstance(case.get("turns"), list), "turns must be a list")
        turns = set()
        for turn in case["turns"]:
            identifier(turn.get("id"), "turn id")
            require(turn["id"] not in turns, "duplicate turn id within case")
            turns.add(turn["id"])
            require(turn.get("role") in {"user", "agent", "system", "human", "tool"}, "unknown turn role")
            require(isinstance(turn.get("text"), str) and bool(turn["text"].strip()), "turn text is required")
            require(isinstance(turn.get("language"), str) and bool(turn["language"]), "turn language is required")
            if not turn["language"].lower().startswith("en"):
                require(isinstance(turn.get("translation"), str) and bool(turn["translation"].strip()), "non-English turn needs an English translation")
        criteria_ids = set()
        for criterion in case.get("criteria", []):
            identifier(criterion.get("id"), "criterion id")
            require(criterion["id"] not in criteria_ids, "duplicate criterion id")
            criteria_ids.add(criterion["id"])
            require(criterion.get("status") in STATUSES, "invalid criterion status")
            require(isinstance(criterion.get("text"), str) and bool(criterion["text"]), "criterion text is required")
            require(isinstance(criterion.get("reason"), str) and bool(criterion["reason"]), "criterion reason is required, or label it unavailable")
        finding_ids = set()
        for finding in case.get("findings", []):
            identifier(finding.get("id"), "finding id")
            require(finding["id"] not in finding_ids, "duplicate finding id")
            finding_ids.add(finding["id"])
            require(finding.get("kind") in KINDS, "invalid finding kind")
            require(finding.get("turn_id") in turns, "finding points to a missing turn")
            for key in ("title", "observed", "expected"):
                require(isinstance(finding.get(key), str) and bool(finding[key].strip()), f"finding {key} is required")
            if finding.get("criterion_id"):
                require(finding["criterion_id"] in criteria_ids, "finding points to a missing criterion")
            if finding["kind"] == "failure":
                basis = finding.get("basis", "evaluator")
                require(basis in {"evaluator", "reviewer"}, "invalid failure basis")
                if basis == "reviewer":
                    require(isinstance(finding.get("rule"), str) and bool(finding["rule"].strip()), "reviewer failure needs the acceptance rule it violates")
                else:
                    require(finding.get("criterion_id") in criteria_ids, "evaluator failure needs a criterion_id")
                    criterion = next(c for c in case["criteria"] if c["id"] == finding["criterion_id"])
                    require(criterion["status"] == "fail", "evaluator failure must reference a failed criterion")
            if finding.get("quote"):
                turn = next(t for t in case["turns"] if t["id"] == finding["turn_id"])
                require(finding["quote"] in turn["text"], "finding quote must match its original turn exactly")
    return spec


def fingerprint(spec):
    return hashlib.sha256(json.dumps(spec, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def validate_feedback(feedback, spec):
    require(isinstance(feedback, dict), "feedback must be an object")
    for key, expected in (("schema_version", 1), ("review_id", spec["review_id"]),
                          ("revision", spec["revision"]), ("fingerprint", fingerprint(spec))):
        require(feedback.get(key) == expected, f"feedback {key} does not match this review")
    cases = {c["id"]: c for c in spec["cases"]}
    require(isinstance(feedback.get("comments"), list), "feedback comments must be a list")
    targets = set()
    for comment in feedback["comments"]:
        case = cases.get(comment.get("case_id"))
        require(case is not None, "feedback refers to a missing case")
        require(comment.get("run_id") == case["run_id"], "feedback run_id mismatch")
        turn = next((t for t in case["turns"] if t["id"] == comment.get("turn_id")), None)
        require(not comment.get("turn_id") or turn is not None, "feedback refers to a missing turn")
        require(comment.get("quote", "") == (turn["text"] if turn else ""), "feedback quote mismatch")
        require(isinstance(comment.get("comment"), str), "feedback comment must be text")
        require(comment.get("decision", "") in {"", "agree", "disagree", "change", "question"}, "invalid feedback decision")
        target = (case["id"], comment.get("turn_id") or "")
        require(target not in targets, "duplicate feedback target")
        targets.add(target)
    return feedback


def render(spec, feedback=None):
    validate(spec)
    if feedback is not None:
        validate_feedback(feedback, spec)
    payload = {"review": spec, "fingerprint": fingerprint(spec), "feedback": feedback}
    # HTML parser raw-text terminators and JS line separators must never reach the document.
    encoded = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    template = (Path(__file__).resolve().parents[1] / "assets" / "review.html").read_text(encoding="utf-8")
    return template.replace("__REVIEW_DATA__", encoded)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("spec", type=Path)
    p.add_argument("--output", "-o", required=True, type=Path)
    p.add_argument("--feedback", type=Path)
    args = p.parse_args()
    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        feedback = json.loads(args.feedback.read_text(encoding="utf-8")) if args.feedback else None
        document = render(spec, feedback)
        require(args.output.resolve() not in {args.spec.resolve(), args.feedback.resolve() if args.feedback else None}, "output must not overwrite an input")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(document, encoding="utf-8")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        p.exit(2, f"Invalid review: {exc}\n")
    print(args.output)


if __name__ == "__main__":
    main()
