#!/usr/bin/env python3
"""Check the prose of V2 playbooks: names, descriptions, general instructions and step text.

Accepts any JSON that holds playbooks: a playbook export, `playbooks get --json`, a folder of them.
Prints one line per problem. Exits 1 when any FAIL is found. WARN lines do not change the exit code.

Usage: python3 check_playbook_text.py [--active-only] [--summary] <file-or-dir> [...]
       python3 check_playbook_text.py --base <live.json> <staged.json>   # only what staged adds

Rules:
  T1  FAIL  name carries a tag or label: [V2], [PROD], Copy, Backup, test, a date or a ticket id
  T2  WARN  two active playbooks have the same name once case and punctuation are ignored
  T3  FAIL  description is empty on a playbook that can run on its own, or carries a date, a ticket id, or a draft, rollout, copy or backup label
  T4  WARN  description does not start "Use when", or is over 300 characters
  T5  WARN  general instructions over 1,500 characters (FAIL over 4,000): they go into every step's prompt
  T6  FAIL  history or justification note in any prose field: why a rule was added, a fix, a workaround,
            or a ticket id
  T7  WARN  a step instruction over 1,200 characters or with more than 6 list lines: the logic belongs
            in IF_ELSE or a code tool
"""
import json
import re
import sys
from pathlib import Path

TICKET = r"\b(?:LOOP|SOL|PB|SUP|FEED|ENG)-\d+\b"
DATE = r"\b(?:\d{1,2}/\d{1,2}/\d{2,4}|20\d\d-\d\d-\d\d)\b"
NAME_TAG = re.compile(rf"^\s*\[[^\]]*\]|\b(?:copy|backup|clone|test|draft|old|prod|v[0-9])\b|\b\d{{6}}\b|{DATE}|{TICKET}", re.I)
DESC_BAD = re.compile(rf"{DATE}|{TICKET}|\b(?:draft|rollout|roll-out|copy|backup|clone)\b", re.I)
NOTE = re.compile(
    rf"\b(?:scoping|implementation|internal|dev|engineering|history|change) note\b"
    rf"|\b(?:this|the) (?:rule|line|step|check|instruction) (?:was|is) (?:added|introduced|kept)\b"
    rf"|\b(?:added|introduced) (?:because|after|to fix)\b"
    rf"|\bfix(?:es|ed)? for\b|\bfixed (?:in|on|after)\b|\bworkaround\b|\bwork-around\b|\bhack\b|\bband-?aid\b"
    rf"|\bknown (?:bug|issue)\b|\bregression\b|\btemporar(?:y|ily)\b|{TICKET}",
    re.I)
LIST_LINE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s", re.M)
PROSE_STEP_FIELDS = {"ask": ("instruction", "exact_words"), "send": ("instruction", "message"), "set": ("instruction",)}
GI_WARN, GI_FAIL, DESC_MAX, STEP_MAX, STEP_LIST_MAX = 1500, 4000, 300, 1200, 6


def steps(node):
    if isinstance(node, dict):
        if isinstance(node.get("type"), str) and "id" in node:
            yield node
        for v in node.values():
            yield from steps(v)
    elif isinstance(node, list):
        for v in node:
            yield from steps(v)


def texts(pb):
    for field in ("name", "description", "general_instructions"):
        yield field, field, pb.get(field) or ""
    for s in steps(pb.get("sections") or pb.get("content") or []):
        for field in PROSE_STEP_FIELDS.get(s["type"], ()):
            value = s.get(field)
            if isinstance(value, str) and value.strip():
                yield f"{s['type']} {s['id']}", field, value


def snippet(text, m):
    return " ".join(text[max(0, m.start() - 50):m.end() + 50].split())


