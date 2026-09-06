"""Part 1 — reproduce each of the six findings by hand against the fixed tip (776500b).

Run: /tmp/qe6-write/.venv/bin/python .qe/probe6/part1_all.py
"""
import sys, tempfile, os, resource, signal, subprocess, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

APPEND = "<!-- APPEND BELOW THIS LINE ONLY -->"


def hdr(name):
    print("\n" + "=" * 10, name, "=" * 10)


# ---------------------------------------------------------------- HIGH-39 (CRLF frozen region)
def high39():
    hdr("HIGH-39: CRLF frozen region survives propagate --write, check catches any change")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new", "a-claim") == 0
    path = p.entry("A0001-a-claim.md")
    p.write_full_entry(path)
    raw = path.read_bytes()
    path.write_bytes(raw.replace(b"\n", b"\r\n"))
    p.git("init", "-q"); p.git("add", "-A"); p.git("commit", "-qm", "committed with CRLF")
    print("check on CRLF committed:", p.cl("check"))
    before_frozen = path.read_bytes().split(APPEND.encode(), 1)[0]

    assert p.cl("new", "b-claim") == 0
    b = p.entry("A0002-b-claim.md")
    t = b.read_text(encoding="utf-8")
    t = t.replace("TODO: the claim, in this project's words. No quotation marks.", "The first claim is not supported.")
    t = t.replace("metric: TODO", "metric: m").replace("cohort: TODO", "cohort: c").replace("condition: TODO", "condition: d")
    t = t.replace("- TODO: one typed pointer per line", '- lab: docs/note-001.md § "Observation" @working\n- entry: A0001-a-claim · challenges')
    t = t.replace("TODO: the rule by which the grounds support the assertion.", "Because the grounds were withdrawn.")
    b.write_text(t, encoding="utf-8")
    assert p.cl("sha", "--write", str(b)) == 0

    rc = p.cl("propagate", "--write")
    after_frozen = path.read_bytes().split(APPEND.encode(), 1)[0]
    print("propagate --write rc:", rc)
    print("frozen region byte-identical:", before_frozen == after_frozen)
    diff = subprocess.run(["git", "-C", str(p.root), "diff", "--stat"], capture_output=True, text=True).stdout
    print("git diff --stat:\n", diff)
    print("check after:", p.cl("check"))
    # also the reverse: hand-rewrite frozen region to CRLF post-commit, check must catch it
    tmp2 = Path(tempfile.mkdtemp())
    p2 = make(tmp2, git=False)
    assert p2.cl("new", "a-claim") == 0
    path2 = p2.entry("A0001-a-claim.md")
    p2.write_full_entry(path2)
    p2.git("init", "-q"); p2.git("add", "-A"); p2.git("commit", "-qm", "committed LF")
    raw2 = path2.read_bytes()
    head, sep, tail = raw2.partition(APPEND.encode())
    path2.write_bytes(head.replace(b"\n", b"\r\n") + sep + tail)
    print("hand-CRLF-rewrite of frozen region; check rc (want nonzero):", p2.cl("check"))
    verdict = "FIXED" if (before_frozen == after_frozen and p2.cl("check") != 0) else "NOT FIXED"
    print("VERDICT HIGH-39:", verdict)


# ---------------------------------------------------------------- HIGH-40 (registry no final newline)
def high40():
    hdr("HIGH-40: source add onto a registry with no final newline")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    reg = p.root / "ledger" / "sources.jsonl"
    raw = reg.read_bytes()
    print("registry ends with newline (before mutate):", raw.endswith(b"\n"))
    reg.write_bytes(raw.rstrip(b"\n"))
    s2 = tmp / "second.txt"; s2.write_text("Another synthetic source.\n", encoding="utf-8")
    rc = p.cl("source", "add", str(s2), "--id", "fx-second", "--type", "paper", "--citation", "Second", "--authors", "B")
    print("source add rc:", rc)
    content = reg.read_text(encoding="utf-8")
    print("registry now:\n", content)
    lines = content.splitlines()
    print("line count:", len(lines))
    print("check rc:", p.cl("check"))
    ok = rc == 0 and len(lines) == 2 and all(l.strip().startswith("{") for l in lines)
    print("VERDICT HIGH-40:", "FIXED" if ok else "NOT FIXED")


