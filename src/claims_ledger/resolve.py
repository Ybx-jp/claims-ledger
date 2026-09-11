"""Every pointer in every entry resolves to the artifact that established the fact, and
every quotation is a contiguous span of the source it names.

Two halves. `resolve_pointer` takes the grounds and the verdict evidence: an evidence
path at its pin, an `entry:` id, a `source:` row, a `search:` block. `check_quote` takes
the Backing: the source's bytes, and each quoted span found in them. `Sources` holds the
registry between them, `check_retraction` reads a retracted entry's defect instead of its
quotes, and the rule each of those keeps is stated where it is kept.

Run:  claims-ledger resolve
Exit 1 on any failure; flags print and exit 0.
Proven against the red-team corpus by `claims-ledger corpus`.
"""

from __future__ import annotations

import re

from .authoring import is_committed
from .freshness import effective_pointer, literal
from .schema import (
    NULL_OBJECT_ID,
    OBJECT_ID_RE,
    PENDING_ANCHOR,
    UNPINNED,
    Report,
    blob_text,
    by_id,
    digest_of,
    git,
    git_blobs,
    git_call,
    git_env,
    git_problem,
    load_entries,
    load_registry,
    normalize,
    normalize_with_map,
    parse_quote,
    read_document,
    section_span,
    section_text,
    source_bytes,
)

SENTENCE_END = ".!?"


class Sources:
    """Registry rows and their bytes, loaded once per run.

    A source id the registry does not have is answered with a problem rather than with
    nothing: the pointer that named it fails, saying the check could not run
    (L0035-a-registry-miss-fails-rather-than-passing, cites-as-live).
    """

    def __init__(self, ledger):
        self.ledger = ledger
        self.rows = load_registry(ledger.registry)
        self._texts = {}

    def text(self, source_id):
        """(nfc text, problem) for a registry id."""
        if source_id not in self._texts:
            row = self.rows.get(source_id)
            if row is None:
                self._texts[source_id] = (
                    None,
                    f"source id {source_id} has no registry row; the check cannot run",
                )
            else:
                self._texts[source_id] = source_bytes(row, self.ledger)
        return self._texts[source_id]

    def surnames_elsewhere(self, source_id):
        """Author surnames from every other registry row that names authors."""
        names = []
        for rid, row in self.rows.items():
            if rid != source_id:
                names += [(n, rid) for n in row.get("authors", [])]
        return names


def pinned_evidence(entry, config):
    """The pointers of an entry that are read out of git rather than off the disk. An
    anchor stated by value is not one: it is read from the tree, and asks the history
    only if the tree no longer holds its text and there is a history to ask."""
    pointers = [p for _, p in entry.grounds] + [v.pointer for v in entry.verdicts]
    return [
        p
        for p in pointers
        if p is not None
        and p.type in config.evidence_types
        and p.pin not in UNPINNED
        and not p.by_value
    ]


# A pin written as a bare object name, which is what `freshness --write` and the authoring
# commands produce. Only these are candidates for the rewritten-history reading: a hex name
# git does not have may be a commit that is gone, where `HEAD@{99}` or a deleted branch is a
# revision expression that never named one here.
OBJECT_NAME = re.compile(r"\A[0-9a-f]{7,40}\Z")


