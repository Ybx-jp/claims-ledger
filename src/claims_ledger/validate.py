"""Every entry in the ledger is well-formed: schema, verbatim fingerprint, grade–grounds
consistency, a hypothesis's motivating entries and falsifier, verdict legality,
supersession both ways, and — when the ledger is in a git repository — immutability of
the region above the APPEND marker and append-only verdicts, checked over the whole
history so a commit that bypassed the hook is caught by the next run anywhere.

Run:  claims-ledger validate [--cached]
      --cached reads staged entries from the index instead of the working tree.
Exit 1 on any failure; flags print and exit 0.

Proven against the red-team corpus by `claims-ledger corpus`. A rule not exercised by a
seed there is not a rule this file is trusted to enforce.
"""

from __future__ import annotations

import itertools
import os
import re
from pathlib import Path

from .schema import (
    ABSENT,
    ACTS,
    APPEND,
    DECIMAL_RE,
    GRADES,
    ID_RE,
    KINDS,
    MEASURED_AND_ABOVE,
    NULL_OBJECT_ID,
    OBJECT_ID_RE,
    SCOPE_KEYS,
    SECTIONS,
    SHA_RE,
    STATUSES,
    TAIL_SECTIONS,
    TERMINAL,
    UNPINNED,
    VERDICT_ENTRY_ACTS,
    Report,
    blob_text,
    by_id,
    git_blobs,
    git_call,
    git_history,
    load_entries,
    normalize,
    parse_entry,
    parse_quote,
    parse_timestamp,
)

ABSENCE_WORDS = {"nobody", "neither", "first", "novel", "unique", "unprecedented"}
ABSENCE_PAIRS = (("no", "one"), ("not", "found"))
NO_FOLLOWERS = {"has", "have", "was", "were", "report", "reports"}


# The falsifier rule is a heuristic on the Warrant's wording, stated so a checker author
# implements what the seeds test: any word beginning `falsif`.
FALSIFIER_RE = re.compile(r"\bfalsif", re.IGNORECASE)


def is_absence_claim(text):
    """The heuristic stated in corpus/README.md: standalone trigger words, the phrases
    `no one` and `not found`, or `no` followed within the sentence by has/have/was/were/
    report/reports. Words are whitespace-delimited with edge punctuation stripped, so
    `no-refresh` is a name and contains no `no`."""
    for sentence in re.split(r"(?<=[.;!?])\s+", text):
        words = [w.strip(".,;:!?()\"'“”").lower() for w in sentence.split()]
        words = [w for w in words if w]
        if ABSENCE_WORDS & set(words):
            return True
        for i, w in enumerate(words):
            if any(
                (w, words[i + 1] if i + 1 < len(words) else None) == pair for pair in ABSENCE_PAIRS
            ):
                return True
            if w == "no" and NO_FOLLOWERS & set(words[i + 1 :]):
                return True
    return False


