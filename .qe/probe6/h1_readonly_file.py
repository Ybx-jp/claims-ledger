"""Hypothesis 1: os.replace into a read-only FILE succeeds when the DIRECTORY is
writable. The old truncating write would have refused (PermissionError). Check
sha --write, propagate --write, freshness --write against a mode-0444 entry."""
import sys, tempfile, stat
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

APPEND = "<!-- APPEND BELOW THIS LINE ONLY -->"


def perm(path):
    return oct(stat.S_IMODE(path.stat().st_mode))


def sha_write():
    print("\n--- sha --write against a chmod 0444 (uncommitted, so no is_committed refusal) entry ---")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new", "a-claim") == 0
    a = p.entry("A0001-a-claim.md")
    p.write_full_entry(a)
    t = a.read_text(encoding="utf-8")
    t = t.replace("cohort: the synthetic graph of these tests", "cohort: edited after chmod")
    a.write_text(t, encoding="utf-8")
    a.chmod(0o444)
    print("mode before:", perm(a))
    before = a.read_bytes()
    rc = p.cl("sha", "--write", str(a))
    after = a.read_bytes()
    print("sha --write rc:", rc, "(old behaviour: PermissionError -> exit 2, file unchanged)")
    print("mode after:", perm(a))
    print("file content changed:", before != after)
    if before != after:
        print("!!! a mode-0444 entry was rewritten by sha --write; the read-only refusal is bypassed")


def propagate_write():
    print("\n--- propagate --write appending a verdict to a mode 0444, GIT-COMMITTED entry ---")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new", "a-claim") == 0
    a = p.entry("A0001-a-claim.md")
    p.write_full_entry(a)
    p.git("init", "-q"); p.git("add", "-A"); p.git("commit", "-qm", "seal")
    a.chmod(0o444)
    print("mode before:", perm(a))

    assert p.cl("new", "b-claim") == 0
    b = p.entry("A0002-b-claim.md")
    t = b.read_text(encoding="utf-8")
    t = t.replace("TODO: the claim, in this project's words. No quotation marks.", "The first claim is unsupported.")
    t = t.replace("metric: TODO", "metric: m").replace("cohort: TODO", "cohort: c").replace("condition: TODO", "condition: d")
    t = t.replace("- TODO: one typed pointer per line", '- lab: docs/note-001.md § "Observation" @working\n- entry: A0001-a-claim · challenges')
    t = t.replace("TODO: the rule by which the grounds support the assertion.", "Because the grounds were withdrawn.")
    b.write_text(t, encoding="utf-8")
    assert p.cl("sha", "--write", str(b)) == 0

    before = a.read_bytes()
    rc = p.cl("propagate", "--write")
    after = a.read_bytes()
    print("propagate --write rc:", rc)
    print("mode after:", perm(a))
    print("verdict appended to a mode-0444 entry:", before != after and APPEND.encode() in after)
    print("check rc:", p.cl("check"))


def freshness_write():
    print("\n--- freshness --write against a mode 0444, git-committed, artifact-pinned entry ---")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new", "a-claim") == 0
    a = p.entry("A0001-a-claim.md")
    p.write_full_entry(a)
    t = a.read_text(encoding="utf-8")
    # add a Grounds pointer that pins the docs artifact so freshness has something to check
    t = t.replace(
        '- lab: docs/note-001.md § "Observation" @working',
        '- lab: docs/note-001.md § "Observation" @working',
    )
    a.write_text(t, encoding="utf-8")
    assert p.cl("sha", "--write", str(a)) == 0
    p.git("init", "-q"); p.git("add", "-A"); p.git("commit", "-qm", "seal")
    a.chmod(0o444)
    print("mode before:", perm(a))
    before = a.read_bytes()
    rc = p.cl("freshness", "--write")
    after = a.read_bytes()
    print("freshness --write rc:", rc)
    print("mode after:", perm(a))
    print("file content changed:", before != after)


def exit_code_regression_check():
    print("\n--- sanity: the audit's earlier claim ('read-only refusals exit 2 cleanly') ---")
    print("checked against: read-only DIRECTORY (entries/ chmod 0555), which is a different")
    print("surface (temp file creation itself fails there) -- see h2 probe.")


if __name__ == "__main__":
    sha_write()
    propagate_write()
    freshness_write()
    exit_code_regression_check()
