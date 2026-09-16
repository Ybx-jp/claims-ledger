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
    CITATION_RE,
    PASSAGE_INDENT,
    LedgerError,
    digest_of,
    git_call,
    git_env,
    section_span,
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


def plan(entry, pointer, tree_text, config):
    """What a lift of `pointer`'s section would do: the witness, each run of prose, and
    the file as the lift would leave it.

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
    proses, kept, at = [], [], 0
    for lo, hi in parts:
        proses.append("\n".join(ln.rstrip() for ln in section[lo:hi].splitlines()).strip("\n"))
        kept.append(section[at:lo])
        at = hi
    kept.append(section[at:])
    new_section = "".join(kept)
    return witness, proses, tree_text[: span[0]] + new_section + tree_text[span[1] :]


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
