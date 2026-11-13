#!/usr/bin/env python3
"""Offline regression for the replay join in analyze_replay.py.

No API calls and no sandbox needed: this only reads committed JSON.
Run: python3 test_replay_join.py   (or python3 -m unittest test_replay_join)

Fixtures (fixtures/<cell>.events.jsonl and fixtures/<cell>.replay.json) are
extracted from logs/<cell>.jsonl and replay-results.jsonl by
`python3 test_replay_join.py --write-fixtures`. The extract keeps every
tool_call, tool_result, assay, variant and variants_result event in log order,
replaces `variants` versions by their sha256, drops other tool arguments and
assay commands, and truncates tool results to 160 characters. The first test
checks that the committed fixtures still equal that extract of the committed
logs.

Covers proof review 5884687642, items 1-3:
- luna-hard-1: historical steps 6 adopt, 7 rejected, 13 adopt; the replay
  adopts at all three; step 7 is the rejected -> adopt transition; replay
  step 13 pairs with historical step 13, and its incumbent is still the
  step 6 median, so the step 7 replay adoption was replaced before step 13.
- astra-max-1-retry: step 7 adopt -> adopt, step 12 rejected -> no-win
  (candidates within the 3% WIN_MARGIN of the incumbent).
- the whole record: 111 calls joined on (cell, step), 0 unmatched, 2
  rejections, 109 scored, 39 replay adoptions, 228 reproduced candidate
  evaluations plus 4 newly evaluated ones.
"""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIX = ROOT / "fixtures"
CELLS = ("luna-hard-1", "astra-max-1-retry")

_argv = sys.argv[:]
sys.path.insert(0, str(ROOT))
import analyze_replay as ar  # noqa: E402  (sets sys.argv for harness import)
sys.argv = _argv


def read_replay():
    with open(ROOT / "replay-results.jsonl") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def extract_events(events):
    out = []
    for e in events:
        k = e.get("kind")
        if k == "tool_call":
            rec = {"kind": k, "step": e.get("step"), "name": e.get("name")}
            if e.get("name") == "variants":
                args = e.get("args") or {}
                rec["args"] = {"path": args.get("path"),
                               "versions_sha256": [hashlib.sha256(str(v).encode()).hexdigest()
                                                   for v in args.get("versions") or []]}
            out.append(rec)
        elif k == "tool_result":
            out.append({"kind": k, "step": e.get("step"), "name": e.get("name"),
                        "result": str(e.get("result"))[:160]})
        elif k == "assay":
            out.append({kk: e.get(kk) for kk in ("kind", "scores", "median", "ok")})
        elif k in ("variant", "variants_result"):
            out.append({kk: v for kk, v in e.items() if kk != "t"})
    return out


def load_fixture(cell):
    with open(FIX / f"{cell}.events.jsonl") as fh:
        events = [json.loads(l) for l in fh if l.strip()]
    replay = json.loads((FIX / f"{cell}.replay.json").read_text())
    return events, replay


def write_fixtures():
    FIX.mkdir(exist_ok=True)
    replay = {r["cell"]: r for r in read_replay()}
    for cell in CELLS:
        with open(FIX / f"{cell}.events.jsonl", "w") as fh:
            for e in extract_events(ar.load_events(cell)):
                fh.write(json.dumps(e) + "\n")
        r = replay[cell]
        (FIX / f"{cell}.replay.json").write_text(json.dumps(
            {"cell": cell, "variants_calls": r["variants_calls"]}, indent=1) + "\n")


def by_step(joined):
    return {p["step"]: p for p in joined["pairs"]}


class FixtureFaithful(unittest.TestCase):
    def test_fixtures_match_committed_logs(self):
        replay = {r["cell"]: r for r in read_replay()}
        for cell in CELLS:
            events, rep = load_fixture(cell)
            self.assertEqual(events, extract_events(ar.load_events(cell)), cell)
            self.assertEqual(rep["variants_calls"], replay[cell]["variants_calls"], cell)


