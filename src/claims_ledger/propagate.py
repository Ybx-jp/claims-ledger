"""The one place machinery writes into an entry.

Walks the `entry:` edges. When an entry cited `cites-as-live` has fallen (refuted,
superseded, retracted), the dependent must carry a `contested` verdict by the
propagation author naming the fallen entry; when an entry is named by a `challenges`
act, the challenged entry must carry a `contested` verdict by the propagation author
naming the challenger. A missing verdict is appended with `--write` and is a failure
either way, so the flag is seen. A `challenges` act against a fallen target is reported
as illegal and nothing is appended. A propagated verdict whose stated cause does not
exist — no such challenger, no such fall — is an orphan and fails. A dependent that has
itself fallen needs no flag: a verdict after a terminal status is illegal, and its
successor is walked.

Run:  claims-ledger propagate [--write]
      Without --write nothing is modified; the missing verdicts are reported. With it
      they are appended, each attributed to the propagation author, and the run still
      exits non-zero so the change is looked at before it is committed.
Exit 1 on any failure.
Proven against the red-team corpus by `claims-ledger corpus`.
"""

from __future__ import annotations

from datetime import datetime

from .config import leaves_root
from .schema import (
    FALLEN,
    TERMINAL,
    LedgerError,
    Report,
    by_id,
    load_entries,
)


def has_propagated(entry, cause_id, act, author):
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
    for v in entry.verdicts:
        if v.status in FALLEN:
            return v
    return None


def verdict_block(status_grade, cause_id, act, note, author):
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        f"- {stamp} · contested · grade: {status_grade} · author: {author}\n"
        f"  evidence: entry: {cause_id} · {act}\n"
        f"  note: {note}\n"
    )


def append_verdict(entry, block, root=None):
    """The verdict appended to the entry file. `root` refuses a write that lands outside
    the project — an entry inside `entries/` can be a symlink to anywhere, and following
    one is the write outside the root that this package states it does not do."""
    if root is not None and (outside := leaves_root(root, entry.path)) is not None:
        raise LedgerError(
            f"{entry.path} leads to {outside}, outside the project root {root}; "
            "nothing is written through a link that leaves the project"
        )
    text = entry.text
    marker = "\n## References"
    if marker in text:
        head, tail = text.split(marker, 1)
        head = head.rstrip("\n") + "\n"
        if "## Verdicts" in head and head.rstrip().endswith("## Verdicts"):
            head += "\n"
        text = head + block + marker + tail
    else:
        text = text.rstrip("\n") + "\n" + block
    try:
        entry.path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise LedgerError(
            f"{entry.path}: cannot append the verdict ({exc.strerror or exc})"
        ) from exc


def run(ledger, write=False):
    entries = load_entries(ledger)
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
            if status[e.id] in FALLEN and p.act == "cites-as-live":
                # A dependent that has itself fallen needs no flag: its status is
                # terminal, a verdict after it is illegal, and its successor is what
                # is walked.
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
        for e, block in pending:
            append_verdict(e, block, root=ledger.config.root)
            reports.append(
                Report(
                    "flag",
                    e.prefix,
                    "Verdicts",
                    f"appended a contested verdict by {author}",
                )
            )
    return reports
