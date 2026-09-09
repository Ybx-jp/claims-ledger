"""Which entries are already about this — asked, not enforced.

Two entries about the same function, written months apart by people who never read each
other, are the failure mode no checker in this package can see: neither names the other,
so every rule that reads an `entry:` edge is out of range by construction. What is
mechanically available is the observation that they are *near* each other — the same
pinned span, or a cohort that nests inside another cohort — and near is not the same as
inconsistent. Only a person can say which.

So this is a lookup and not a checker. The same heuristic run as a gate over this
repository's ledger names a few hundred pairs to surface the two worth reading; a gate at
that rate teaches people to ignore it. Asked one entry at a time it answers with a
handful.

Each rule this file holds itself to is stated where it is kept — `find` for what makes a
neighbour, `span` for the pin it drops, `relation` for the link it reads back, `handover`
for the line it writes out, and `run` for the fact that it reports nothing at all.

Run:  claims-ledger neighbours <entry id | entry path | ground pointer>
Always exits 0.
"""

from __future__ import annotations

import posixpath

from .schema import (
    LedgerError,
    load_entries,
    normalize,
    parse_pointer,
)


def span(pointer):
    """The part of an evidence pointer two entries can share: its type, its path and its
    section, with the pin dropped and the path normalized.

    The pin is dropped because it is the one part of a pointer expected to differ between
    two entries about the same code — they were written at different commits — so
    comparing it would make the lookup answer `nothing` exactly when it matters
    (L0164-a-shared-span-is-compared-without-its-pin, cites-as-live).
    """
    return (pointer.type, posixpath.normpath(pointer.target), pointer.section)


def spans(entry, config):
    """The evidence spans an entry rests on. An `entry:`, `source:`, `search:` or
    `defect:` ground is not one: it names no artifact two entries could both be about."""
    return {span(p) for p in entry.ground_pointers if p.type in config.evidence_types}


def cohort_words(entry):
    """The words of an entry's cohort line, for the nesting test.

    Normalized through the same `normalize` the fingerprint uses, lowercased, split on
    everything that is not alphanumeric, and words of three characters or fewer dropped —
    `a`, `of`, `the` are what every cohort has in common, and keeping them would let two
    cohorts nest on nothing. An empty cohort yields no words and nests with nothing, which
    is what a scaffold still saying `TODO` should do here.
    """
    text = normalize(entry.scope.get("cohort", ""))
    words = "".join(c.lower() if c.isalnum() else " " for c in text).split()
    return frozenset(w for w in words if len(w) > 3)


def nests(mine, theirs):
    """Whether one cohort's words contain the other's, in either direction.

    Nesting rather than similarity, and no threshold: the shape this looks for is the one
    that has actually gone wrong here — two entries whose Scopes name two nested sets,
    where the narrower is read as the wider
    (L0156-a-scope-and-a-warrant-name-one-set-of-statuses, cites-as-live). A similarity
    score tuned until it surfaced that shape would be a number chosen to fit the one
    example it was chosen from.
    """
    return bool(mine) and bool(theirs) and (mine <= theirs or theirs <= mine)


def relation(subject, other):
    """How the two entries are already related in the ledger, or None: a ground either
    way, or a supersession either way.

    That is every link the checkers can already see between two entries, which is exactly
    the set that makes a pair one somebody has read
    (L0165-a-recorded-relation-is-named-so-it-is-not-drawn-twice, cites-as-live).
    """
    for p in subject.ground_pointers:
        if p.type == "entry" and p.target == other.id:
            return f"this entry cites it `{p.act}`"
    for p in other.ground_pointers:
        if p.type == "entry" and p.target == subject.id:
            return f"it cites this entry `{p.act}`"
    if subject.front.get("supersedes") == other.id:
        return "this entry supersedes it"
    if other.front.get("supersedes") == subject.id:
        return "it supersedes this entry"
    return None