def check_frontmatter(e, entries, config):
    out = []
    fail = lambda part, msg: out.append(Report("fail", e.prefix, part, msg))  # noqa: E731
    f = e.front
    for part, msg in e.problems:
        if part == "frontmatter":
            fail("frontmatter", msg)

    ident = f.get("id", "")
    stem = e.path.stem
    if not ident:
        fail("filename and id", "no id")
    elif ident != stem:
        fail("filename and id", f"id `{ident}` does not match filename `{stem}`")
    m = ID_RE.match(ident or stem)
    if not m:
        fail("filename and id", f"`{ident or stem}` is not <letter><four digits>-<slug>")
    elif m.group(1) in config.archived_prefixes:
        fail("filename and id", f"series `{m.group(1)}` is an archived prefix and is skipped")

    if f.get("kind") not in KINDS:
        fail("frontmatter kind", f"kind `{f.get('kind')}` is not one of {list(KINDS)}")
    if parse_timestamp(f.get("stated")) is None:
        fail(
            "frontmatter stated",
            f"`{f.get('stated')}` is not ISO 8601 to the second with a UTC offset",
        )
    author = f.get("author", "")
    if not re.match(r"^[a-z][a-z0-9-]*$", author):
        fail("frontmatter author", f"author `{author}` is not a lowercase author name")
    if f.get("grade") not in GRADES:
        fail("frontmatter grade", f"grade `{f.get('grade')}` is not one of {list(GRADES)}")

    needs_credence = f.get("kind") in ("prediction", "hypothesis")
    credence = f.get("credence")
    if needs_credence and credence is None:
        fail("frontmatter credence", f"kind: {f.get('kind')} requires credence")
    if needs_credence and not f.get("resolves_when"):
        fail("frontmatter resolves_when", f"kind: {f.get('kind')} requires resolves_when")
    if not needs_credence and (credence is not None or f.get("resolves_when")):
        fail(
            "frontmatter credence",
            "credence and resolves_when are omitted for a claim, never guessed",
        )
    if credence is not None:
        if not DECIMAL_RE.match(str(credence).strip()):
            fail("frontmatter credence", f"credence `{credence}` is not a plain decimal number")
        else:
            value = float(credence)
            if not 0.0 <= value <= 1.0:
                fail("frontmatter credence", f"credence {value} is outside [0, 1]")

    sup = f.get("supersedes")
    if sup is None:
        fail("frontmatter supersedes", "no supersedes: line (`none` or an id)")
    elif sup != "none" and sup not in entries:
        fail("frontmatter supersedes", f"supersedes `{sup}`, which does not exist")

    declared = f.get("verbatim_sha", "")
    if not SHA_RE.match(declared):
        fail("frontmatter verbatim_sha", "verbatim_sha is not a 64-hex sha256")
    elif declared != e.computed_sha():
        fail(
            "frontmatter verbatim_sha",
            "declared verbatim_sha does not match the value computed from Scope and Backing",
        )
    return out


def check_sections(e, config):
    out = []
    fail = lambda part, msg: out.append(Report("fail", e.prefix, part, msg))  # noqa: E731
    expected = list(SECTIONS) + list(TAIL_SECTIONS)
    present = [s for s in e.section_order if s in expected]
    if present != expected:
        missing = [s for s in expected if s not in e.section_order]
        for s in missing:
            fail(s, "section missing")
        if not missing:
            fail("sections", f"sections out of order: {e.section_order}")
    for s in e.section_order:
        if s not in expected:
            fail(s, "not a section of the schema")
    if not e.has_append:
        fail("sections", f"missing the line `{APPEND}`")
    elif e.text.index(APPEND) < (e.text.find("## Backing") if "## Backing" in e.text else 0):
        fail("sections", "the APPEND marker must follow Backing and precede Verdicts")
    for part, msg in e.problems:
        if part != "frontmatter":
            fail(part, msg)

    assertion = e.assertion
    if not assertion:
        fail("Assertion", "empty")
    elif any(c in assertion for c in '"“”„«»'):
        fail("Assertion", "quotation marks are illegal in Assertion; source words live in Backing")

    scope = e.scope
    for ln in e.scope_text.splitlines():
        if ln.strip() and ln.split(":", 1)[0].strip() not in SCOPE_KEYS:
            fail("Scope", f"line {ln.strip()!r} is not metric:, cohort: or condition:")
    if e.grade in MEASURED_AND_ABOVE:
        for key in SCOPE_KEYS:
            if not scope.get(key):
                fail("Scope", f"grade {e.grade} requires a {key}: line")

    if not e.grounds:
        fail("Grounds", "no grounds; a Warrant needs something to rest on")
    for raw, p in e.grounds:
        if p is None or p.type not in config.ground_types:
            fail(
                "Grounds",
                f"`{raw}` is not a typed pointer ({'/'.join(config.ground_types)})",
            )
        elif p.type == "entry" and p.act not in ACTS:
            fail("Grounds", f"`{raw}` carries act `{p.act}`, not one of {list(ACTS)}")
        elif p.type in config.evidence_types and p.sectioned != config.is_sectioned(p.type):
            want = (
                f'{p.type}: <path> § "<section>" @<commit>'
                if config.is_sectioned(p.type)
                else f"{p.type}: <path> @<commit>"
            )
            fail("Grounds", f"`{raw}` is not written as `{want}`")
    kinds = {p.type for p in e.ground_pointers}
    evidence = kinds & set(config.evidence_types)
    if e.grade in MEASURED_AND_ABOVE and not evidence:
        fail(
            "frontmatter grade",
            f"{e.grade} requires a {' or '.join(config.evidence_types)} ground; "
            f"grounds are {sorted(kinds)}",
        )
    if e.grade == "asserted" and evidence:
        fail(
            "frontmatter grade",
            f"asserted forbids a {' or '.join(sorted(evidence))} ground; an observation "
            "is measured",
        )
    if is_absence_claim(assertion) and "search" not in kinds:
        fail(
            "Grounds",
            "the Assertion reads as an absence or priority claim and carries no search: ground",
        )

    if not e.sections.get("Warrant", "").strip():
        fail("Warrant", "empty")
    if e.front.get("kind") == "hypothesis":
        # A hypothesis is a bet on a design: it names the claims motivating it and says
        # what would falsify it, or the roster it feeds has nothing to test.
        if "entry" not in kinds:
            fail(
                "Grounds", "a hypothesis names the entries motivating it; there is no entry: ground"
            )
        if not FALSIFIER_RE.search(e.sections.get("Warrant", "")):
            fail(
                "Warrant",
                "a hypothesis states what would falsify it; no sentence here says `falsified if`, "
                "`falsifier` or the like",
            )

    for b in e.backing:
        if not b.source_id or "·" not in b.source:
            fail(b.part, "source: is `<registry id> · <locator>`")
        if not b.speaker:
            fail(b.part, "speaker: is empty")
        if parse_quote(b.quote) is None:
            fail(b.part, "quote: is not quoted spans separated by […]")

    for raw, r in e.references:
        if r is None:
            fail("References", f"`{raw}` is not `- <path> · standing | record · <act>`")
        elif r.act not in ACTS:
            fail("References", f"`{raw}` carries act `{r.act}`")
    return out


