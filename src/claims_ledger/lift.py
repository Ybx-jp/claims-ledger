"""Lifting narrative prose out of an artifact and onto the entry that rests on it.

The prose a project writes about its own code is a commitment in words; the entry is
where a commitment lives. `lift` moves the words and leaves the citation, so the section
holds the code and a line saying where the rest of it went, and `show` reads it back.

Run:  claims-ledger lift <entry id> [--ground N] [--write] [--patch <file>]
      claims-ledger show <entry id>
Nothing is written without `--write`; the default run says what it would do.

What keeps it honest is stated at `refuse_unless_git_holds_it`, where it is kept: the
package already rewrites a project's source in `renumber --write`, which is licensed by
an invariant this command cannot inherit, so the lift carries its own.
"""

from __future__ import annotations

import re

from .schema import (
    ACT_ALLOWS,
    CITATION_RE,
    PASSAGE_INDENT,
    LedgerError,
    digest_of,
    git_call,
    git_env,
    section_span,
    selects_document,
)

DOCSTRING_RE = re.compile(r'^(?P<indent>[ \t]*)(?P<quote>"""|\'\'\')', re.MULTILINE)


class LiftError(LedgerError):
    """A lift that will not be attempted, said in terms of the thing to fix."""


def refuse_unless_git_holds_it(repo, rel, text):
    """Raise unless HEAD holds `rel` with exactly `text`.

    `renumber --write` may rewrite a project's files because undoing its substitution
    reproduces what was there; a lift deletes, and nothing reconstructs a deletion from
    the file it left behind. What stands in for reversibility is that the bytes being
    removed are already in git before they are removed, so the witness has something to
    resolve against and a person has something to restore from. A lift from a dirty file
    would put prose on an entry that no commit ever held
    (L0269-a-lift-refuses-what-git-does-not-already-hold, cites-as-live).
    """
    if repo is None:
        raise LiftError(f"{rel}: there is no repository, so nothing holds the prose being lifted")
    got = git_call(repo, "show", f"HEAD:{rel}", env=git_env())
    if not got.ok:
        raise LiftError(
            f"{rel}: HEAD does not hold this file ({got.why}); commit it before lifting"
        )
    if got.out.replace("\r\n", "\n").replace("\r", "\n") != text:
        raise LiftError(
            f"{rel}: the working tree differs from HEAD; commit or stash the change before "
            "lifting, so the witness names bytes git already holds"
        )


def liftable(section):
    """[(start, stop)] over `section` for each contiguous run of docstring body that can
    be lifted, or None when there is none to take.

    A run and not the whole body, because a citation line stops one and starts the next.
    Measured on this repository, taking only the run before the first citation reached
    765 of 1275 docstring body lines (60%) where taking every run reaches 1115 (87%);
    each run is still contiguous in the artifact, which is what the passage is compared
    against, so nothing is given up by taking them all.

    The summary line stays. PEP 257 already separates a one-line summary from the body,
    and leaving it is what keeps `help()`, pydoc and Sphinx answering with a sentence
    instead of nothing — a docstring lifted whole is a change to the distributed package
    and not only to the repository
    (L0270-a-lift-leaves-the-summary-line, cites-as-live).

    A line carrying a citation is never lifted, of this entry's id or any other. A
    section is often pinned by several entries, each citing from the same docstring, and
    a lift that took their citations with it would move them where no document glob
    reaches and leave their References rows naming a file that no longer cites them —
    a detection regression that every checker would pass
    (L0271-a-lift-never-moves-a-citation, cites-as-live).
    """
    m = DOCSTRING_RE.search(section)
    if m is None:
        return None
    quote = m.group("quote")
    end = section.find(quote, m.end())
    if end == -1:
        return None
    body = section[m.end() : end]
    lines = body.splitlines()
    if len(lines) < 3:
        return None  # a summary and its closing quotes; there is no body under it
    # The summary line is the first, and the blank line under it is the seam.
    cut = 1
    while cut < len(lines) and not lines[cut].strip():
        cut += 1
    runs, cur, at = [], [], m.end() + sum(len(x) + 1 for x in lines[:cut])
    start = at
    for ln in lines[cut:]:
        if CITATION_RE.search(ln):
            if any(x.strip() for x in cur):
                runs.append((start, at))
            cur, start = [], at + len(ln) + 1
        else:
            cur.append(ln)
        at += len(ln) + 1
    if any(x.strip() for x in cur):
        runs.append((start, at))
    # Each run is trimmed back to its last line with anything on it, so a blank line
    # before a citation is not lifted and then missing from what the witness holds.
    out = []
    for lo, hi in runs:
        # `splitlines` drops the newline the last body line does not have, so the walk
        # above can run one character past the body and take the closing quote with it.
        trimmed = section[lo : min(hi, end)].rstrip()
        if trimmed:
            out.append((lo, lo + len(trimmed)))
    return out or None


def citation_act(status):
    """The act a citation written now may use against an entry in `status`.

    Asked of `ACT_ALLOWS` rather than tabulated again here, in the order a reader of the
    entry would want it: as live where it is live, as contested where it is contested,
    and as fallen where nothing else is legal. A second copy of that table is how a
    marker comes to be written with an act `references` refuses the moment it is read.
    """
    order = ("cites-as-live", "cites-as-contested", "cites-as-fallen")
    return next(act for act in order if status in ACT_ALLOWS[act])


