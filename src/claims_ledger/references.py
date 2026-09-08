"""Citations, both directions, checked.

Entry to entry, at `run`: an `entry:` ground names an entry that exists, under an act
that entry's current status allows. Document to entry, also at `run`: an inline
`(A0007-<slug>, cites-as-live)` and the row in the entry's References section have to
agree with each other and with the status. The hypothesis roster is checked against the
entries at `check_roster`. Each rule is stated where it is applied.

Run:  claims-ledger references
Exit 1 on any failure.
Proven against the red-team corpus by `claims-ledger corpus`.
"""

from __future__ import annotations

import os

from .schema import (
    ACT_ALLOWS,
    ACTS,
    CITATION_RE,
    MISCITATION_RE,
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
    hypothesis whose status is not terminal
    (L0048-every-open-hypothesis-has-exactly-one-roster-row, cites-as-live), the row's
    first cell citing it and its last cell stating its status
    (L0049-a-roster-row-states-what-the-entry-says, cites-as-live). A row that says
    something the entry does not, or a hypothesis with no row, is a failure; the roster
    is not generated, so it is checked.

    Two rows for one hypothesis fail as well as none: a duplicated row is the shape in
    which a stale status survives an edit to its twin, and the reader has no way to tell
    which of the two was maintained.
    """
    out = []
    roster = ledger.config.roster
    if not roster:
        return out
    rows = []  # (doc name, entry id, act, cells)
    for name, path in ledger.docs:
        if os.path.basename(name) != roster:
            continue
        body, _ = read_document(path)
        if body is None:
            continue  # reported once, by run(), rather than once per checker loop
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


def run(ledger, entries=None):
    """Both directions.

    **Entry to entry.** Every `entry:` ground names an entry that exists and carries an
    act compatible with the target's current status — `cites-as-live` needs open or
    corroborated, `cites-as-contested` needs contested, `challenges` needs open,
    corroborated or contested, `cites-as-fallen` and `distinguishes` accept any status,
    and `cites-as-fallen` is the only *citation* act legal against a fallen one
    (L0042-an-act-is-checked-against-the-targets-current-status, cites-as-live). The
    filter a reader would otherwise apply every time is applied for them here.

    **Document to entry.** A document cites an entry inline as
    `(A0007-<slug>, cites-as-live)`. Every cited id exists, the act is compatible with the
    target's status, and the entry's References section lists the citing document; every
    location an entry lists really cites it
    (L0044-a-citation-and-its-references-row-must-agree, cites-as-live). No document may
    cite an id in a quarantined series, by prefix alone
    (L0045-an-archived-series-is-refused-by-prefix, cites-as-live). A document that
    carries an entry's Assertion verbatim without citing it is reported too
    (L0046-an-uncited-verbatim-assertion-is-a-failure, cites-as-live): that finds copies,
    and says nothing about restatements in other words.
    """
    entries = load_entries(ledger) if entries is None else entries
    index = by_id(entries)
    status = {e.id: e.status() for e in entries}
    config = ledger.config
    archived = archived_id_re(config)
    reports = []

    for e in entries:
        if status[e.id] in TERMINAL:
            # A terminal entry's Grounds are immutable and are history: a dependent whose
            # live-cited ground fell is superseded, and the successor's acts are what is
            # held to the targets' current statuses. The line is terminality and not
            # `FALLEN`, because what makes the act unrepairable is that no verdict may
            # follow — true of `non-comparable` as much as of a fall — while the Grounds
            # sit in the frozen region and cannot be edited either
            # (L0154-a-terminal-entrys-grounds-are-immutable-history, cites-as-live).
            continue
        for _raw, p in e.grounds:
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

    # A document that could not be opened at all, and one that fails at the read: either
    # way its citations were not checked, and a checker that cannot read a document may
    # not report a clean run over it
    # (L0047-an-unreadable-document-is-a-failure-not-a-clean-run, cites-as-live).
    # `fail`, not `flag`, because the exit code is what a hook acts on and nothing here
    # was verified.
    for name, problem in ledger.unreadable_docs:
        reports.append(Report("fail", None, name, problem))

    cited = {}  # doc name -> {(entry id, act)}
    for name, path in ledger.docs:
        body, problem = read_document(path)
        if body is None:
            reports.append(Report("fail", None, name, f"{problem}; its citations were not checked"))
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
        for m in MISCITATION_RE.finditer(body):
            if m.group(2) in ACTS or m.group(1)[0] in config.archived_prefixes:
                continue  # a citation, or already reported by prefix
            # A parenthetical shaped like a citation whose act is not a citation act.
            # `CITATION_RE` does not match it and no other rule reads documents, so a
            # mistyped act — and `distinguishes`, which an entry may perform and a
            # document may not — used to sit in a checked document as unchecked prose
            # (L0159-a-citation-shaped-parenthetical-names-a-citation-act, cites-as-live).
            reports.append(
                Report(
                    "fail",
                    None,
                    name,
                    f"`{m.group(0)}` is shaped like a citation but `{m.group(2)}` is not a "
                    f"citation act; a document cites an entry with one of {list(ACTS)}",
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
        for _raw, r in e.references:
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
