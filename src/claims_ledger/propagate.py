"""The one place machinery writes into an entry.

Walks the `entry:` edges. When an entry cited `cites-as-live` has fallen (refuted,
superseded, retracted), the dependent must carry a `contested` verdict by the
propagation author naming the fallen entry
(L0017-a-fallen-ground-demands-a-verdict-on-its-dependent, cites-as-live); when an entry
is named by a `challenges` act, the challenged entry must carry a `contested` verdict by
the propagation author naming the challenger
(L0018-a-challenges-act-demands-a-verdict-on-its-target, cites-as-live). A missing
verdict is appended with `--write` and is a failure either way, so the flag is seen
(L0012-a-propagated-append-is-still-a-failing-run, cites-as-live). A `challenges` act
against a fallen target is reported as illegal and nothing is appended
(L0019-a-challenges-act-against-a-terminal-target-appends-nothing, cites-as-live). A
propagated verdict whose stated cause does not exist — no such challenger, no such fall
— is an orphan and fails
(L0013-a-propagated-verdict-names-a-cause-that-happened, cites-as-live). A dependent
whose own status is terminal needs no flag: a verdict after a terminal status is
illegal, and its successor is walked
(L0155-a-terminal-dependent-is-not-flagged, cites-as-live).

Two acts walk and the rest do not. A `distinguishes` ground carries nothing here: it says
the two entries are different claims about the same artifact, which is a statement about
their Scopes, so the target's fall is not news about the entry that distinguished itself
from it (L0161-a-distinguishing-ground-propagates-nothing, cites-as-live).

Run:  claims-ledger propagate [--write]
      Without --write nothing is modified
      (L0021-without-write-nothing-is-modified, cites-as-live); the missing verdicts are
      reported. With it they are appended, each attributed to the propagation author,
      and the run still exits non-zero so the change is looked at before it is
      committed.
Exit 1 on any failure.
Proven against the red-team corpus by `claims-ledger corpus`.
"""

from __future__ import annotations

import re
from datetime import datetime

from .config import leaves_root
from .schema import (
    APPEND,
    FALLEN,
    TERMINAL,
    LedgerError,
    Report,
    by_id,
    load_entries,
    read_text_exact,
    write_text_atomically,
)


def has_propagated(entry, cause_id, act, author):
    """Whether `entry` already carries the propagated verdict it is owed for `cause_id`.

    Five conditions of one verdict: a contested status, the propagation author, an
    `entry:` pointer, that pointer's target, and the act that caused it. A near miss
    does not discharge the propagation — it leaves a verdict the entry still owes
    (L0025-a-propagation-is-recognized-only-on-an-exact-match, cites-as-live).
    """
    return any(
        v.author == author
        and v.status == "contested"
        and v.pointer
        and v.pointer.type == "entry"
        and v.pointer.target == cause_id
        and v.pointer.act == act
        for v in entry.verdicts
    )


def falling_verdict(entry):
    """The verdict that took `entry` down, or None.

    Its grade is the grade a propagated flag carries, and its index and timestamp are
    what the note names, so the flag says which fall caused it
    (L0026-a-propagated-fall-carries-the-grade-of-the-fall, cites-as-live).
    """
    for v in entry.verdicts:
        if v.status in FALLEN:
            return v
    return None


def verdict_block(status_grade, cause_id, act, note, author):
    """The three lines of a propagated verdict.

    Contested, attributed to the propagation author, and carrying its cause as an
    `entry:` pointer with the act that caused it: there is no route through here to a
    propagated verdict of another status, or to one that names nothing
    (L0024-a-propagated-verdict-is-contested-and-names-its-cause, cites-as-live).
    """
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        f"- {stamp} · contested · grade: {status_grade} · author: {author}\n"
        f"  evidence: entry: {cause_id} · {act}\n"
        f"  note: {note}\n"
    )


