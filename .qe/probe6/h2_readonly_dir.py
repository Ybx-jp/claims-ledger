"""Hypothesis 2: a WRITABLE file inside a NON-writable directory. Old code (truncating
open()) succeeded; new code needs to create a temp file beside the target, which needs
directory write permission. Is the diagnostic a clean exit 2 with a real message, or a
traceback / a misleading message?"""
import sys, tempfile, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make


def sha_write():
    print("\n--- sha --write: entry file writable, entries/ directory read-only ---")
    tmp = Path(tempfile.mkdtemp())
    p = make(tmp, git=False)
    assert p.cl("new", "a-claim") == 0
    a = p.entry("A0001-a-claim.md")
    p.write_full_entry(a)
    t = a.read_text(encoding="utf-8")
    t = t.replace("cohort: the synthetic graph of these tests", "cohort: edited")
    a.write_text(t, encoding="utf-8")
    before = a.read_bytes()
    os.chmod(a.parent, 0o555)  # r-xr-xr-x: entries/ not writable, file itself is 0o644
    try:
        import io, contextlib
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            try:
                rc = p.cl("sha", "--write", str(a))
                exc = None
            except BaseException as e:
                rc = None
                exc = e
    finally:
        os.chmod(a.parent, 0o755)
    print("rc:", rc, "exception escaped:", repr(exc) if exc else None)
    print("stdout:", buf_out.getvalue())
    print("stderr:", buf_err.getvalue())
    after = a.read_bytes()
    print("file unchanged:", before == after)
    # look for a leftover temp file that failed to be created/cleaned
    leftovers = [f.name for f in a.parent.iterdir() if "claims-ledger-" in f.name]
    print("leftover temp names:", leftovers)
    msg = (buf_out.getvalue() + buf_err.getvalue())
    misleading = "cannot write" in msg and "Permission denied" not in msg and exc is None
    print("message text:", msg.strip())


if __name__ == "__main__":
    sha_write()