class LunaHard1(unittest.TestCase):
    def setUp(self):
        events, rep = load_fixture("luna-hard-1")
        self.j = ar.join_cell("luna-hard-1", events, rep["variants_calls"])
        self.p = by_step(self.j)

    def test_keyed_by_step(self):
        self.assertEqual(sorted(self.p), [6, 7, 13])
        self.assertTrue(all(p["match"] == "matched" for p in self.j["pairs"]))
        self.assertEqual(self.j["problems"], {})

    def test_historical_outcomes(self):
        self.assertEqual([self.p[s]["hist_outcome"] for s in (6, 7, 13)],
                         ["adopt", "rejected", "adopt"])
        self.assertTrue(self.p[7]["hist_result"].startswith(ar.REJECTION))

    def test_three_replay_adoptions(self):
        self.assertEqual([self.p[s]["rep_outcome"] for s in (6, 7, 13)], ["adopt"] * 3)
        self.assertEqual([self.p[s]["rep_winner"] for s in (6, 7, 13)], [0, 0, 0])

    def test_step7_rejected_to_adopt(self):
        p7 = self.p[7]
        self.assertEqual((p7["hist_outcome"], p7["rep_outcome"]), ("rejected", "adopt"))
        self.assertAlmostEqual(p7["rep_winner_median"], 56.473219328167716)
        self.assertAlmostEqual(p7["inc_rep"], 53.39869428694062)
        self.assertEqual(p7["candidates"], "newly-evaluated")

    def test_step13_pairs_with_historical_step13(self):
        p13 = self.p[13]
        self.assertAlmostEqual(p13["hist_median"], 56.473219328167716)
        self.assertAlmostEqual(p13["rep_winner_median"], 56.473219328167716)
        self.assertEqual(p13["candidates"], "reproduced")

    def test_step13_incumbent_is_still_step6_median(self):
        self.assertAlmostEqual(self.p[13]["inc_rep"], self.p[6]["rep_winner_median"])
        self.assertEqual(self.p[7]["next_call_incumbent"], "different-median")

    def test_reproduction_counts(self):
        self.assertEqual(self.j["repro"], {"exact": 4, "newly_evaluated": 2})


class AstraMax1Retry(unittest.TestCase):
    def setUp(self):
        events, rep = load_fixture("astra-max-1-retry")
        self.j = ar.join_cell("astra-max-1-retry", events, rep["variants_calls"])
        self.p = by_step(self.j)

    def test_steps_and_transitions(self):
        self.assertEqual(sorted(self.p), [7, 12])
        self.assertEqual((self.p[7]["hist_outcome"], self.p[7]["rep_outcome"]), ("adopt", "adopt"))
        self.assertEqual((self.p[12]["hist_outcome"], self.p[12]["rep_outcome"]),
                         ("rejected", "no-win"))

    def test_step12_gain_under_margin(self):
        p12 = self.p[12]
        best = max(s[1] for s in p12["rep_scores"])
        self.assertLess(best, p12["inc_rep"] * ar.harness.WIN_MARGIN)
        self.assertGreater(best, p12["inc_rep"])


class PositionalHazard(unittest.TestCase):
    def test_missing_replay_call_is_counted_not_shifted(self):
        events, rep = load_fixture("luna-hard-1")
        calls = [c for c in rep["variants_calls"] if c["step"] != 7]
        j = ar.join_cell("luna-hard-1", events, calls)
        p = by_step(j)
        self.assertEqual(p[7]["match"], "historical-only")
        self.assertAlmostEqual(p[13]["rep_winner_median"], p[13]["hist_median"])
        s = ar.summarize([j])
        self.assertEqual((s["unmatched_historical_calls"], s["unmatched_replay_calls"]), (1, 0))


class WholeRecord(unittest.TestCase):
    def test_summary(self):
        results = read_replay()
        s = ar.summarize([ar.join_cell(r["cell"], ar.load_events(r["cell"]),
                                       r.get("variants_calls", [])) for r in results])
        self.assertEqual(s["cells"], 87)
        self.assertEqual((s["historical_variants_calls"], s["replay_variants_calls"],
                          s["matched_calls"]), (111, 111, 111))
        self.assertEqual((s["unmatched_historical_calls"], s["unmatched_replay_calls"]), (0, 0))
        self.assertEqual(s["historical_outcomes"], {"adopt": 38, "no-win": 71, "rejected": 2})
        self.assertEqual(s["historical_scored_calls"], 109)
        self.assertEqual(s["replay_outcomes"], {"adopt": 39, "no-win": 72})
        self.assertEqual(s["outcome_transitions"], {"adopt->adopt": 38, "no-win->no-win": 71,
                                                    "rejected->adopt": 1, "rejected->no-win": 1})
        self.assertEqual(s["replay_same_winner"], 38)
        self.assertEqual(s["replay_adoptions_from_historical_rejection"], ["luna-hard-1 step 7"])
        self.assertEqual((s["candidate_evals_reproduced_exact"], s["candidate_evals_drifted"],
                          s["candidate_evals_missing"], s["candidate_evals_newly_evaluated"]),
                         (228, 0, 0, 4))
        self.assertEqual(s["log_attachment_problems"], {})


if __name__ == "__main__":
    if "--write-fixtures" in sys.argv:
        write_fixtures()
        print("fixtures written")
    else:
        unittest.main()