def why_not(ledger, p):
    """Why an evidence pointer did not resolve, in terms of what git was actually asked.

    `git show <pin>:<path>` fails for unrelated reasons and says the same thing for all of
    them, which left the checker reporting the symptom and never the cause. The commit that
    vanishes under a squashed, rebased or force-pushed history is the expensive one — every
    ground pinned into it fails at once, and the repair is a supersession per entry — so it
    is worth asking to name it rather than leaving a person to compare object ids by eye.

    Every question here goes through `git_call` and not `git()`, and the difference is the
    whole of this function's honesty. `git()` folds `no` and `could not answer` into one
    None, and a diagnosis built on that folding states as fact what it never established:
    a git broken only in `show` passes the `unasked` gate in `run()` — which asks
    `rev-parse --git-dir` and nothing more — and would be told, of a healthy commit and a
    present path, that the path is not in it. So the cases where git failed to answer are
    named as that (L0031-a-diagnosis-separates-a-no-from-an-unanswered-question,
    cites-as-live), and the rewritten-history reading is reached only after the object is
    known to be absent, the pin is known to be an object name, the name is not a prefix of
    several, and the clone is not shallow
    (L0032-a-rewritten-history-is-the-last-reading, cites-as-live). A shallow clone has no
    object for a commit that is perfectly well upstream, which is the same silence a
    rewrite leaves behind.
    """
    if p.pin in UNPINNED:
        return (
            f"the pin names no revision, so {p.target} is read from the working tree, where "
            "it is not a readable file"
        )
    repo = ledger.repo or ledger.tree
    obj = git_call(repo, "cat-file", "-t", p.pin)
    if obj.ok:
        kind = obj.out.strip()
        if kind != "commit":
            return f"{p.pin} is a {kind}, not a commit"
        blob = git_call(repo, "cat-file", "-e", f"{p.pin}:{p.target}")
        if blob.ok:
            return (
                f"git has that commit and has {p.target} in it, and still did not return the "
                "content; that is git failing to answer rather than a pointer that is wrong"
            )
        if blob.code is None:
            return f"the commit is there and git could not be asked for {p.target} ({blob.why})"
        return f"the commit is there and {p.target} is not in it"
    if obj.code is None:
        return f"git could not be asked what {p.pin} is ({obj.why})"
    if not OBJECT_NAME.match(p.pin):
        return f"git cannot resolve {p.pin} to an object in this repository"
    # `--disambiguate` and not the error text: git's last stderr line for an ambiguous
    # prefix is `fatal: Not a valid object name`, the same line it prints for one that is
    # simply absent — the candidates go to earlier `hint:` lines that `git_call` drops.
    # Keying on the wording would have left this branch dead and sent an ambiguous pin to
    # the rewritten-history reading, which is the one thing it must not say. This command
    # answers with the names themselves: none for absent, several for ambiguous.
    names = git_call(repo, "rev-parse", f"--disambiguate={p.pin}")
    if names.ok and len(names.out.split()) > 1:
        return f"{p.pin} is a prefix of more than one object here, so it names none of them"
    if (git(repo, "rev-parse", "--is-shallow-repository") or "").strip() == "true":
        return (
            "this repository does not have that object, and it is a shallow clone, where a "
            "commit outside the graft boundary cannot be told apart from one that was never "
            "here; deepen the clone before reading this as a rewritten history"
        )
    return (
        "this repository has no such commit; a squashed, rebased or force-pushed history "
        "drops the commit a pin names, and every ground pinned into it fails at once — "
        "docs/OPERATING.md says what that costs and how it is repaired"
    )


def resolve_pointer(p, e, part, index, sources, ledger, unasked=None):
    """Reports for one typed pointer; empty when it resolves. `unasked` is why git could
    not be asked at all, in which case a pinned pointer is left unjudged: `run()` has
    already said so once, for the ledger
    (L0030-an-unaskable-git-is-reported-once-for-the-ledger, cites-as-live).

    An unpinned evidence path is read off the disk, and a file that is not readable UTF-8
    is a pointer that does not resolve rather than a traceback out of the checker
    (L0033-an-unreadable-evidence-file-is-an-unresolved-pointer, cites-as-live).

    A pointer naming a section resolves only when that section is present in the text
    read at the pin, so a ground whose section was deleted under it fails here rather
    than being read as satisfied
    (L0034-a-sections-presence-is-checked-at-the-pin, cites-as-live).
    """
    out = []
    fail = lambda msg: out.append(Report("fail", e.prefix, part, msg))  # noqa: E731
    if p.type in ledger.config.evidence_types:
        if p.pin in UNPINNED:
            path = ledger.tree / p.target
            # read_document, not read_text: an evidence file that is unreadable or not
            # UTF-8 is a pointer that does not resolve, reported below, never a crash.
            text = read_document(path)[0] if path.is_file() else None
        elif unasked:
            return out
        else:
            # `git show <pin>:<path>` reads the path from the repository's root, so the
            # question goes to the repository holding the entries rather than to the
            # project root. They are the same directory in a real project; in a corpus
            # history seed the repository is built in a temporary directory.
            text = git(ledger.repo or ledger.tree, "show", f"{p.pin}:{p.target}")
        if text is None:
            fail(f"{p.type}: {p.target} @{p.pin} does not resolve: {why_not(ledger, p)}")
        elif p.section and section_span(text, ledger.config, p.type, p.section) is None:
            fail(f"{p.target} @{p.pin} has no section {p.section!r}")
    elif p.type == "entry":
        if p.target not in index:
            fail(f"entry: {p.target} does not exist")
    elif p.type == "source":
        _, problem = sources.text(p.target)
        if problem:
            fail(problem)
    elif p.type == "search":
        if not all(p.fields.get(k) for k in ("corpus", "query", "date")):
            fail("search: needs corpus=, query= and date=")
    return out


