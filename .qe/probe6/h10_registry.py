"""Hypothesis 10: HIGH-40's fix (`source add` onto a registry with no final newline) --
also try: empty, all-whitespace, ends in \\r\\n, truncated mid-JSON, a symlink, a FIFO."""
import sys, tempfile, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make


def add_second(p, tmp, label):
    s2 = tmp / f"second-{label.replace(' ', '_')}.txt"
    s2.write_text(f"Another synthetic source for {label}.\n", encoding="utf-8")
    rc = p.cl("source", "add", str(s2), "--id", f"fx-{label.replace(' ', '-')}", "--type", "paper",
              "--citation", "Second", "--authors", "B")
    return rc


def case(label, mutate):
    print(f"\n=== {label} ===")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    reg = p.root / "ledger" / "sources.jsonl"
    mutate(reg)
    print("registry bytes before:", reg.read_bytes()[:80])
    rc = add_second(p, tmp, label)
    print("source add rc:", rc)
    content = reg.read_bytes()
    print("registry bytes after (last 120):", content[-120:])
    check_rc = p.cl("check")
    print("check rc:", check_rc)
    # parse-ability
    ok_lines = 0
    bad_lines = 0
    for ln in content.decode("utf-8", errors="replace").splitlines():
        if not ln.strip():
            continue
        try:
            import json
            json.loads(ln)
            ok_lines += 1
        except Exception:
            bad_lines += 1
    print(f"parseable lines: {ok_lines}, unparseable: {bad_lines}")


def m_empty(reg):
    reg.write_bytes(b"")


def m_whitespace(reg):
    reg.write_bytes(b"   \n\t\n  \n")


def m_crlf_end(reg):
    raw = reg.read_bytes()
    reg.write_bytes(raw.rstrip(b"\n") + b"\r\n")


def m_truncated_json(reg):
    raw = reg.read_bytes()
    # cut mid-object
    idx = raw.index(b'"citation"')
    reg.write_bytes(raw[:idx])


def m_symlink(reg):
    target = reg.parent / "sources.real.jsonl"
    target.write_bytes(reg.read_bytes())
    reg.unlink()
    os.symlink(target, reg)


def m_fifo(reg):
    reg.unlink()
    os.mkfifo(reg)


if __name__ == "__main__":
    case("empty registry", m_empty)
    case("all-whitespace registry", m_whitespace)
    case("registry ending in CRLF", m_crlf_end)
    case("registry truncated mid-JSON (no trailing newline either)", m_truncated_json)
    case("registry is a symlink to a real file", m_symlink)

    print("\n=== registry is a FIFO ===")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    reg = p.root / "ledger" / "sources.jsonl"
    reg.unlink()
    os.mkfifo(reg)
    import subprocess
    s2 = tmp / "second-fifo.txt"; s2.write_text("Another synthetic source.\n", encoding="utf-8")
    r = subprocess.run(
        ["claims-ledger", "--root", str(p.root), "source", "add", str(s2), "--id", "fx-fifo",
         "--type", "paper", "--citation", "Second", "--authors", "B"],
        capture_output=True, text=True, timeout=10,
    )
    print("source add rc:", r.returncode)
    print("stdout:", r.stdout.strip())
    print("stderr:", r.stderr.strip())