# ---------------------------------------------------------------- MEDIUM-41 (temp file + rename, RLIMIT_FSIZE)
def medium41():
    hdr("MEDIUM-41: a failed append (real RLIMIT_FSIZE) leaves the entry as it found it")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new", "a-claim") == 0
    path = p.entry("A0001-a-claim.md")
    p.write_full_entry(path)
    assert p.cl("new", "b-claim") == 0
    b = p.entry("A0002-b-claim.md")
    t = b.read_text(encoding="utf-8")
    t = t.replace("TODO: the claim, in this project's words. No quotation marks.", "The first claim is unsupported.")
    t = t.replace("metric: TODO", "metric: m").replace("cohort: TODO", "cohort: c").replace("condition: TODO", "condition: d")
    t = t.replace("- TODO: one typed pointer per line", '- lab: docs/note-001.md § "Observation" @working\n- entry: A0001-a-claim · challenges')
    t = t.replace("TODO: the rule by which the grounds support the assertion.", "Because the grounds were withdrawn.")
    b.write_text(t, encoding="utf-8")
    assert p.cl("sha", "--write", str(b)) == 0
    p.git("init", "-q"); p.git("add", "-A"); p.git("commit", "-qm", "sealed")
    before = path.read_bytes()
    size = path.stat().st_size
    limit = size + 40
    env = dict(os.environ, PROBE_LIMIT=str(limit))
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys,os,signal,resource; signal.signal(signal.SIGXFSZ, signal.SIG_IGN); "
         "lim=int(os.environ['PROBE_LIMIT']); resource.setrlimit(resource.RLIMIT_FSIZE, (lim, lim)); "
         "from claims_ledger import cli; sys.exit(cli.main(['--root', sys.argv[1], 'propagate', '--write']))",
         str(p.root)],
        env=env, capture_output=True, text=True)
    print("child rc:", r.returncode)
    print("child stderr:", r.stderr.strip()[-300:])
    after = path.read_bytes()
    print("entry bytes before/after:", len(before), len(after))
    print("entry byte-identical to committed state:", after == before)
    print("has APPEND marker still:", APPEND.encode() in after)
    print("check rc after crash:", p.cl("check"))
    # look for leftover temp files
    leftovers = [f for f in path.parent.iterdir() if f.name.startswith(".") and "claims-ledger-" in f.name]
    print("leftover temp files in entries/:", [f.name for f in leftovers])
    verdict = "FIXED" if after == before else "NOT FIXED"
    print("VERDICT MEDIUM-41:", verdict)


# ---------------------------------------------------------------- MEDIUM-42 (retry interrupted source add)
def medium42():
    hdr("MEDIUM-42: retrying an interrupted source add stores the right bytes")
    tmp = Path(tempfile.mkdtemp()); p = make(tmp, git=False)
    big = tmp / "big.txt"; big.write_text("The bytes of the second source.\n" * 80, encoding="utf-8")
    dig = hashlib.sha256(big.read_bytes()).hexdigest()
    env = dict(os.environ, PROBE_LIMIT="500")
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys,os,signal,resource; signal.signal(signal.SIGXFSZ, signal.SIG_IGN); "
         "lim=int(os.environ['PROBE_LIMIT']); resource.setrlimit(resource.RLIMIT_FSIZE, (lim, lim)); "
         "from claims_ledger import cli; sys.exit(cli.main(['--root', sys.argv[1], 'source', 'add', sys.argv[2], "
         "'--id', 'fx-2', '--type', 'paper', '--citation', 'C', '--authors', 'A']))",
         str(p.root), str(big)],
        env=env, capture_output=True, text=True)
    print("interrupted attempt rc:", r.returncode)
    print("stderr:", r.stderr.strip())
    cache = p.root / "ledger" / "cache" / dig
    print("cache file exists after interruption:", cache.exists())
    print("registry rows after interruption:", p.root.joinpath("ledger/sources.jsonl").read_text().count("{"))
    leftovers = [f.name for f in (p.root/"ledger"/"cache").iterdir() if "claims-ledger-" in f.name]
    print("leftover temp files in cache/:", leftovers)
    print("--- retry, no limit ---")
    rc = p.cl("source", "add", str(big), "--id", "fx-2", "--type", "paper", "--citation", "C", "--authors", "A")
    print("retry rc:", rc)
    ok_cache = cache.exists() and cache.stat().st_size == big.stat().st_size
    ok_digest = cache.exists() and hashlib.sha256(cache.read_bytes()).hexdigest() == dig
    print("cache size now == source size:", ok_cache, "digest matches:", ok_digest)
    print("check rc:", p.cl("check"))
    verdict = "FIXED" if (rc == 0 and ok_cache and ok_digest) else "NOT FIXED"
    print("VERDICT MEDIUM-42:", verdict)