def digest_in_tree(ledger, p, cached=False):
    """(whether the tree this run reads holds the text the anchor names, or None when the
    path is not a readable file there, why not).

    The index under `--cached`, read through git as `freshness` reads it, and the working
    tree otherwise. The hook runs `check --cached`, and a read of the working tree there
    answered for a file the author had staged in one state and left in another: the
    anchor matched the tree, the commit carried the index, and the entry landed with an
    anchor no version of the path holds — D64's end state with no rewrite anywhere.
    """
    where = "the index" if cached else "the working tree"
    if cached:
        answer = git_call(
            ledger.repo or ledger.tree, "show", f":{p.target}", env=git_env(index=True)
        )
        if not answer.ok:
            return None, f"{p.target} could not be read from the index ({answer.why})"
        text = answer.out
    else:
        path = ledger.tree / p.target
        if not path.is_file():
            return None, f"{p.target} is not a readable file in {where}"
        text, problem = read_document(path)
        if text is None:
            return None, f"{p.target} {problem}"
    found = section_text(text, ledger.config, p.type, p.section) if p.sectioned else text
    if found is None:
        return None, f"{p.target} has no section {p.section!r} in {where}"
    return digest_of(found) == p.digest, None


def digest_in_history(ledger, p):
    """(whether some version of the path this repository holds digests to the anchor, why
    git could not say).

    Every version the path has ever held, on any ref, with full history, read through one
    `cat-file --batch`; the section is found in each the way the comparison finds it, and
    the first that digests to the anchor is the text the ground was established on. Only
    asked once the tree no longer holds that text, which is the ordinary case for a
    ground that has moved and not yet been re-read, and the extraordinary one for a
    ground whose founding commit a rewritten history dropped. A shallow clone has no
    object for a version that is perfectly well upstream, so an empty search there is
    reported as one that could not be made rather than as text that is gone
    (L0206-the-search-for-an-anchors-text-reads-every-version-git-holds, cites-as-live).
    """
    repo = ledger.repo
    if repo is None:
        return None, "there is no repository whose history could be searched"
    log = git_call(
        repo,
        "log",
        "--all",
        "--format=",
        "--raw",
        "--no-abbrev",
        "--full-history",
        "--",
        literal(p.target),
    )
    if not log.ok:
        return None, f"git could not list the versions of {p.target} ({log.why})"
    ids = set()
    for line in log.out.splitlines():
        if line.startswith(":"):
            ids |= {tok for tok in line.split() if OBJECT_ID_RE.match(tok)}
    ids.discard(NULL_OBJECT_ID)
    blobs, failures = git_blobs(repo, sorted(ids))
    for data in blobs.values():
        text = blob_text(data)
        found = section_text(text, ledger.config, p.type, p.section) if p.sectioned else text
        if found is not None and digest_of(found) == p.digest:
            return True, None
    if failures:
        why = next(iter(failures.values()))
        return None, f"git could not hand over every version of {p.target} ({why})"
    if (git(repo, "rev-parse", "--is-shallow-repository") or "").strip() == "true":
        return None, (
            "this repository is a shallow clone, and a version outside the graft boundary "
            "cannot be searched; deepen the clone before reading this as text that is gone"
        )
    return False, None


