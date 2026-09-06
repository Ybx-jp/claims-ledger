"""QE6 — confirming a residual LOW-36-class defect: option-shaped pins (`@--foo=bar`)
are misclassified as `unstable-pin` because `git rev-parse --symbolic-full-name` echoes
unrecognized double-dash arguments back on stdout with exit 0, which `is_object_name()`
reads as "this is a real symbolic ref name". Compare against `resolve`'s independent
answer for the same pin — do the two checkers now agree or contradict?"""

from claims_ledger import freshness, resolve, validate
from claims_ledger.schema import open_ledger, exit_code


def build_dash_pin(project, pin_text):
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "artifacts")
    assert project.cl("new", "fraction-law") == 0
    path = next(project.entries.glob("A0001-*.md"))
    project.write_full_entry(path)
    text = path.read_text(encoding="utf-8").replace(
        '- lab: docs/note-001.md § "Observation" @working',
        f"- experiment: docs/note-001.md @{pin_text}",
    )
    path.write_text(text, encoding="utf-8")
    assert project.cl("sha", "--write", str(path)) == 0
    project.git("add", "-A")
    project.git("commit", "-qm", "the claim")
    return path


def test_option_shaped_pin_vs_resolve(project):
    for pin_text in ["--upload-pack=x", "--foo", "--depth=1"]:
        build_dash_pin(project, pin_text)
        ledger = open_ledger(root=project.root)
        fresh = [(r.outcome, r.message) for r in freshness.run(ledger)]
        res = [(r.outcome, r.message) for r in resolve.run(ledger)]
        val = [(r.outcome, r.message) for r in validate.run(ledger)]
        print(f"\n=== pin={pin_text!r} ===")
        print("freshness:", fresh)
        print("resolve:  ", res)
        print("validate: ", val)
        print("CLI check exit:", project.cl("check"))