def check_verdicts(e, entries, config):
    out = []
    fail = lambda part, msg: out.append(Report("fail", e.prefix, part, msg))  # noqa: E731
    flag = lambda part, msg: out.append(Report("flag", e.prefix, part, msg))  # noqa: E731
    ground_keys = {normalize(raw) for raw, _ in e.grounds}
    stated = parse_timestamp(e.front.get("stated"))
    last = stated
    order_broken = False
    terminal, reinstated = None, False
    superseded_seen = 0

    for v in e.verdicts:
        part = f"verdict {v.index}"
        if v.malformed:
            fail(part, v.malformed)
            continue
        if v.status not in STATUSES or v.status == "open":
            fail(part, f"status `{v.status}` is not a verdict status")
            continue
        if v.grade not in GRADES:
            fail(part, f"grade `{v.grade}` is not one of {list(GRADES)}")
        if v.author not in config.verdict_authors:
            fail(
                part,
                f"author `{v.author}` is not one of {list(config.verdict_authors)}; "
                "a verdict is written by a named author and by nobody else",
            )
        ts = parse_timestamp(v.timestamp)
        if ts is None:
            fail(part, f"timestamp `{v.timestamp}` is not ISO 8601 to the second with a UTC offset")
        elif last is not None and ts < last:
            order_broken = True
        if ts is not None:
            last = max(last, ts) if last else ts

        p = v.pointer
        if v.evidence is None:
            fail(part, "no evidence: line")
        elif p is None:
            fail(part, f"evidence `{v.evidence}` is not a typed pointer")
        else:
            if (p.type == "defect") != (v.status == "retracted"):
                fail(part, "defect: is the evidence of a retracted verdict and of no other")
            if p.type == "entry" and p.act not in VERDICT_ENTRY_ACTS and p.act not in ACTS:
                fail(part, f"entry: evidence carries act `{p.act}`")
            # The two shapes the machinery writes: propagate's, naming the entry whose
            # fall or challenge caused the flag, and freshness's, naming the pinned
            # ground that moved or was withdrawn. Anything else under the machine's name
            # is a person borrowing the authority of a check that did not run.
            propagated = v.status == "contested" and (
                (p.type == "entry" and p.act in ("fallen", "challenges"))
                or (p.type in config.evidence_types and p.pin not in UNPINNED)
            )
            if v.author == config.propagation_author and not propagated:
                fail(
                    part,
                    "a propagation verdict is contested with entry: evidence · fallen or "
                    "· challenges, or an evidence ground carrying a pin; anything else was "
                    "written by a person under the machine's name",
                )
            if v.status == "superseded":
                if not (p.type == "entry" and p.act == "supersedes"):
                    fail(part, "a superseded verdict names its successor: entry: <id> · supersedes")
                else:
                    successor = entries.get(p.target)
                    if successor is None:
                        fail(part, f"names successor `{p.target}`, which does not exist")
                    elif successor.front.get("supersedes") != e.id:
                        fail(
                            part,
                            f"names successor `{p.target}`, whose supersedes: is "
                            f"`{successor.front.get('supersedes')}`; "
                            "discoverability runs both ways",
                        )
            if v.status == "corroborated" and normalize(v.evidence) in ground_keys:
                fail(
                    part,
                    "a corroborating verdict must point at a ground the entry does not "
                    "already cite",
                )
        # `artifact:` is machine provenance, and this is the only checker that looks at
        # its shape. `freshness` writes it and `orphans()` holds the verdict to it — but
        # `orphans()` asks only once the ground looks fresh again, so in the state a
        # discharge normally lives in, the drift still live, no code read the value at
        # all: a propagated verdict carrying forty zeros, a non-hash, or no `artifact:`
        # line silenced a real ongoing drift with every checker at exit 0. Well-formedness
        # is asked here instead, of every verdict, in every state, before git is asked
        # anything.
        records_drift = (
            v.author == config.propagation_author
            and v.status == "contested"
            and p is not None
            and p.type in config.evidence_types
            and p.pin not in UNPINNED
        )
        if records_drift:
            if v.artifact is None:
                fail(
                    part,
                    "no artifact: line; a propagated verdict over a pinned ground records "
                    "the object id the drift was seen at, or `absent` for a ground that "
                    "was gone, and a discharge that states no cause is one nothing can check",
                )
            elif v.artifact != ABSENT and not OBJECT_ID_RE.match(v.artifact):
                fail(
                    part,
                    f"artifact `{v.artifact}` is neither a 40-character object id nor `{ABSENT}`",
                )
            elif v.artifact == NULL_OBJECT_ID:
                # Well-formed and naming nothing. Git's null object id is forty hex
                # characters no artifact has ever hashed to, so it passes the shape while
                # recording no artifact at all — and `blobs_since()` drops it from what
                # the path has held, so the value is one nothing can ever confirm.
                fail(part, "artifact is the null object id, which names no artifact")
        elif v.artifact is not None:
            # The other direction, and the one a person reaches for: `artifact:` on a
            # hand-written `corroborated` verdict is machine provenance nothing machine
            # produced. Stated as a shape rather than as an accusation, because the rule
            # cannot tell a person fabricating provenance from a verdict the machinery
            # really wrote under a `propagation-author` the configuration has since been
            # changed away from — and it said "claims a check that did not run" about
            # every tool-written verdict in the ledger after that one-line config edit.
            fail(
                part,
                "artifact: is recorded by `freshness --write` on a propagated verdict "
                "naming a pinned ground, and this verdict is not that shape; if the "
                "machinery wrote it, `propagation-author` no longer names its author",
            )
        if v.status == "non-comparable" and e.grade not in MEASURED_AND_ABOVE:
            fail(
                part, f"non-comparable is legal only at measured and above; this entry is {e.grade}"
            )
        if v.status == "refuted" and v.grade != e.grade and v.grade in GRADES:
            flag(
                part,
                f"refuted on {v.grade} evidence against a {e.grade} entry; evidence types are "
                "not ranked, so this is for review",
            )
        if v.status == "superseded":
            superseded_seen += 1
            if superseded_seen > 1:
                fail(part, "a second superseded verdict; supersession is a chain, not a tree")

        if terminal:
            if (
                terminal in ("refuted", "non-comparable")
                and v.status == "superseded"
                and not reinstated
            ):
                reinstated = True
            else:
                fail(
                    part,
                    f"follows a terminal `{terminal}` verdict; nothing may follow it"
                    + (
                        " except one superseded"
                        if terminal in ("refuted", "non-comparable")
                        else ""
                    ),
                )
        elif v.status in TERMINAL:
            terminal = v.status

    if order_broken:
        fail(
            "Verdicts",
            "verdict timestamps must be non-decreasing down the file and none earlier than stated",
        )
    return out