def grouped(pending):
    """[(entry, joined blocks)] — every block destined for one entry in a single write.

    Each block is built from `entry.text` as it was parsed, so two writes to one entry
    make the second overwrite the first. An entry citing two fallen grounds earns two
    verdicts and must keep both.

    Ledger: (L0014-one-append-carries-every-verdict-an-entry-is-owed, cites-as-live).
    """
    order, blocks = [], {}
    for entry, block in pending:
        key = str(entry.path)
        if key not in blocks:
            order.append(key)
            blocks[key] = (entry, [])
        blocks[key][1].append(block)
    return [(blocks[k][0], "\n".join(blocks[k][1])) for k in order]


REFERENCES_RE = re.compile(r"(?:\r\n|\n)## References")


def append_verdict(entry, block, *, root):
    """The verdicts appended to the entry file, and the only append in the package:
    `freshness --write` reaches its write through here rather than through one of its
    own (L0027-one-function-appends-every-verdict, cites-as-live).

    `root` refuses a write that lands outside the project — an entry inside `entries/`
    can be a symlink to anywhere, and following one is the write outside the root that
    this package states it does not do
    (L0022-nothing-is-written-through-a-link-that-leaves-the-root, cites-as-live).

    Required, and keyword-only, because a guard a caller may omit is a guard a caller
    omits: HIGH-11, MEDIUM-19 and HIGH-56 were each one write site that never asked this
    question, and a default of None was the third one waiting to happen
    (L0023-the-root-of-an-append-is-required-and-keyword-only, cites-as-live).

    The file is re-read from disk with its own line endings, rather than written back
    from the text the parser normalized: an entry committed with CRLF was otherwise
    rewritten line for line by an append that was supposed to add three, and every byte
    of its immutable frozen region changed with it.

    The insertion point is looked for below the APPEND marker and nowhere else. `##
    References` above the marker is a layout `validate` rejects — and `propagate --write`
    does not require `validate` to be clean before it writes — so choosing the insertion
    point by that heading alone put the verdict inside the frozen region of a committed
    entry.

    Ledger: (L0028-an-append-cannot-reach-above-the-marker, cites-as-live) and
    (L0029-an-append-keeps-the-line-endings-it-found, cites-as-live).
    """
    if (outside := leaves_root(root, entry.path)) is not None:
        raise LedgerError(
            f"{entry.path} leads to {outside}, outside the project root {root}; "
            "nothing is written through a link that leaves the project"
        )
    text = read_text_exact(entry.path)
    newline = "\r\n" if "\r\n" in text else "\n"
    if newline != "\n":
        block = block.replace("\n", newline)
    head, marker, appendable = text.partition(APPEND)
    if not marker:
        head, appendable = "", text
    m = REFERENCES_RE.search(appendable)
    if m:
        before, after = appendable[: m.start()], appendable[m.start() :]
        before = before.rstrip("\r\n") + newline
        if before.rstrip().endswith("## Verdicts"):
            before += newline
        appendable = before + block + after
    else:
        appendable = appendable.rstrip("\r\n") + newline + block
    new_text = head + marker + appendable
    if marker and new_text.partition(APPEND)[0] != head:
        # Cannot happen with the insertion above, and asserted rather than trusted: this
        # is the one function in the package that writes into a committed entry, and the
        # region above the marker is what it may not touch.
        raise LedgerError(
            f"{entry.path}: appending the verdict would change the region above the "
            "APPEND marker, which is immutable; nothing was written"
        )
    try:
        write_text_atomically(entry.path, new_text)
    except OSError as exc:
        raise LedgerError(
            f"{entry.path}: cannot append the verdict ({exc.strerror or exc})"
        ) from exc


