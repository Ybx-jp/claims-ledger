"""Citations, both directions, checked.

Entry to entry: every `entry:` ground names an entry that exists and carries an act
compatible with the target's current status — `cites-as-live` needs open or
corroborated, `cites-as-contested` needs contested, `challenges` needs open,
corroborated or contested, `cites-as-fallen` accepts any status and is the only act
legal against a fallen one. The filter a reader must apply every time is applied for
them here. An entry that has itself fallen is exempt: its Grounds are immutable history,
and a dependent whose live-cited ground fell is superseded rather than repaired.

Document to entry: a document cites an entry inline as `(A0007-slug, cites-as-live)`.
Every cited id exists, the act is compatible with the target's status, and the entry's
References section lists the citing document; every location an entry lists really
cites it. No document may cite an id in a quarantined series, by prefix alone. A
document that carries an entry's Assertion verbatim without citing it is reported too:
that finds copies, and says nothing about restatements in other words.

The hypothesis roster (a ROSTER.md among the documents, or whatever the project's
configuration names) is a hand-maintained view of the entries and is checked against
them: one row per hypothesis whose status is not terminal, the row's first cell citing
it and its last cell stating its status.

Run:  claims-ledger references
Exit 1 on any failure.
Proven against the red-team corpus by `claims-ledger corpus`.
"""

from __future__ import annotations

import os

from .schema import (
    ACT_ALLOWS,
    CITATION_RE,
    FALLEN,
    TERMINAL,
    Report,
    archived_id_re,
    by_id,
    load_entries,
    normalize,
    read_document,
)


def roster_rows(body):
    """(entry id, act, cells) for each table row whose first cell cites an entry."""
    rows = []
    for line in body.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = CITATION_RE.search(cells[0]) if cells else None
        if m:
            rows.append((m.group(1), m.group(2), cells))
    return rows


def check_roster(entries, index, status, ledger):
    """The hypothesis roster is a hand-maintained view of the entries: one row per
    hypothesis whose status is not terminal, the row's first cell citing it and its
    last cell stating its status. A row that says something the entry does not, or a
    hypothesis with no row, is a failure; the roster is not generated, so it is
    checked."""
    out = []
    roster = ledger.config.roster
    if not roster:
        return out
    rows = []  # (doc name, entry id, act, cells)
    for name, path in ledger.docs:
        if os.path.basename(name) != roster:
            continue
        body = read_document(path)
        if body is None:
            continue
        for ident, act, cells in roster_rows(body):
            rows.append((name, ident, act, cells))
            target = index.get(ident)
            if target is None:
                continue  # reported as a dangling citation above
            if target.front.get("kind") != "hypothesis":
                out.append(
                    Report(
                        "fail",
                        None,
                        name,
                        f"row cites {ident} as its hypothesis, but that entry is a "
                        f"{target.front.get('kind')}",
                    )
                )
            elif cells[-1] != status[ident]:
                out.append(
                    Report(
                        "fail",
                        None,
                        name,
                        f"row for {ident} says `{cells[-1]}`; the entry's status is "
                        f"`{status[ident]}`",
                    )
                )
    for e in entries:
        if e.front.get("kind") != "hypothesis" or status[e.id] in TERMINAL:
            continue
        mine = [r for r in rows if r[1] == e.id]
        if not mine:
            out.append(
                Report(
                    "fail",
                    e.prefix,
                    "Roster",
                    f"no row in a {roster} document cites this open hypothesis; the roster "
                    "has one row per hypothesis that is not terminal",
                )
            )
        elif len(mine) > 1:
            out.append(
                Report("fail", e.prefix, "Roster", f"{len(mine)} roster rows cite this hypothesis")
            )
    return out


def run(ledger):
    entries = load_entries(ledger)
    index = by_id(entries)
    status = {e.id: e.status() for e in entries}
    config = ledger.config
    archived = archived_id_re(config)
    reports = []

    for e in entries:
        if status[e.id] in FALLEN:
            # A fallen entry's Grounds are immutable and are history: a dependent whose
            # live-cited ground fell is superseded, and the successor's acts are what is
            # held to the targets' current statuses.
            continue
        for raw, p in e.grounds:
            if p is None or p.type != "entry" or p.act not in ACT_ALLOWS:
                continue
            target = index.get(p.target)
            if target is None:
                reports.append(
                    Report("fail", e.prefix, "Grounds", f"cites {p.target}, which does not exist")
                )
            elif status[p.target] not in ACT_ALLOWS[p.act]:
                reports.append(
                    Report(
                        "fail",
                        e.prefix,
                        "Grounds",
                        f"{p.act} against {p.target}, whose status is {status[p.target]}; "
                        f"{p.act} needs {' or '.join(sorted(ACT_ALLOWS[p.act]))}",
                    )
                )

    cited = {}  # doc name -> {(entry id, act)}
    for name, path in ledger.docs:
        body = read_document(path)
        if body is None:
            continue
        cited[name] = set()
        seen_archived = sorted({m.group(0) for m in archived.finditer(body)}) if archived else []
        if seen_archived:
            reports.append(
                Report(
                    "fail",
                    None,
                    name,
                    f"cites archived id(s) {', '.join(seen_archived)}; no document may "
                    "cite the archive",
                )
            )
        for m in CITATION_RE.finditer(body):
            ident, act = m.group(1), m.group(2)
            if ident[0] in config.archived_prefixes:
                continue  # already reported by prefix
            cited[name].add((ident, act))
            target = index.get(ident)
            if target is None:
                reports.append(Report("fail", None, name, f"cites {ident}, which does not exist"))
                continue
            if status[ident] not in ACT_ALLOWS[act]:
                reports.append(
                    Report(
                        "fail",
                        None,
                        name,
                        f"{act} against {ident}, whose status is {status[ident]}; "
                        f"{act} needs {' or '.join(sorted(ACT_ALLOWS[act]))}",
                    )
                )
            if not any(r and r.path == name and r.act == act for _, r in target.references):
                reports.append(
                    Report(
                        "fail",
                        None,
                        name,
                        f"cites {ident} {act} but {ident}'s References section does not "
                        "list this document",
                    )
                )
        norm_body = normalize(body)
        for e in entries:
            needle = normalize(e.assertion)
            if (
                len(needle) >= 20
                and needle in norm_body
                and not any(i == e.id for i, _ in cited[name])
            ):
                reports.append(
                    Report(
                        "fail",
                        None,
                        name,
                        f"carries the Assertion of {e.id} verbatim without citing it",
                    )
                )

    reports += check_roster(entries, index, status, ledger)

    for e in entries:
        for raw, r in e.references:
            if r is None:
                continue
            if r.path not in cited:
                reports.append(
                    Report(
                        "fail",
                        e.prefix,
                        "References",
                        f"lists {r.path}, which is not a document this checker can see",
                    )
                )
            elif (e.id, r.act) not in cited[r.path]:
                reports.append(
                    Report(
                        "fail",
                        e.prefix,
                        "References",
                        f"lists {r.path} · {r.act}, but that document does not cite "
                        f"{e.id} that way",
                    )
                )
    return reports
