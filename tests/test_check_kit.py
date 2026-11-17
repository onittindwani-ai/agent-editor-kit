import os, re, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = os.path.join(ROOT, "scripts", "check_kit.py")


def run(root_dir):
    """Run a copy of the checker against a fake kit folder."""
    scripts = os.path.join(root_dir, "scripts")
    os.makedirs(scripts, exist_ok=True)
    with open(CHECK, encoding="utf-8") as f, open(os.path.join(scripts, "check_kit.py"), "w", encoding="utf-8") as g:
        g.write(f.read())
    return subprocess.run([sys.executable, os.path.join(scripts, "check_kit.py"), "--min-skills", "1", "--min-lines", "12"],
                          capture_output=True, text=True)


def skill(root_dir, name, body, fm_name=None):
    d = os.path.join(root_dir, "skills", name)
    os.makedirs(d, exist_ok=True)
    fm_name = fm_name or name
    with open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(f"---\nname: {fm_name}\ndescription: A description that is clearly long enough to pass the check.\n---\n{body}\n")


GOOD = "line\n" * 10


class CheckKit(unittest.TestCase):
    def test_good_kit_passes(self):
        with tempfile.TemporaryDirectory() as d:
            skill(d, "ae-one", GOOD + "Hand off to ae-two.")
            skill(d, "ae-two", GOOD)
            r = run(d)
            self.assertEqual(r.returncode, 0, r.stdout)

    def test_unknown_skill_link_fails(self):
        with tempfile.TemporaryDirectory() as d:
            skill(d, "ae-one", GOOD + "Hand off to ae-missing.")
            r = run(d)
            self.assertEqual(r.returncode, 1)
            self.assertIn("unknown skill ae-missing", r.stdout)

    def test_name_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as d:
            skill(d, "ae-one", GOOD, fm_name="ae-other")
            r = run(d)
            self.assertEqual(r.returncode, 1)
            self.assertIn("front matter name", r.stdout)

    def test_path_and_dash_fail(self):
        with tempfile.TemporaryDirectory() as d:
            skill(d, "ae-one", GOOD + "see ~/stuff\nand a — dash")
            r = run(d)
            self.assertEqual(r.returncode, 1)
            self.assertIn("local path", r.stdout)
            self.assertIn("em or en dash", r.stdout)

    def test_too_short_fails(self):
        with tempfile.TemporaryDirectory() as d:
            skill(d, "ae-one", "x")
            r = run(d)
            self.assertEqual(r.returncode, 1)
            self.assertIn("lines (minimum", r.stdout)


if __name__ == "__main__":
    unittest.main()