def run(ledger, write=False, entries=None):
    entries = load_entries(ledger) if entries is None else entries
    index = by_id(entries)
    status = {e.id: e.status() for e in entries}
    author = ledger.config.propagation_author
    reports = []
    pending = []  # (entry, block)

    for e in entries:
        for _, p in e.grounds:
            if p is None or p.type != "entry" or p.target not in index:
                continue
            target = index[p.target]
            if status[e.id] in TERMINAL and p.act == "cites-as-live":
                # A dependent whose own status is terminal needs no flag: a verdict after
                # it is illegal, and its successor is what is walked. The test is
                # `TERMINAL` and not `FALLEN`: a `non-comparable` dependent is terminal
                # without having fallen, and flagging it demanded a verdict `validate`
                # then refused as one following a terminal verdict — `propagate --write`
                # wrote what `validate` rejects, and neither run could be made to pass.
                # The target side below stays `FALLEN`: what propagates is a ground that
                # fell, while what exempts is this entry's own terminality
                # (L0155-a-terminal-dependent-is-not-flagged, cites-as-live).
                continue
            if p.act == "cites-as-live" and status[target.id] in FALLEN:
                if not has_propagated(e, target.id, "fallen", author):
                    fv = falling_verdict(target)
                    reports.append(
                        Report(
                            "fail",
                            e.prefix,
                            "Verdicts",
                            f"cites {target.id} cites-as-live and {target.id} has fallen to "
                            f"{status[target.id]}, but carries no contested verdict by "
                            f"{author} naming it",
                        )
                    )
                    pending.append(
                        (
                            e,
                            verdict_block(
                                fv.grade if fv else target.grade,
                                target.id,
                                "fallen",
                                f"{target.id} {status[target.id]} "
                                f"(verdict {fv.index if fv else '?'}, "
                                f"{fv.timestamp if fv else 'unknown'})",
                                author,
                            ),
                        )
                    )
            elif p.act == "challenges":
                if status[target.id] in TERMINAL:
                    reports.append(
                        Report(
                            "fail",
                            target.prefix,
                            "Verdicts",
                            f"{e.id} challenges {target.id}, whose status is terminal "
                            f"({status[target.id]}); no contested verdict is appended and the "
                            "act is illegal — a fallen entry is cited cites-as-fallen",
                        )
                    )
                elif not has_propagated(target, e.id, "challenges", author):
                    reports.append(
                        Report(
                            "fail",
                            target.prefix,
                            "Verdicts",
                            f"{e.id} cites {target.id} · challenges but {target.id} carries "
                            "no propagated contested verdict naming it",
                        )
                    )
                    pending.append(
                        (
                            target,
                            verdict_block(
                                e.grade,
                                e.id,
                                "challenges",
                                f"propagated from {e.id}'s challenges act",
                                author,
                            ),
                        )
                    )

    for e in entries:
        for v in e.verdicts:
            p = v.pointer
            if v.author != author or not p or p.type != "entry":
                continue
            cause = index.get(p.target)
            if p.act == "challenges":
                ok = cause is not None and any(
                    g and g.type == "entry" and g.target == e.id and g.act == "challenges"
                    for _, g in cause.grounds
                )
                why = f"{p.target} carries no challenges act against {e.id}"
            elif p.act == "fallen":
                ok = (
                    cause is not None
                    and status.get(p.target) in FALLEN
                    and any(
                        g
                        and g.type == "entry"
                        and g.target == p.target
                        and g.act == "cites-as-live"
                        for _, g in e.grounds
                    )
                )
                why = (
                    f"{p.target} has not fallen"
                    if cause is not None and status.get(p.target) not in FALLEN
                    else f"{e.id} does not cite {p.target} cites-as-live"
                )
            else:
                continue
            if cause is None:
                why = f"{p.target} does not exist"
            if not ok:
                reports.append(
                    Report(
                        "fail",
                        e.prefix,
                        "Verdicts",
                        f"verdict {v.index} by {author} names {p.target} as its cause, but "
                        f"{why}; a propagated verdict that nothing caused is an orphan",
                    )
                )

    if write:
        for e, block in grouped(pending):
            append_verdict(e, block, root=ledger.config.root)
            reports.append(
                Report(
                    "flag",
                    e.prefix,
                    "Verdicts",
                    f"appended {block.count(2 * chr(10)) + 1} contested verdict(s) by {author}",
                )
            )
    return reports