def resolve_by_value(p, e, part, ledger, committed, unasked=None, cached=False):
    """Reports for a ground whose anchor is stated by value; empty when it resolves.

    `p` is the pointer the ground is compared from — the ground itself, or the latest
    reading that re-read it — because what a person needs to be able to read is the text
    the claim currently rests on, and a founding text that a later reading has moved past
    is history.

    While the entry is not yet committed, the anchor has to digest to the section as the
    tree has it: the hook is the moment a mistyped or stale digest can still be fixed,
    `sha --write` recomputes it, and an anchor naming text the tree does not hold would
    otherwise be flagged as moved on the entry's first run and discharged by a reading
    of text nobody established a claim on. Once the entry is committed, the text may
    have moved on, and the anchor resolves when that text is still in the tree or in any
    version of the path this repository holds; when it is in neither, the ground is
    flagged rather than failed — the datum is stated in full and is compared exactly as
    before, and what is lost is the diff a person would read, which a rewritten history
    drops and a reading of the section as it now stands moves the ground past
    (L0211-an-anchor-by-value-resolves-to-text-this-run-reads-or-in-history,
    cites-as-live). `committed` is `(whether git has the entry, why it could not say)`.
    """
    out = []
    held, why = digest_in_tree(ledger, p, cached)
    if held:
        return out
    is_committed_, unanswered = committed
    if unanswered is not None and unasked:
        return out  # git could not be asked at all, and `run()` has said so once
    if unanswered is not None:
        out.append(
            Report(
                "fail",
                e.prefix,
                part,
                f"`{p.raw}` was not resolved: whether {e.id} is committed could not be "
                f"established ({unanswered})",
            )
        )
        return out
    if not is_committed_:
        where = "the index" if cached else "the working tree"
        reason = why or (
            f"{p.target} holds section {p.section!r} with a different digest"
            if p.sectioned
            else f"{p.target} has a different digest"
        )
        out.append(
            Report(
                "fail",
                e.prefix,
                part,
                f"`{p.raw}` names text {where} does not hold: {reason}; the entry is not "
                "committed, and `claims-ledger sha --write` recomputes its anchors",
            )
        )
        return out
    found, could_not = digest_in_history(ledger, p)
    if found:
        return out
    if found is None:
        out.append(Report("fail", e.prefix, part, f"`{p.raw}` was not resolved: {could_not}"))
        return out
    out.append(
        Report(
            "flag",
            e.prefix,
            part,
            f"`{p.raw}`: no version of {p.target} this repository holds digests to the "
            "anchor, so the text this ground was established on cannot be shown; a "
            "rewritten history drops it, and a reading of the section as it now stands "
            "moves the ground past it",
        )
    )
    return out


def sentence_bounds(text):
    """Positions where sentences end in `text`, ignoring the period of `et al.`: the
    window the relayed-material flag reads would otherwise stop at the abbreviation, and
    the authority being relayed is what follows it
    (L0040-et-als-period-does-not-end-a-sentence, cites-as-live).
    """
    ends = []
    for m in re.finditer(r"[.!?]", text):
        if text[max(0, m.start() - 5) : m.start()].endswith("et al"):
            continue
        ends.append(m.end())
    return ends


