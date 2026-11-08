"""Regression checks for evidence-ledger integrity, not claimed semantic review."""
import copy
from pathlib import Path
import tempfile
import unittest

from corpus_audit import markdown_blocks, read_records, validate_records


class InventoryTests(unittest.TestCase):
    def test_nested_fences_and_unclosed_source_are_preserved(self):
        blocks = markdown_blocks("source.md", b"# A\n````text\n```py\nx\n```\n````\n# B\n~~~python\ny\n")
        self.assertEqual([(b["start_line"], b["end_line"], b["closed"]) for b in blocks],
                         [(2, 6, True), (8, 9, False)])
        self.assertEqual(blocks[1]["heading"], "# B")
        self.assertNotEqual(blocks[0]["content_sha256"], blocks[1]["content_sha256"])

    def setUp(self):
        self.manifest = {"files": [{"path": p, "sha256": "same", "kind": "text", "lines": 4}
                                    for p in ("a.md", "b.md")]}
        self.record = {"path": "a.md", "sha256": "same", "status": "read", "summary": "Source read",
                       "components": ["example"], "variant_notes": [], "next_actions": [], "uncertainties": [],
                       "evidence": [{"start_line": 1, "end_line": 4, "finding": "A bounded source."}]}
        self.duplicate = dict(self.record, path="b.md", status="duplicate-reviewed", duplicate_of="a.md")

    def test_complete_equal_duplicate(self):
        self.assertEqual(validate_records(self.manifest, [self.record, self.duplicate]), [])

    def test_missing_stale_and_out_of_bounds_fail(self):
        changed = copy.deepcopy(self.record)
        changed["sha256"] = "stale"
        changed["evidence"][0]["end_line"] = 5
        errors = validate_records(self.manifest, [changed])
        self.assertTrue(any("Missing reading" in e for e in errors))
        self.assertTrue(any("Stale content" in e for e in errors))
        self.assertTrue(any("Invalid evidence" in e for e in errors))

    def test_duplicate_cycle_and_unequal_hash_fail(self):
        a = dict(self.record, status="duplicate-reviewed", duplicate_of="b.md")
        errors = validate_records(self.manifest, [a, self.duplicate])
        self.assertEqual(sum("directly inspected" in e for e in errors), 2)
        changed = copy.deepcopy(self.manifest)
        changed["files"][1]["sha256"] = "different"
        errors = validate_records(changed, [self.record, self.duplicate])
        self.assertTrue(any("Unequal duplicate" in e for e in errors))

    def test_partial_and_duplicate_records_fail(self):
        errors = validate_records(self.manifest, [dict(self.record, status="partial"), self.record])
        self.assertTrue(any("Duplicate reading" in e for e in errors))
        errors = validate_records(self.manifest, [dict(self.record, status="partial"), self.duplicate])
        self.assertTrue(any("Incomplete/unknown" in e for e in errors))

    def test_malformed_schema_does_not_pass_or_crash(self):
        changed = dict(self.record, summary=17, components="not-a-list", variant_notes=None,
                       next_actions={}, uncertainties=False,
                       evidence=[{"start_line": True, "end_line": True, "finding": 9}])
        errors = validate_records(self.manifest, [changed, self.duplicate])
        self.assertGreaterEqual(len(errors), 7)
        malformed = [None, [], {"path": []}, dict(self.record, status=[]),
                     dict(self.duplicate, duplicate_of={}), dict(self.record, evidence=[None])]
        for value in malformed:
            with self.subTest(record=value):
                self.assertTrue(validate_records(self.manifest, [value]))

    def test_invalid_ledger_wrapper_reports_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "read-bad.json"
            for value in ('{}', '{"files": {}}', 'null', '{'):
                path.write_text(value)
                with self.subTest(value=value), self.assertRaisesRegex(ValueError, "read-bad.json"):
                    read_records(Path(directory))


if __name__ == "__main__":
    unittest.main()
