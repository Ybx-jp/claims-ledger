"""Citations, both directions, checked.

Entry to entry, at `run`: an `entry:` ground names an entry that exists, under an act
that entry's current status allows. Document to entry, also at `run`: an inline
`(A0007-<slug>, cites-as-live)`, whose `-<slug>` may be left off, and the row in the
entry's References section have to agree with each other and with the
status. The hypothesis roster is checked against the entries at `check_roster`. Where the
project asks for it, `misplaced_citations` holds a citation to the span its entry pins and
`slug_shape` holds a marker to one of the two spellings; both are configured rather than
always on, and both are off by default. Each rule is stated where it is applied.

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
    by_number,
    citation_slug_policy,
    cited_parts,
    load_entries,
    normalize,
    read_document,
    section_span,
    staged_documents,
)


def document_bodies(ledger, cached=False):
    """{path: (text, problem)} for every configured document, read once for the whole run.

    Under `cached` a document the index holds is read from the index, because that is the
    text the commit will carry and the citation it holds is the one that will land
    (L0221-the-documents-a-cached-run-reads-are-the-staged-ones, cites-as-live). Read once
    here rather than at each of the three loops below, which used to read every document
    three times over.
    """
    staged = staged_documents(ledger, (path for _, path in ledger.docs)) if cached else {}
    bodies = {}
    for _name, path in ledger.docs:
        # `staged` already carries (text, problem) in the shape `read_document` returns, so
        # a document the index holds as undecodable bytes, and one git could not be asked
        # about, are both reported here rather than read out of the working tree.
        bodies[path] = staged[path] if path in staged else read_document(path)
    return bodies


def misplaced_citations(ledger, entries=None, only=None, bodies=None):
    """Citations that sit outside the section the entry they name is pinned to.

    The rule is narrow, and every part of the narrowness is load-bearing. It asks only
    about a citation in a document that the cited entry *also* rests on, by a sectioned
    ground: then there is a span in this very file that the claim is about, and the
    sentence promising it belongs in that span, so the promise and the code that keeps it
    move together and a reader who finds one finds the other. A citation of an entry
    grounded elsewhere is asked nothing, because there is no section here for it to be
    outside of (L0173-a-citation-belongs-in-the-span-its-entry-pins, cites-as-live).

    An entry may rest on several sections of one file; the citation need only be inside
    one of them. `only` narrows the question to one entry, which is what the authoring
    side asks at the moment that entry is written.

    Returned as reports at whatever outcome the project configured, and never called at
    all when it configured `off` — the caller decides, because this is one rule with two
    callers and a second copy of the condition is how two of them come to disagree.
    """
    entries = load_entries(ledger) if entries is None else entries
    index, numbered = by_id(entries), by_number(entries)
    config = ledger.config
    outcome = config.citation_placement
    bodies = document_bodies(ledger) if bodies is None else bodies
    out = []
    for name, path in ledger.docs:
        body, _ = bodies[path]
        if body is None:
            continue  # reported by run(), which is where an unreadable document is a failure
        for m in CITATION_RE.finditer(body):
            ident = m.group(1)
            target, _ = cited_target(ident, index, numbered)
            if target is None:
                continue  # a dangling citation, reported as that
            # Resolved before `only` is compared, and against the entry rather than
            # against the text of the marker: a marker naming the number alone names this
            # entry, and comparing the two strings would stop asking the placement
            # question of exactly the markers a project configured `forbid` for
            # (L0288-a-rule-follows-the-entry-a-marker-resolves-to, cites-as-live).
            if only is not None and target.id != only:
                continue
            spans = []
            for pointer in target.ground_pointers:
                if pointer.type not in config.evidence_sectioned or pointer.target != name:
                    continue
                if not pointer.section:
                    continue
                span = section_span(body, config, pointer.type, pointer.section)
                if span is not None:
                    spans.append((pointer.section, span))
            if not spans or any(start <= m.start() < end for _, (start, end) in spans):
                continue
            where = ", ".join(f'§ "{section}"' for section, _ in spans)
            out.append(
                Report(
                    "fail" if outcome == "fail" else "flag",
                    None,
                    name,
                    f"cites {ident} from outside {where}, the section of this file its "
                    "ground names; the sentence that states a commitment belongs in the "
                    "span that keeps it, so the two move together",
                )
            )
    return out


def cited_target(ident, index, numbered):
    """(entry, problem) for the entry a marker names — the problem being what to print
    when it names none.

    A marker states the whole id, `A0007-a-slug`, or the series and number alone,
    `A0007`, and both name the same entry: the slug is the entry's title in the filename
    and the number is what identifies it. The whole id is looked up first and only a
    marker carrying no slug falls back to the number, so a marker whose slug is wrong —
    a typo, or a slug left behind by a rename — is still `does not exist` rather than
    quietly resolving through the number it happens to share
    (L0284-a-marker-names-its-entry-by-id-or-by-number, cites-as-live).

    Two entries answering to one number is a state a merge can produce and `validate`
    fails on; here it is said rather than guessed at, because picking either of them
    would report a status the reader cannot check.
    """
    if ident in index:
        return index[ident], None
    number, slug = cited_parts(ident)
    candidates = numbered.get(number, ())
    if slug is not None:
        # The slug is wrong, not the number. Saying so, and naming what the number does
        # answer to, turns a rename that left a marker behind from a hunt into an edit;
        # `does not exist` alone sends the reader looking for an entry that is there.
        known = ", ".join(sorted(e.id for e in candidates))
        return None, (
            f"cites {ident}, which does not exist"
            + (f"; {number} is {known}" if candidates else "")
        )
    if not candidates:
        return None, f"cites {ident}, which does not exist"
    if len(candidates) > 1:
        names = ", ".join(sorted(e.id for e in candidates))
        return None, (
            f"cites {ident}, and {len(candidates)} entries answer to that number ({names}); "
            "a marker that names no slug cannot say which"
        )
    return candidates[0], None


def slug_shape(name, policy, ident, entry):
    """The report a marker owes for carrying the entry's slug, or leaving it out, where
    the project has said which it wants; None where it has not.

    Asked only of a marker that resolved. A marker naming an entry that does not exist
    has a failure of its own already, and a second report about the shape of an id that
    names nothing is one the reader has to read past to find the one that matters
    (L0287-the-slug-rule-is-asked-of-a-marker-that-resolved, cites-as-live).

    The policy is handed in rather than looked up here, because it is a property of the
    document and this is called once per marker: on this repository that is one walk of
    the rules for each of four hundred markers where twenty-odd documents would do.
    """
    if policy == "either":
        return None
    _number, slug = cited_parts(ident)
    if policy == "require" and slug is None:
        return Report(
            "fail",
            None,
            name,
            f"cites {ident} without the entry's slug; a marker in this document names the "
            f"entry in full, as `{entry.id}`",
        )
    if policy == "forbid" and slug is not None:
        return Report(
            "fail",
            None,
            name,
            f"cites {ident} with the entry's slug; a marker in this document names the id "
            f"alone, as `{entry.id.split('-', 1)[0]}`",
        )
    return None


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


def check_roster(entries, index, numbered, status, ledger, bodies):
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
        body, _ = bodies[path]
        if body is None:
            continue  # reported once, by run(), rather than once per checker loop
        for ident, act, cells in roster_rows(body):
            target, _ = cited_target(ident, index, numbered)
            # Keyed by the entry the marker resolves to rather than by the marker's own
            # text, so a row citing the number alone is the row that hypothesis has and
            # not a second one nothing counts.
            rows.append((name, target.id if target else ident, act, cells))
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
            elif cells[-1] != status[target.id]:
                out.append(
                    Report(
                        "fail",
                        None,
                        name,
                        f"row for {ident} says `{cells[-1]}`; the entry's status is "
                        f"`{status[target.id]}`",
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


def run(ledger, entries=None, cached=False):
    """Both directions.

    **Entry to entry.** Every `entry:` ground names an entry that exists and carries an
    act compatible with the target's current status — `cites-as-live` needs open or
    corroborated, `cites-as-contested` needs contested, `challenges` needs open,
    corroborated or contested, `cites-as-fallen` and `distinguishes` accept any status,
    and `cites-as-fallen` is the only *citation* act legal against a fallen one
    (L0042-an-act-is-checked-against-the-targets-current-status, cites-as-live). The
    filter a reader would otherwise apply every time is applied for them here.

    **Document to entry.** A document cites an entry inline as
    `(A0007-<slug>, cites-as-live)`, the `-<slug>` optional. Every cited id exists,
    the act is compatible with the
    target's status, and the entry's References section lists the citing document; every
    location an entry lists really cites it
    (L0044-a-citation-and-its-references-row-must-agree, cites-as-live). No document may
    cite an id in a quarantined series, by prefix alone
    (L0045-an-archived-series-is-refused-by-prefix, cites-as-live). A document that
    carries an entry's Assertion verbatim without citing it is reported too
    (L0046-an-uncited-verbatim-assertion-is-a-failure, cites-as-live): that finds copies,
    and says nothing about restatements in other words. Which of the two spellings a
    document may use is the project's to configure, and both are legal until it does
    (L0285-the-slug-a-marker-carries-is-configured, cites-as-live).
    """
    entries = load_entries(ledger, cached=cached) if entries is None else entries
    bodies = document_bodies(ledger, cached=cached)
    index, numbered = by_id(entries), by_number(entries)
    status = {e.id: e.status() for e in entries}
    minted = set(numbered)
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
        body, problem = bodies[path]
        if body is None:
            reports.append(Report("fail", None, name, f"{problem}; its citations were not checked"))
            continue
        cited[name] = set()
        policy = citation_slug_policy(name, config)  # a property of the document, asked once
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
            if m.group(1).split("-", 1)[0] not in minted:
                # The id has to be one this ledger actually minted, matched on the series
                # and number with any slug set aside. `MISCITATION_RE` is a shape, and the
                # shape alone is common in ordinary prose — `(E501, unresolved)` in a
                # source comment is a lint code and a word, and reporting it would fail a
                # commit over a sentence that cites nothing. Only the ledger knows which
                # ids are its own, so the rule asks it
                # (L0175-an-unminted-id-is-not-a-citation-shape, cites-as-live).
                continue
            # A parenthetical shaped like a citation whose act is not a citation act.
            # `CITATION_RE` does not match it and no other rule reads documents, so a
            # mistyped act — and `distinguishes`, which an entry may perform and a
            # document may not — used to sit in a checked document as unchecked prose
            # (L0176-a-citation-shaped-parenthetical-names-a-citation-act, cites-as-live).
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
            target, why = cited_target(ident, index, numbered)
            if target is None:
                reports.append(Report("fail", None, name, why))
                continue
            # Keyed by the entry rather than by the text of the marker, so the References
            # row an entry writes names the act the document really performs however the
            # marker spelled the id, and the two directions still have to agree
            # (L0288-a-rule-follows-the-entry-a-marker-resolves-to, cites-as-live).
            cited[name].add((target.id, act))
            shape = slug_shape(name, policy, ident, target)
            if shape is not None:
                reports.append(shape)
            if status[target.id] not in ACT_ALLOWS[act]:
                reports.append(
                    Report(
                        "fail",
                        None,
                        name,
                        f"{act} against {ident}, whose status is {status[target.id]}; "
                        f"{act} needs {' or '.join(sorted(ACT_ALLOWS[act]))}",
                    )
                )
            if not any(r and r.path == name and r.act == act for _, r in target.references):
                reports.append(
                    Report(
                        "fail",
                        None,
                        name,
                        f"cites {ident} {act} but {target.id}'s References section does not "
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

    reports += check_roster(entries, index, numbered, status, ledger, bodies)
    if config.citation_placement != "off":
        reports += misplaced_citations(ledger, entries=entries, bodies=bodies)

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
