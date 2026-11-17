import json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def make_fixture():
    """A synthetic 35 s transcript, so the rules can be tested without any video."""
    d = tempfile.mkdtemp(prefix="agent-editor-test-")
    names = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet"]
    words, t = [], 0.0
    for i in range(100):
        w = "Claude" if i == 20 else names[i % 10]
        words.append({"t": round(t, 2), "e": round(t + 0.3, 2), "w": w})
        t += 0.35
    ing = {"media": {"file": "project/source.mp4", "duration": round(t, 2), "w": 1280, "h": 720,
                     "origin": "fixture", "origin_path": "", "origin_start": 0},
           "words": words, "silences": [], "sentences": [], "thumbs": []}
    json.dump(ing, open(os.path.join(d, "ingest.json"), "w"))
    return d

os.environ["AGENT_EDITOR_PROJECT"] = make_fixture()
import server  # noqa: E402

class Ops(unittest.TestCase):
    def setUp(self):
        server.STATE = server.new_state()
        server.handle_op({"op": "hello", "agent": "A", "role": "cutter"})
        server.handle_op({"op": "hello", "agent": "R", "role": "reviewer"})
        self.w = server.WORDS

    def op(self, **k):
        return server.handle_op(k)[1]

    def after(self, i):
        w = self.w
        return round(min(w[i]["e"] + 0.04, (w[i]["e"] + w[i + 1]["t"]) / 2), 3)

    def before(self, i):
        w = self.w
        return round(max(0.0, max(w[i]["t"] - 0.06, (w[i - 1]["e"] + w[i]["t"]) / 2)), 3)

    def test_needs_hello(self):
        self.assertFalse(self.op(op="cut", agent="Z", start=1, end=3)["ok"])

    def test_cut_between_words_ok(self):
        w0, w1 = self.w[0], self.w[1]
        r = self.op(op="cut", agent="A", start=self.before(1), end=self.after(5))
        self.assertTrue(r["ok"], r)

    def test_cut_inside_word_refused(self):
        w = self.w[3]
        mid = (w["t"] + w["e"]) / 2
        r = self.op(op="cut", agent="A", start=mid, end=mid + 2)
        self.assertFalse(r["ok"])
        self.assertIn("inside the word", r["error"])

    def test_overlap_refused(self):
        a = self.op(op="cut", agent="A", start=0, end=self.after(6))
        self.assertTrue(a["ok"], a)
        b = self.op(op="cut", agent="A", start=self.before(3), end=self.after(10))
        self.assertFalse(b["ok"])
        self.assertIn("overlaps", b["error"])

    def test_caption_rules(self):
        w = self.w[:3]
        ok = self.op(op="caption", agent="A", start=w[0]["t"], end=w[2]["e"], text=" ".join(x["w"] for x in w)[:22])
        self.assertTrue(ok["ok"], ok)
        self.assertFalse(self.op(op="caption", agent="A", start=50, end=51, text="one two three four")["ok"])
        bad = self.op(op="caption", agent="A", start=self.w[40]["t"], end=self.w[41]["e"], text="banana pizza")
        self.assertFalse(bad["ok"])
        self.assertIn("not spoken", bad["error"])

    def test_fx_spacing(self):
        self.assertTrue(self.op(op="fx", agent="A", type="punch_zoom", at=10, dur=1.2)["ok"])
        self.assertFalse(self.op(op="fx", agent="A", type="punch_zoom", at=12, dur=1.2)["ok"])
        self.assertTrue(self.op(op="fx", agent="A", type="punch_zoom", at=16, dur=1.2)["ok"])

    def test_graphic_rules(self):
        w = next(x for x in self.w if x["w"].strip(",.").lower() == "claude")
        ok = self.op(op="graphic", agent="A", template="lower_third", text="Claude", at=w["t"], dur=2)
        self.assertTrue(ok["ok"], ok)
        self.assertFalse(self.op(op="graphic", agent="A", template="stat_card", text="Claude", at=w["t"] + 1, dur=2)["ok"])
        bad = self.op(op="graphic", agent="A", template="highlight", text="banana", at=w["t"] + 20, dur=2)
        self.assertFalse(bad["ok"])
        self.assertIn("not spoken", bad["error"])
        self.assertFalse(self.op(op="graphic", agent="A", template="nope", text="Claude", at=w["t"] + 20)["ok"])

    def test_only_reviewer_rejects(self):
        cid = self.op(op="cut", agent="A", start=0, end=self.after(6))["id"]
        self.assertFalse(self.op(op="reject", agent="A", id=cid, reason="not allowed for me")["ok"])
        self.assertTrue(self.op(op="reject", agent="R", id=cid, reason="cuts the middle of a sentence")["ok"])
        self.assertEqual(server.STATE["cuts"][0]["status"], "rejected")

if __name__ == "__main__":
    unittest.main()