# ---------------------------------------------------------------- MEDIUM-43 (insertion point below marker)
def medium43():
    hdr("MEDIUM-43: propagate --write never writes above the APPEND marker, even with References above it")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new", "a-claim") == 0
    a = p.entry("A0001-a-claim.md")
    p.write_full_entry(a)
    text = a.read_text(encoding="utf-8")
    # move "## References" to sit ABOVE the APPEND marker (a layout `validate` rejects)
    text2 = text.replace("\n## References\n", "\n")
    text2 = text2.replace("\n" + APPEND, "\n## References\n\n" + APPEND)
    a.write_text(text2, encoding="utf-8")
    assert p.cl("sha", "--write", str(a)) == 0
    p.git("init", "-q"); p.git("add", "-A"); p.git("commit", "-qm", "sealed, out-of-order layout")
    print("check before (want nonzero: sections out of order):", p.cl("check"))
    before = a.read_bytes()
    before_frozen = before.split(APPEND.encode(), 1)[0]

    assert p.cl("new", "b-claim") == 0
    b = p.entry("A0002-b-claim.md")
    t = b.read_text(encoding="utf-8")
    t = t.replace("TODO: the claim, in this project's words. No quotation marks.", "The first claim is unsupported.")
    t = t.replace("metric: TODO", "metric: m").replace("cohort: TODO", "cohort: c").replace("condition: TODO", "condition: d")
    t = t.replace("- TODO: one typed pointer per line", '- lab: docs/note-001.md § "Observation" @working\n- entry: A0001-a-claim · challenges')
    t = t.replace("TODO: the rule by which the grounds support the assertion.", "Because the grounds were withdrawn.")
    b.write_text(t, encoding="utf-8")
    assert p.cl("sha", "--write", str(b)) == 0

    rc = p.cl("propagate", "--write")
    after = a.read_bytes()
    after_frozen = after.split(APPEND.encode(), 1)[0]
    print("propagate --write rc:", rc)
    print("frozen region unchanged:", before_frozen == after_frozen)
    print("check after:", p.cl("check"))
    verdict = "FIXED" if before_frozen == after_frozen else "NOT FIXED"
    print("VERDICT MEDIUM-43:", verdict)


# ---------------------------------------------------------------- LOW-44 (sha --write over several paths)
def low44():
    hdr("LOW-44: sha --write a b c does not silently skip the rest")
    # NOTE: the original repro used `chmod 0444` on the middle path to force an
    # AuthoringError. Under the fixed write path that no longer fails (see Hypothesis 1
    # in Part 2) so a *committed* middle entry (refused without --force) is used instead
    # to exercise cmd_sha's per-path exception handling honestly.
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    for slug in ("one", "two", "three"):
        assert p.cl("new", slug) == 0
    entries = sorted(p.entries.glob("*.md"))
    for e in entries:
        p.write_full_entry(e)
    p.git("init", "-q")
    p.git("add", str(entries[1])); p.git("commit", "-qm", "seal the middle one")
    # edit Scope on all three so sha is stale
    for e in entries:
        t = e.read_text(encoding="utf-8")
        t = t.replace("cohort: the synthetic graph of these tests", "cohort: the synthetic graph of these tests, edited")
        e.write_text(t, encoding="utf-8")
    import io, contextlib
    buf_out, buf_err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        rc = p.cl("sha", "--write", *[str(e) for e in entries])
    print("rc:", rc)
    print("stdout:\n", buf_out.getvalue())
    print("stderr:\n", buf_err.getvalue())
    out = buf_out.getvalue() + buf_err.getvalue()
    third_mentioned = entries[2].name in out or "three" in out
    print("third path named in output:", third_mentioned)
    verdict = "FIXED" if third_mentioned else "NOT FIXED"
    print("VERDICT LOW-44:", verdict)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    fns = {"high39": high39, "high40": high40, "medium41": medium41,
           "medium42": medium42, "medium43": medium43, "low44": low44}
    if which == "all":
        for f in fns.values():
            f()
    else:
        fns[which]()
