"""Every pointer in every entry resolves to the artifact that established the fact, and
every quotation is a contiguous span of the source it names.

Grounds and verdict evidence: an evidence path exists at its pin and names a section
that is there; an `entry:` id exists; a `source:` id has a registry row; a `search:`
block is complete. Backing: the source's bytes are present and hash to the registry row;
each quoted span is found in the source after the same normalization the fingerprint
uses, spans in source order; a span that starts or ends inside a sentence carries the
elision mark on that side; a consultation-type source's speaker is its expert, and a
consultation sentence that names another registered author or `et al.` is flagged as
relayed third-party material. A retracted entry's quotes are not re-reported; instead
the defect its verdict states must reproduce.

A cache or registry miss never passes silently: it is a failure that says the check
could not run.

Run:  claims-ledger resolve
Exit 1 on any failure; flags print and exit 0.
Proven against the red-team corpus by `claims-ledger corpus`.
"""

from __future__ import annotations

import re

from .schema import (
    UNPINNED,
    Report,
    by_id,
    git,
    load_entries,
    load_registry,
    normalize,
    normalize_with_map,
    parse_quote,
    read_document,
    source_bytes,
)

SENTENCE_END = ".!?"


class Sources:
    """Registry rows and their bytes, loaded once per run."""

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


def resolve_pointer(p, e, part, index, sources, ledger):
    """Reports for one typed pointer; empty when it resolves."""
    out = []
    fail = lambda msg: out.append(Report("fail", e.prefix, part, msg))  # noqa: E731
    if p.type in ledger.config.evidence_types:
        if p.pin in UNPINNED:
            path = ledger.tree / p.target
            # read_document, not read_text: an evidence file that is unreadable or not
            # UTF-8 is a pointer that does not resolve, reported below, never a crash.
            text = read_document(path)[0] if path.is_file() else None
        else:
            # `git show <pin>:<path>` reads the path from the repository's root, so the
            # question goes to the repository holding the entries rather than to the
            # project root. They are the same directory in a real project; in a corpus
            # history seed the repository is built in a temporary directory.
            text = git(ledger.repo or ledger.tree, "show", f"{p.pin}:{p.target}")
        if text is None:
            fail(f"{p.type}: {p.target} @{p.pin} does not resolve")
        elif p.section and not re.search(rf"^#+\s*{re.escape(p.section)}\s*$", text, re.MULTILINE):
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


def sentence_bounds(text):
    """Positions where sentences end in `text`, ignoring the period of `et al.`."""
    ends = []
    for m in re.finditer(r"[.!?]", text):
        if text[max(0, m.start() - 5) : m.start()].endswith("et al"):
            continue
        ends.append(m.end())
    return ends


def check_quote(e, b, sources, quiet=False):
    """Reports for one Backing block. With `quiet` the reports are returned but the
    relayed-speaker flag is not raised (used when reproducing a retraction's defect)."""
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
    """On a retracted entry, the defect the verdict states must reproduce."""
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


def run(ledger):
    entries = load_entries(ledger)
    index = by_id(entries)
    sources = Sources(ledger)
    reports = []
    for e in entries:
        for _, p in e.grounds:
            if p is not None:
                reports += resolve_pointer(p, e, "Grounds", index, sources, ledger)
        for v in e.verdicts:
            p = v.pointer
            if p is not None and p.type != "defect":
                reports += resolve_pointer(p, e, f"verdict {v.index}", index, sources, ledger)
        if e.status() == "retracted":
            reports += check_retraction(e, sources)
        else:
            for b in e.backing:
                reports += check_quote(e, b, sources)
    return reports