def check_supersession(e, entries):
    """The successor's side of a chain: its predecessor carries the final verdict naming
    it, and the verbatim record is unchanged unless verbatim_change says why."""
    out = []
    sup = e.front.get("supersedes")
    if not sup or sup == "none" or sup not in entries:
        return out
    pred = entries[sup]
    final = pred.superseded_verdicts()
    if not final:
        out.append(
            Report(
                "fail",
                pred.prefix,
                "Verdicts",
                f"{e.id} names supersedes: {pred.id} but {pred.id} carries no superseded verdict",
            )
        )
    else:
        named = {v.pointer.target for v in final if v.pointer and v.pointer.type == "entry"}
        if e.id not in named:
            out.append(
                Report(
                    "fail",
                    e.prefix,
                    "frontmatter supersedes",
                    f"{pred.id} is already superseded by {', '.join(sorted(named))}; "
                    "a second successor forks the chain",
                )
            )
    if e.computed_sha() != pred.computed_sha() and not e.front.get("verbatim_change"):
        out.append(
            Report(
                "fail",
                e.prefix,
                "frontmatter verbatim_sha",
                f"the verbatim record differs from {pred.id}'s and no verbatim_change is declared",
            )
        )
    return out


def _frozen_sections(text):
    e = parse_entry("x.md", text)
    parts = {"frontmatter": "\n".join(f"{k}: {v}" for k, v in e.front.items())}
    for s in SECTIONS:
        parts[s] = e.sections.get(s, "")
    return parts, e


