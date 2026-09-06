import subprocess, sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests"))
from conftest import Project, LAB_NOTE, SOURCE_TEXT  # noqa

def make(tmp: Path, git=True):
    root = tmp / "project"; root.mkdir(parents=True)
    p = Project(root)
    assert p.cl("init") == 0
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs" / "note-001.md").write_text(LAB_NOTE, encoding="utf-8")
    src = tmp / "source.txt"; src.write_text(SOURCE_TEXT, encoding="utf-8")
    assert p.cl("source","add",str(src),"--id","fx-source","--type","paper",
                "--citation","A synthetic source (these tests)","--authors","Okafor") == 0
    if git:
        p.git("init")
    return p