def marker_for(entry, section, parts):
    """The citation a lift leaves where the prose was, as `(at, line)`, or None when the
    section already carries one of this entry.

    A lift is a deletion. Where the section already cited the entry, that citation stays
    where its author put it and is the marker; `liftable` would not have taken the line
    it is on in any case. Where the section cited nothing, the deletion used to leave a
    section no reader could trace: the prose was on the entry,
    and nothing in the file said which entry, or that there had been prose at all. The
    only signal was a freshness flag saying the section had moved, which is what any edit
    produces and which names no id. So the marker is written here, and it is an ordinary
    citation rather than a form of its own — held to the entry's status at every check
    like any other, and read back by `show`
    (L0277-a-lift-leaves-a-citation-where-the-prose-was, cites-as-live).

    It goes where the first run began, which is a line start inside the docstring body,
    and takes that prose's own indentation. Nothing has to be known about the artifact's
    language for that: the lift only ever takes docstring body, so the marker lands
    inside the same string literal the prose came out of, and a comment syntax the tool
    would have to be told per evidence type is never needed.
    """
    if any(m.group(1) == entry.id for m in CITATION_RE.finditer(section)):
        return None
    at, stop = parts[0]
    first = next((ln for ln in section[at:stop].splitlines() if ln.strip()), "")
    indent = first[: len(first) - len(first.lstrip())]
    return at, f"{indent}({entry.id}, {citation_act(entry.status())})"


def reference_row(entry, rel, config):
    """The `## References` row a marker written into `rel` owes, or None when it owes
    none — because the artifact is not a document, or because the entry lists it already.

    A citation is a citation where a checker reads one. Where the artifact is a
    configured document, `references` reads the marker and fails until the entry's
    References section lists the citing document, so the row is written by the same
    command that writes the marker and the lift leaves `check` green rather than leaving
    a failure for whoever runs it next. Where the artifact is not a document the row
    would itself be the failure — `references` reports a row naming a file it cannot see
    — so an inert marker gets none and names the entry for a reader instead of for a
    checker (L0278-a-marker-is-declared-where-a-checker-reads-it, cites-as-live).
    """
    if not selects_document(rel, config):
        return None
    act = citation_act(entry.status())
    if any(r and r.path == rel and r.act == act for _, r in entry.references):
        return None
    return f"- {rel} · standing · {act}"


def plan(entry, pointer, tree_text, config):
    """What a lift of `pointer`'s section would do: the witness, each run of prose, the
    file as the lift would leave it, and the marker line it would write, if any.

    The witness is the digest of the section as it stands *before* the lift, which is the
    only moment it can be taken: afterwards no tree holds it and only history does.
    """
    span = section_span(tree_text, config, pointer.type, pointer.section)
    if span is None:
        raise LiftError(
            f"{pointer.target} holds no section {pointer.section!r}; there is nothing to lift"
        )
    section = tree_text[span[0] : span[1]]
    witness = digest_of(section)
    parts = liftable(section)
    if parts is None:
        raise LiftError(
            f"{pointer.target} § {pointer.section!r} has no docstring body to lift under its "
            "summary line, or every line of one carries a citation"
        )
    mark = marker_for(entry, section, parts)
    proses, kept, at = [], [], 0
    for lo, hi in parts:
        proses.append("\n".join(ln.rstrip() for ln in section[lo:hi].splitlines()).strip("\n"))
        kept.append(section[at:lo])
        if mark is not None and mark[0] == lo:
            kept.append(mark[1])
        at = hi
    kept.append(section[at:])
    new_section = "".join(kept)
    after = tree_text[: span[0]] + new_section + tree_text[span[1] :]
    return witness, proses, after, (mark[1] if mark else None)


def passage_block(stamp, author, pointer, witness, prose):
    """The `## Passages` block a lift appends, as text."""
    body = "\n".join(
        (PASSAGE_INDENT + ln).rstrip() if ln.strip() else "" for ln in prose.splitlines()
    )
    lifted = f'{pointer.type}: {pointer.target} § "{pointer.section}" ={witness}'
    return f"- {stamp} · author: {author}\n  lifted: {lifted}\n  passage:\n{body}\n"


def append_passage(text, block):
    """`text` with `block` appended to its `## Passages` section, the section added when
    it is not there.

    Appended below the APPEND marker and never above it, so a lift onto an entry that is
    already committed touches no frozen byte and costs no supersession
    (L0273-a-lifted-passage-is-appended-and-never-frozen, cites-as-live).
    """
    if "## Passages" in text:
        return text.rstrip("\n") + "\n\n" + block
    return text.rstrip("\n") + "\n\n## Passages\n\n" + block


def add_reference_row(text, row):
    """`text` with `row` added to the entry's `## References` section.

    Not appended to the end of the file, which is where `## Passages` is: a row written
    after that heading is a row in another section, and the References section it was
    meant for stays empty while the checker that reads it says the document cites an
    entry that does not list it.
    """
    m = re.search(r"^## References[ \t]*$", text, re.MULTILINE)
    if m is None:
        raise LiftError("the entry has no References section for the marker's row to go in")
    nxt = re.compile(r"^## ", re.MULTILINE).search(text, m.end())
    end = nxt.start() if nxt else len(text)
    rows = [ln for ln in text[m.end() : end].splitlines() if ln.strip()]
    tail = text[end:]
    return text[: m.end()] + "\n\n" + "\n".join([*rows, row]) + "\n" + ("\n" + tail if tail else "")
