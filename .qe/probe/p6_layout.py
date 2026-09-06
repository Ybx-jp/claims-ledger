import sys, tempfile, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_helper import make
APPEND = "<!-- APPEND BELOW THIS LINE ONLY -->"

def build(tmp, mutate=None):
    p = make(tmp, git=False)
    assert p.cl("new","a-claim") == 0
    a = p.entry("A0001-a-claim.md"); p.write_full_entry(a)
    if mutate:
        a.write_text(mutate(a.read_text(encoding="utf-8")), encoding="utf-8")
        p.cl("sha","--write",str(a))
    assert p.cl("new","b-claim") == 0
    b = p.entry("A0002-b-claim.md")
    t = b.read_text(encoding="utf-8")
    t = t.replace("TODO: the claim, in this project's words. No quotation marks.","The first claim is unsupported.")
    t = t.replace("metric: TODO","metric: m").replace("cohort: TODO","cohort: c").replace("condition: TODO","condition: d")
    t = t.replace("- TODO: one typed pointer per line",'- lab: docs/note-001.md § "Observation" @working\n- entry: A0001-a-claim · challenges')
    t = t.replace("TODO: the rule by which the grounds support the assertion.","Because the grounds were withdrawn.")
    b.write_text(t, encoding="utf-8"); assert p.cl("sha","--write",str(b)) == 0
    p.git("init","-q"); p.git("add","-A"); p.git("commit","-qm","sealed")
    return p, a

def show(label, mutate):
    print("\n===", label, "===")
    p, a = build(Path(tempfile.mkdtemp()), mutate)
    print("check before:", p.cl("check"))
    before = a.read_text(encoding="utf-8")
    print("propagate --write rc:", p.cl("propagate","--write"))
    after = a.read_text(encoding="utf-8")
    fb, fa = before.split(APPEND,1)[0] if APPEND in before else before, after.split(APPEND,1)[0] if APPEND in after else after
    print("frozen region changed by the write:", fb != fa)
    print("check after:", p.cl("check"))

# 1: References heading appears inside Backing (a quoted document that has one)
def m1(t):
    return t.replace('  quote: "The error', '  quote: "The error').replace(
        "\n\n<!-- APPEND", "\n- source: fx-source · whole text\n  speaker: Okafor\n  quote: \"x\"\n\n<!-- APPEND")
# 2: References section placed above the APPEND marker
def m2(t):
    t = t.replace("\n## References\n", "\n")
    return t.replace("\n"+ "<!-- APPEND BELOW THIS LINE ONLY -->", "\n## References\n\n<!-- APPEND BELOW THIS LINE ONLY -->")
# 3: no References section at all
def m3(t):
    return t.replace("\n## References\n", "\n")

show("2: References above the APPEND marker", m2)
show("3: no References section", m3)
