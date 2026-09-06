import sys, tempfile, os, resource, signal, subprocess, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make

MODE = sys.argv[1] if len(sys.argv) > 1 else "setup"

if MODE == "setup":
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new","a-claim") == 0
    path = p.entry("A0001-a-claim.md")
    p.write_full_entry(path)
    assert p.cl("new","b-claim") == 0
    b = p.entry("A0002-b-claim.md")
    t = b.read_text(encoding="utf-8")
    t = t.replace("TODO: the claim, in this project's words. No quotation marks.","The first claim is unsupported.")
    t = t.replace("metric: TODO","metric: m").replace("cohort: TODO","cohort: c").replace("condition: TODO","condition: d")
    t = t.replace("- TODO: one typed pointer per line",'- lab: docs/note-001.md § "Observation" @working\n- entry: A0001-a-claim · challenges')
    t = t.replace("TODO: the rule by which the grounds support the assertion.","Because the grounds were withdrawn.")
    b.write_text(t, encoding="utf-8")
    assert p.cl("sha","--write",str(b)) == 0
    p.git("init","-q"); p.git("add","-A"); p.git("commit","-qm","sealed")
    size = path.stat().st_size
    print("SETUP", tmp, "entry bytes:", size)
    limit = size + 40
    env = dict(os.environ, PROBE_LIMIT=str(limit))
    r = subprocess.run([sys.executable, __file__, "child", str(p.root)], env=env, capture_output=True, text=True)
    print("child rc", r.returncode)
    print("child stdout:", r.stdout[-2000:])
    print("child stderr:", r.stderr[-2000:])
    now = path.stat().st_size
    print("entry bytes after:", now)
    txt = path.read_text(encoding="utf-8", errors="replace")
    print("has APPEND:", "<!-- APPEND BELOW THIS LINE ONLY -->" in txt)
    print("tail:", repr(txt[-120:]))
    print("check rc after crash:", p.cl("check"))
else:
    root = sys.argv[2]
    signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
    lim = int(os.environ["PROBE_LIMIT"])
    resource.setrlimit(resource.RLIMIT_FSIZE, (lim, lim))
    from claims_ledger import cli
    sys.exit(cli.main(["--root", root, "propagate", "--write"]))
