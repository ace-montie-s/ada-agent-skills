"""Evidence integrity and safe HTML tests. Run with unittest discovery."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "render.py"
loader = importlib.util.spec_from_file_location("review_renderer", MODULE)
renderer = importlib.util.module_from_spec(loader)
loader.loader.exec_module(renderer)


def example():
    return {
        "schema_version": 1, "review_id": "delivery-review", "revision": "r1",
        "title": "Delivery review", "summary": "Inspect the support offer.",
        "cases": [{"id": "case-1", "title": "Late delivery", "run_id": "run-1", "status": "fail",
                   "criteria": [{"id": "c1", "text": "Ask for status", "status": "fail", "reason": "Support offered first"}],
                   "turns": [{"id": "t1", "role": "user", "language": "en", "text": "Delivery is late."},
                             {"id": "t2", "role": "agent", "language": "en", "text": "Would you like support?"}],
                   "findings": [{"id": "f1", "kind": "failure", "turn_id": "t2", "criterion_id": "c1",
                                 "quote": "support", "title": "Support first", "observed": "No status asked", "expected": "Ask for status"}]}]
    }


def feedback(spec):
    return {"schema_version": 1, "review_id": spec["review_id"], "revision": spec["revision"],
            "fingerprint": renderer.fingerprint(spec), "comments": [{"case_id": "case-1", "run_id": "run-1", "turn_id": "t2",
                                                                     "quote": "Would you like support?", "comment": "Ask for status first", "decision": "change"}]}


class ReviewTests(unittest.TestCase):
    def test_full_dialogue_embedded_and_recoverable(self):
        spec = example()
        output = renderer.render(spec)
        encoded = output.split('<script id="review-data" type="application/json">')[1].split('</script>')[0]
        self.assertEqual(json.loads(encoded)["review"], spec)
        self.assertNotIn("__REVIEW_DATA__", output)

    def test_script_breakout_is_inert(self):
        spec = example()
        attack = '</script><img src=x onerror="alert(1)">\u2028'
        spec["title"] = attack
        spec["cases"][0]["turns"][0]["text"] = attack
        output = renderer.render(spec)
        self.assertNotIn(attack, output)
        self.assertIn('\\u003c/script\\u003e', output)
        self.assertNotIn("innerHTML", output)

    def test_translation_required(self):
        spec = example()
        turn = spec["cases"][0]["turns"][0]
        turn.update(language="id", text="Tolong bantu.")
        with self.assertRaisesRegex(ValueError, "translation"):
            renderer.render(spec)
        turn["translation"] = "Please help."
        renderer.validate(spec)

    def test_broken_evidence_anchors_rejected(self):
        for key, value in [("turn_id", "missing"), ("criterion_id", "missing"), ("quote", "not in message")]:
            with self.subTest(key=key):
                spec = example()
                spec["cases"][0]["findings"][0][key] = value
                with self.assertRaises(ValueError):
                    renderer.render(spec)

    def test_reviewer_concern_does_not_change_saved_pass(self):
        spec = example()
        case = spec["cases"][0]
        case["status"] = case["criteria"][0]["status"] = "pass"
        with self.assertRaisesRegex(ValueError, "failed criterion"):
            renderer.render(spec)
        case["findings"][0]["kind"] = "concern"
        self.assertEqual(renderer.validate(spec)["cases"][0]["status"], "pass")

    def test_missing_transcript_keeps_unknown(self):
        spec = example()
        case = spec["cases"][0]
        case.update(status="unknown", turns=[], findings=[], criteria=[])
        renderer.render(spec)

    def test_reviewer_failure_preserves_saved_pass_and_requires_rule(self):
        spec = example()
        case = spec["cases"][0]
        case["status"] = case["criteria"][0]["status"] = "pass"
        finding = case["findings"][0]
        finding.update(basis="reviewer")
        with self.assertRaisesRegex(ValueError, "acceptance rule"):
            renderer.render(spec)
        finding["rule"] = "Give guidance and check elapsed time before offering support."
        self.assertEqual(renderer.validate(spec)["cases"][0]["status"], "pass")
        output = renderer.render(spec)
        self.assertIn("Reviewer failed", output)
        self.assertIn("Saved check:", output)

    def test_unknown_failure_basis_rejected(self):
        spec = example()
        spec["cases"][0]["findings"][0]["basis"] = "invented"
        with self.assertRaisesRegex(ValueError, "basis"):
            renderer.render(spec)

    def test_duplicate_id_rejected(self):
        spec = example()
        spec["cases"].append(copy.deepcopy(spec["cases"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate case"):
            renderer.render(spec)
        spec = example()
        spec["cases"][0]["turns"].append(copy.deepcopy(spec["cases"][0]["turns"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate turn"):
            renderer.render(spec)

    def test_feedback_round_trip(self):
        spec = example()
        f = feedback(spec)
        self.assertEqual(renderer.validate_feedback(f, spec), f)
        self.assertIn("Ask for status first", renderer.render(spec, f))

    def test_stale_or_wrong_feedback_rejected(self):
        spec = example()
        for key, value in [("review_id", "other"), ("revision", "r2"), ("fingerprint", "changed")]:
            f = feedback(spec)
            f[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                renderer.validate_feedback(f, spec)
        for key, value in [("case_id", "other"), ("run_id", "other"), ("turn_id", "other"), ("quote", "edited")]:
            f = feedback(spec)
            f["comments"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                renderer.validate_feedback(f, spec)
        f = feedback(spec)
        spec["cases"][0]["turns"][0]["text"] = "Changed evidence"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            renderer.validate_feedback(f, spec)


if __name__ == "__main__":
    unittest.main()