def findings(pb):
    out = []
    name, desc, gi = pb.get("name") or "", pb.get("description") or "", pb.get("general_instructions") or ""
    if m := NAME_TAG.search(name):
        out.append(("FAIL", "T1", "name", "name", name, f"name carries {m.group(0).strip()!r}: name the customer's intent only"))
    if not desc.strip() and pb.get("can_run_standalone") is not False:
        out.append(("FAIL", "T3", "description", "description", desc, "description is empty: the reasoner routes on it"))
    elif m := DESC_BAD.search(desc):
        out.append(("FAIL", "T3", "description", "description", desc, f"description carries {m.group(0)!r}"))
    if desc.strip() and pb.get("can_run_standalone") is not False and not desc.strip().lower().startswith("use when"):
        out.append(("WARN", "T4", "description", "description", desc, "description should start \"Use when\""))
    if len(desc) > DESC_MAX:
        out.append(("WARN", "T4", "description", "description", desc, f"description is {len(desc)} characters, over {DESC_MAX}"))
    if len(gi) > GI_WARN:
        level = "FAIL" if len(gi) > GI_FAIL else "WARN"
        out.append((level, "T5", "general_instructions", "general_instructions", gi,
                    f"general instructions are {len(gi)} characters and go into every step's prompt: "
                    f"move step-specific rules into their step"))
    for where, field, text in texts(pb):
        if field == "name":
            continue
        if m := NOTE.search(text):
            out.append(("FAIL", "T6", where, field, text, f"history or justification note: {snippet(text, m)!r}"))
        if where.split()[0] in PROSE_STEP_FIELDS and field == "instruction":
            lists = len(LIST_LINE.findall(text))
            if len(text) > STEP_MAX or lists > STEP_LIST_MAX:
                out.append(("WARN", "T7", where, field, text,
                            f"instruction is {len(text)} characters with {lists} list lines: move branching to "
                            f"IF_ELSE or a code tool"))
    return out


def new_findings(base, head):
    old = {(where, field): text for where, field, text in texts(base or {})}
    return [f for f in findings(head) if old.get((f[2], f[3])) != f[4]]


def duplicate_names(pbs):
    seen, out = {}, []
    for pb in pbs:
        key = re.sub(r"[^a-z0-9]+", " ", (pb.get("name") or "").lower()).strip()
        if key in seen:
            out.append(("WARN", "T2", "name", "name", pb.get("name"), f"same name as {seen[key]!r}"))
        else:
            seen[key] = pb.get("name")
    return out


def load(path):
    doc = json.loads(Path(path).read_text())
    return doc.get("playbook", doc) if isinstance(doc, dict) else doc


def files(args):
    for a in args:
        p = Path(a)
        yield from sorted(p.rglob("*.json")) if p.is_dir() else [p]


def report(rows, label):
    for level, rule, where, _field, _text, msg in rows:
        print(f"{level} {rule} {label} [{where}] {msg}")


def main(argv):
    if "--base" in argv:
        i = argv.index("--base")
        base, head = load(argv[i + 1]), load(argv[i + 2])
        rows = new_findings(base, head)
        report(rows, head.get("name"))
        print(f"{sum(r[0] == 'FAIL' for r in rows)} FAIL, {sum(r[0] == 'WARN' for r in rows)} WARN")
        return 1 if any(r[0] == "FAIL" for r in rows) else 0
    active_only, summary = "--active-only" in argv, "--summary" in argv
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    pbs = []
    for path in files(args):
        try:
            pb = load(path)
        except (ValueError, OSError):
            continue
        if not isinstance(pb, dict) or (active_only and pb.get("is_active") is False):
            continue
        pbs.append(pb)
    per_rule, fails, warns = {}, 0, 0
    for pb in pbs:
        rows = findings(pb)
        for r in rows:
            per_rule[(r[1], r[0])] = per_rule.get((r[1], r[0]), 0) + 1
        fails += sum(r[0] == "FAIL" for r in rows)
        warns += sum(r[0] == "WARN" for r in rows)
        if not summary:
            report(rows, pb.get("name"))
    dups = duplicate_names(pbs)
    warns += len(dups)
    if not summary:
        report(dups, "")
    print(f"checked {len(pbs)} playbooks: {fails} FAIL, {warns + 0} WARN")
    if summary:
        for (rule, level), n in sorted(per_rule.items()):
            print(f"  {rule} {level}: {n}")
        if dups:
            print(f"  T2 WARN: {len(dups)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