def check_quote(e, b, sources, quiet=False):
    """Reports for one Backing block. With `quiet` the reports are returned but the
    relayed-speaker flag is not raised (used when reproducing a retraction's defect).

    A consultation-type source backs only its own expert's judgment: the block's speaker
    must be the speaker the registry records, and a relayed result resolves to the
    primary source or not at all
    (L0038-a-consultation-backs-only-its-experts-own-judgment, cites-as-live).

    Each span is looked for from the end of the one before it, so a quote is a forward
    walk of its source and cannot be assembled out of order
    (L0036-quoted-spans-are-found-in-source-order, cites-as-live). A span that begins or
    ends inside a sentence with no elision mark on that side is a quotation that reads as
    more complete than it is, and it fails
    (L0037-a-quote-cut-mid-sentence-carries-an-elision-mark, cites-as-live).

    A consultation quote that verified is then read for who else it names: a sentence
    holding another registered author's surname, or `et al.`, is flagged as material the
    expert may be relaying rather than judging
    (L0039-a-consultation-sentence-naming-another-author-is-flagged, cites-as-live).
    """
    out = []
    part = b.part
    fail = lambda msg: out.append(Report("fail", e.prefix, part, msg))  # noqa: E731
    row = sources.rows.get(b.source_id)
    text, problem = sources.text(b.source_id)
    if problem:
        fail(problem)
        return out
    if row.get("type") == "consultation" and b.speaker != row.get("speaker"):
        fail(
            f"a consultation-type source backs only its expert's own judgment: speaker is "
            f"`{b.speaker}`, the registry says `{row.get('speaker')}`; a relayed result resolves "
            "to the primary source or not at all"
        )
        return out
    quote = parse_quote(b.quote)
    if quote is None:
        fail("quote: is not quoted spans separated by […]")
        return out

    nfc, norm, idx = normalize_with_map(text)
    pos = 0
    located = []
    for k, span in enumerate(quote.spans, start=1):
        needle = normalize(span)
        p = norm.find(needle, pos)
        if p < 0:
            where = "" if k == 1 else f" after span {k - 1}"
            fail(
                f"span {k} is not a contiguous span of {b.source_id}{where}: {span[:60]!r}…"
                if len(span) > 60
                else f"span {k} is not a contiguous span of {b.source_id}{where}: {span!r}"
            )
            return out
        start, end = idx[p], idx[p + len(needle) - 1] + 1
        located.append((start, end))
        pos = p + len(needle)

    first_start, _ = located[0]
    _, last_end = located[-1]
    if not quote.lead_elided:
        before = nfc[:first_start]
        gap = before[len(before.rstrip()) :]
        prev = before.rstrip()[-1:] if before.strip() else ""
        # The closing-quote case is the exception: `… said."` ends a sentence even though
        # the last character is the quotation mark rather than the stop.
        if (
            prev
            and prev not in SENTENCE_END
            and "\n\n" not in gap
            and prev not in '"“'
            and not (prev in '"”)' and before.rstrip()[-2:-1] in SENTENCE_END)
        ):
            fail("the quote starts inside a sentence with no elision mark on that side")
    if not quote.trail_elided:
        last_char = quote.spans[-1].rstrip()[-1:]
        after = nfc[last_end:]
        gap = after[: len(after) - len(after.lstrip())]
        nxt = after.lstrip()[:1]
        if last_char not in SENTENCE_END and nxt and nxt not in SENTENCE_END and "\n\n" not in gap:
            fail(
                f"the quote ends at {quote.spans[-1].split()[-1]!r}, inside a sentence, with no "
                "elision mark on that side"
            )
    if out or quiet or row.get("type") != "consultation":
        return out

    ends = sentence_bounds(nfc)
    for k, (start, end) in enumerate(located, start=1):
        s_start = max([x for x in ends if x <= start], default=0)
        s_end = min([x for x in ends if x >= end], default=len(nfc))
        sentence = nfc[s_start:s_end]
        named = [
            (n, rid)
            for n, rid in sources.surnames_elsewhere(b.source_id)
            if re.search(rf"\b{re.escape(n)}\b", sentence)
        ]
        if re.search(r"\bet al\b", sentence):
            named.append(("et al.", "an unregistered source"))
        if named:
            who = ", ".join(f"{n} ({rid})" for n, rid in named)
            out.append(
                Report(
                    "flag",
                    e.prefix,
                    part,
                    f"the source sentence containing span {k} names {who}; the expert may "
                    "be attributing the result onward, and relayed material resolves to "
                    "the primary source",
                )
            )
    return out