def _frozen_region(text):
    """The bytes above the APPEND marker, or None when there is no marker to be above.

    The sections are what a report can name, but they are not the whole of what is
    frozen: a section runs from its own heading to the next, so every byte before the
    first heading belongs to no section and left the parsed comparison untouched. The
    scaffold leaves that region empty, which is what made it a hiding place — nothing
    legitimate is ever written there, so nothing legitimate ever changes there.
    """
    head, marker, _ = text.partition(APPEND)
    return head if marker else None


def _read_bytes(path):
    """The entry file's bytes, or None when it cannot be read. A file that will not read
    is `resolve`'s and the parser's finding; here it only means there is nothing to
    compare, and a comparison that did not happen is never reported as one that passed."""
    try:
        return Path(path).read_bytes()
    except OSError:
        return None


def _frozen_bytes(data):
    """The frozen region of an entry as raw bytes, or None when there is no marker."""
    if data is None:
        return None
    head, marker, _ = data.partition(APPEND.encode("utf-8"))
    return head if marker else None


def check_history(ledger, entries, cached=False):
    """Immutability, from git. For each entry file: the region above the APPEND marker
    equals the blob at the commit that created the file, and across every consecutive
    pair of revisions the verdict blocks only ever grow.

    Three git processes for the whole ledger — one to ask whether anything is committed,
    one walk of the history under the entries directory, one `cat-file --batch` for every
    blob the walk named — rather than two plus one per revision for each entry. The walk
    is the part that scaled worst: `git log -- <path>` visits every commit however few
    touched the path, so the old per-entry loop cost the product of entries and commits.
    """
    out = []
    if not ledger.repo:
        return out
    repo = ledger.repo
    # `git log` exits non-zero over a repository with no commits in it at all, which is
    # the ordinary state of a ledger being scaffolded and is not a failure to report. It
    # is also how a repository that cannot be read fails, so the two are separated once,
    # here, rather than collapsed into the empty revision list they both produce.
    committed_anything = git_call(repo, "rev-parse", "--verify", "--quiet", "HEAD").ok
    rels = [(e, os.path.relpath(e.path, repo)) for e in entries]
    # No --follow: it runs rename detection against every file in the parent, so a
    # successor written as a near-copy of a predecessor that is still in the tree is
    # reported as "renamed" from it, and the creating commit comes back as one where
    # this file did not exist (corpus K18). An entry is never renamed: its id is its
    # filename.
    history, why = git_history(repo, os.path.relpath(ledger.entries_dir, repo))
    if history is None:
        if committed_anything:
            for e, rel in rels:
                out.append(
                    Report(
                        "fail",
                        e.prefix,
                        "frontmatter",
                        f"cannot read the history of {rel} ({why}); the frozen-region and "
                        "append-only checks did not run over this entry",
                    )
                )
        return out
    revisions = {rel: list(reversed(history.get(rel, []))) for _, rel in rels}  # oldest first
    wanted = []
    for _, rel in rels:
        wanted += [f"{h}:{rel}" for h in revisions[rel]]
        if cached and revisions[rel]:
            wanted.append(f":{rel}")
    blobs, unread = git_blobs(repo, wanted)
    for e, rel in rels:
        revs = revisions[rel]
        if not revs:
            continue  # not yet committed: nothing to be immutable against
        creating = revs[0]
        original_bytes = blobs.get(f"{creating}:{rel}")
        if original_bytes is None:
            out.append(
                Report(
                    "fail",
                    e.prefix,
                    "frontmatter",
                    f"cannot read {rel} at {creating[:7]} ({unread[f'{creating}:{rel}']})",
                )
            )
            continue
        then, _ = _frozen_sections(blob_text(original_bytes))
        now, _ = _frozen_sections(e.text)
        named = False
        for name in then:
            if then[name].strip() != now[name].strip():
                named = True
                out.append(
                    Report(
                        "fail",
                        e.prefix,
                        name,
                        f"differs from the blob at the creating commit {creating[:7]}; the "
                        "region above the APPEND marker is immutable",
                    )
                )
        # And the same comparison again, on the bytes. Everything above reads both sides
        # as text, and text arrives here through universal newlines on both sides — the
        # blob is decoded that way above, `read_text` decodes — so a frozen region
        # rewritten from CRLF to LF compared equal to itself while every byte of it had
        # changed. "Immutable" means the bytes.
        then_bytes = _frozen_bytes(original_bytes)
        now_bytes = _frozen_bytes(blobs.get(f":{rel}") if cached else _read_bytes(e.path))
        if not named and None not in (then_bytes, now_bytes) and then_bytes != now_bytes:
            out.append(
                Report(
                    "fail",
                    e.prefix,
                    "the frozen region",
                    f"has the same text as the blob at the creating commit {creating[:7]} "
                    "and not the same bytes; the region above the APPEND marker is "
                    "immutable, line endings included",
                )
            )
        states = []
        for h in revs:
            data = blobs.get(f"{h}:{rel}")
            if data is None:
                out.append(
                    Report(
                        "fail",
                        e.prefix,
                        "Verdicts",
                        f"cannot read {rel} at {h[:7]} ({unread[f'{h}:{rel}']}); verdicts "
                        "append and only append, and across that revision it was not "
                        "checked that they did",
                    )
                )
            states.append((h, None if data is None else blob_text(data)))
        states.append(("working tree", e.text))
        for (h_old, t_old), (h_new, t_new) in itertools.pairwise(states):
            if t_old is None or t_new is None or t_old == t_new:
                continue  # a revision that could not be read is reported above, not waived
            old = [v.raw.rstrip() for v in parse_entry("x.md", t_old).verdicts]
            new = [v.raw.rstrip() for v in parse_entry("x.md", t_new).verdicts]
            label = h_new[:7] if h_new != "working tree" else h_new
            for i, block in enumerate(old, start=1):
                if i > len(new) or new[i - 1] != block:
                    out.append(
                        Report(
                            "fail",
                            e.prefix,
                            f"verdict {i}",
                            f"present at {h_old[:7]} and changed or removed at {label}; "
                            "verdicts append and only append",
                        )
                    )
                    break
    return out


def run(ledger, cached=False):
    entries = load_entries(ledger, cached=cached)
    index = by_id(entries)
    config = ledger.config
    reports = []
    for e in entries:
        reports += check_frontmatter(e, index, config)
        reports += check_sections(e, config)
        reports += check_verdicts(e, index, config)
        reports += check_supersession(e, index)
    reports += check_history(ledger, entries, cached=cached)
    return reports