def find(entries, config, mine, words, subject=None):
    """[(entry, reasons, relation)] — every neighbour, the ones nobody has related first,
    and among those the ones sharing the most spans.

    An entry is a neighbour when it shares an evidence span or when the two cohorts nest,
    and on no other test
    (L0163-a-neighbour-shares-a-span-or-nests-a-cohort, cites-as-live).

    `subject` is None when the question was asked with a bare ground pointer: there is no
    entry yet, so there is no cohort to nest and no relation to report.
    """
    out = []
    for e in entries:
        if subject is not None and e.id == subject.id:
            continue
        shared = sorted(mine & spans(e, config))
        reasons = [
            f"shares {t}: {path}" + (f' § "{sec}"' if sec else "") for t, path, sec in shared
        ]
        if subject is not None and nests(words, cohort_words(e)):
            reasons.append(f"cohort nests: {e.scope.get('cohort', '').strip()}")
        if reasons:
            out.append((e, reasons, relation(subject, e) if subject is not None else None))
    out.sort(key=lambda row: (row[2] is not None, -len(row[1]), row[0].id))
    return out


def subject_of(ledger, entries, target):
    """(entry or None, spans, cohort words) for what was asked about.

    Three shapes, told apart by what they parse as: an entry id, a path to an entry file,
    or a ground pointer written as it would be written in an entry. The pointer form is
    what an author has before the entry exists — the question is asked of the ground being
    considered, and there is nothing yet to look it up by
    (L0166-a-neighbour-question-is-asked-of-an-entry-or-of-a-ground, cites-as-live).
    """
    for e in entries:
        if target in (e.id, str(e.path), e.path.name):
            return e, spans(e, ledger.config), cohort_words(e)
    pointer = parse_pointer(target)
    if pointer is not None and pointer.type in ledger.config.evidence_types:
        return None, {span(pointer)}, frozenset()
    raise LedgerError(
        f"{target!r} is neither an entry in "
        f"{ledger.config.relative(ledger.entries_dir)} nor a ground pointer of a declared "
        f"evidence type ({'/'.join(ledger.config.evidence_types)})"
    )


def handover(unrelated):
    """The lines a person would otherwise have to compose, written out verbatim.

    A lookup that stops at `here are five entries you have not read together` leaves the
    reader to remember the pointer syntax, the act, and which of the pair may carry the
    ground. Printing the ground itself is the last thing this can do without deciding
    anything: it is the same text either way, and which of the neighbours it is written
    against — if any — is still a judgement nobody else can make
    (L0171-the-lookup-hands-over-the-line-it-would-take, cites-as-live).
    """
    if not unrelated:
        return []
    return [
        "",
        "Nothing above is decided. The line that would record a distinction, verbatim —",
        "in the Grounds of the entry being written, beside what it rests on:",
        *(f"    - entry: {e.id} · distinguishes" for e in unrelated),
        "",
        "Grounds are frozen once an entry is committed, so those go in an entry that is",
        "still being written; between two committed entries the distinction waits for",
        "whichever is superseded next. To reconcile a pair rather than hold it apart:",
        "    claims-ledger new <slug> --supersedes <id>",
    ]


def run(ledger, target, entries=None):
    """The lookup, as lines of text — returned rather than printed, so that the one thing
    that writes to a terminal is the command.

    No Report is built here and nothing is written: this answers a question rather than
    holding the ledger to a rule, so it has no failure to report and `check` does not run
    it (L0162-neighbours-reports-nothing-and-exits-zero, cites-as-live).
    """
    entries = load_entries(ledger) if entries is None else entries
    subject, mine, words = subject_of(ledger, entries, target)
    found = find(entries, ledger.config, mine, words, subject)
    name = subject.id if subject is not None else target
    if not found:
        return [f"no entry shares a ground span or a nesting cohort with {name}"]
    lines = []
    for e, reasons, rel in found:
        lines.append(f"{e.id}  ·  {e.status()}")
        lines.extend(f"    {reason}" for reason in reasons)
        if rel is not None:
            lines.append(f"    already related: {rel}")
    unrelated = [e for e, _, rel in found if rel is None]
    lines.append(
        f"\n{len(found)} neighbour(s) of {name}, {len(unrelated)} with no relation recorded."
    )
    lines.extend(handover(unrelated))
    return lines


def count(ledger, entries=None):
    """How many neighbours each entry has — the distribution the lookup is judged on, so
    that the claim about its size is a thing anybody can recompute
    (L0167-the-neighbour-count-is-recomputable, cites-as-live)."""
    entries = load_entries(ledger) if entries is None else entries
    return {
        e.id: len(find(entries, ledger.config, spans(e, ledger.config), cohort_words(e), e))
        for e in entries
    }