def check_retraction(e, sources):
    """On a retracted entry, the defect the verdict states must reproduce: the Backing
    quote the verdict names is re-checked, and a quote that still verifies is flagged,
    because a retraction resting on a defect that is not there is one a reader cannot
    confirm (L0041-a-retraction-must-reproduce-its-defect, cites-as-live).
    """
    out = []
    for v in e.verdicts:
        if v.status != "retracted" or not v.pointer or v.pointer.type != "defect":
            continue
        part = f"verdict {v.index}"
        m = re.search(r"Backing quote (\d+)", v.pointer.target)
        if not m:
            out.append(
                Report(
                    "flag",
                    e.prefix,
                    part,
                    "the stated defect names no Backing quote, so this checker cannot "
                    "reproduce it; a human confirms the retraction",
                )
            )
            continue
        n = int(m.group(1))
        block = next((b for b in e.backing if b.index == n), None)
        if block is None:
            out.append(
                Report(
                    "flag",
                    e.prefix,
                    part,
                    f"the stated defect names Backing quote {n}, which the entry does not have",
                )
            )
            continue
        if not check_quote(e, block, sources, quiet=True):
            out.append(
                Report(
                    "flag",
                    e.prefix,
                    part,
                    f"the retraction names Backing quote {n} as the defect, but the quote "
                    f"verifies as a contiguous span of {block.source_id}; the stated "
                    "defect does not reproduce",
                )
            )
    return out


def run(ledger, entries=None, cached=False):
    entries = load_entries(ledger) if entries is None else entries
    index = by_id(entries)
    sources = Sources(ledger)
    reports = []
    # A pinned pointer is read out of git, and `git()` answers None both for a pin that
    # is not there and for a git that could not be asked. Read as the first, a git that
    # is not on PATH turns every pinned pointer in the ledger into `does not resolve` — a
    # diagnosis of the pointer for a question nobody put, and a person sent to look at
    # pins that are perfectly good. Asked once, for the ledger, and the pinned pointers
    # are then left unjudged rather than blamed.
    unasked = None
    if any(pinned_evidence(e, ledger.config) for e in entries):
        unasked = git_problem(ledger.repo or ledger.tree)
    if unasked:
        reports.append(
            Report(
                "fail",
                None,
                "Grounds",
                f"{unasked}, so the pinned pointers were not read out of git; whether "
                "each still names its artifact is unknown, not settled",
            )
        )
    for e in entries:
        committed = None
        for i, (_, p) in enumerate(e.grounds, start=1):
            if p is None:
                continue
            if p.type in ledger.config.evidence_types and p.by_value:
                if p.digest == PENDING_ANCHOR:
                    # Names no datum yet; `validate` refuses it, and there is no text to
                    # look for in the tree or in history.
                    continue
                # Resolved from where the ground is compared from, and only once it is
                # known whether the entry is committed, which is asked once per entry.
                if committed is None:
                    committed = is_committed(ledger.repo, e.path)
                q, _ = effective_pointer(e, p, ledger.config, ledger.repo)
                reports += resolve_by_value(
                    q, e, f"Grounds {i}", ledger, committed, unasked, cached=cached
                )
                continue
            reports += resolve_pointer(p, e, "Grounds", index, sources, ledger, unasked)
        for v in e.verdicts:
            p = v.pointer
            if p is None or p.type == "defect":
                continue
            if p.type in ledger.config.evidence_types and p.by_value:
                # A reading's evidence is a dated act, and its digest is the datum it read,
                # stated in full; `validate` holds it to a shape and `freshness` compares
                # the latest one, so there is nothing here to read it out of.
                continue
            reports += resolve_pointer(p, e, f"verdict {v.index}", index, sources, ledger, unasked)
        if e.status() == "retracted":
            reports += check_retraction(e, sources)
        else:
            for b in e.backing:
                reports += check_quote(e, b, sources)
    return reports
