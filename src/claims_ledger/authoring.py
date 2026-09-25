"""Writing an entry, not checking one.

Everything here is a convenience for an author: the next free id, a scaffolded entry
file, the recomputation of `verbatim_sha` after Scope or Backing is edited, and the
registration of a source together with the bytes a quotation is checked against.

Two rules the checkers enforce shape what this module will and will not do — the frozen
region, which `restamp` refuses to touch, and a registry row that would arrive without
its bytes, which `register_source` will not write. Each is stated where it is kept.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path

from .config import leaves_root
from .schema import (
    APPEND,
    ID_RE,
    PENDING_ANCHOR,
    PREFIX_RE,
    committed_paths,
    digest_of,
    enclosing_repository,
    fingerprint,
    git_call,
    git_problem,
    heads_in_progress,
    load_entries,
    load_registry,
    parse_entry,
    read_artifact,
    read_text_exact,
    section_digest,
    write_bytes_atomically,
    write_text_atomically,
)

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# POSIX NAME_MAX. A slug long enough to overrun it used to reach write_text() and come
# back as `unexpected OSError: File name too long`, which is a bug report asked of a user
# who mistyped a slug.
NAME_MAX = 255

TEMPLATE = """---
id: {id}
kind: {kind}
stated: {stated}
author: {author}
grade: {grade}
{extra}supersedes: {supersedes}
verbatim_sha: {sha}
---

## Assertion

{assertion}

## Scope

metric: {metric}
cohort: {cohort}
condition: {condition}

## Grounds

{grounds}

## Warrant

{warrant}

## Backing

{backing}

{append}

## Verdicts

## References
"""

PLACEHOLDER_ASSERTION = "TODO: the claim, in this project's words. No quotation marks."
PLACEHOLDER_WARRANT = "TODO: the rule by which the grounds support the assertion."
PLACEHOLDER_GROUNDS = (
    "- TODO: one typed pointer per line — the narrowest section that carries the rule, "
    "never a caller that follows it"
)
# The scaffold is the one place an author is looking at the moment they choose a
# ground, and the choice is where the avoidable drift comes from: a ground wider than
# the claim goes stale for edits the claim does not name, and a ground on a caller goes
# stale for every edit to that caller, forever. Both cost a supersession each time, so
# the rule is written into the placeholder rather than left to the documentation
# (L0078-the-scaffold-states-the-ground-rule-where-the-author-chooses, cites-as-live).
TODO_SCOPE = "TODO"


class AuthoringError(Exception):
    """Something an author has to fix before the file can be written."""


def ids_in_the_repository(ledger):
    """({every entry id this repository holds anywhere: where}, what could not be asked).

    Allocation used to be max+1 over the entries directory of one checkout, and two
    branches off one base were therefore allocated the same number. Measured on git
    2.43.0: when the slugs differ the two files merge without a conflict, and all five
    checkers then read the merged tree at exit 0 and say nothing, so the duplicate is
    permanent and silent. The question asked here is the repository's rather than the
    checkout's — every entry filename any ref has ever carried, and every entry file a
    sibling worktree holds right now, including the mints it has not committed
    (L0233-an-id-is-allocated-above-the-whole-repository, cites-as-live).

    Both halves are answered out of what a repository already shares, so neither costs a
    fetch or a network. Worktrees of one repository share their refs, so a branch another
    session committed on is readable from here with nothing exchanged; what no ref can
    show is a mint a sibling checkout has written and not committed, and `git worktree
    list` is what names the checkouts to look in. That is the topology concurrent sessions
    actually have — one repository, several worktrees, each on its own branch.

    A question git declined comes back as a `why` rather than as an empty set. An id
    allocated over a repository that could not be read is exactly the collision this
    exists to prevent, and a caller that cannot ask has to say so rather than mint on the
    strength of the one directory it could see.

    Each id comes back with where it was found — the ref the walk reached it on, or the
    sibling worktree it was listed in — because a number named by hand is refused by
    saying where it is held, and "somewhere in this repository" is a search handed back
    to the person who asked.
    """
    ids, unasked = {}, []
    if not ledger.repo:
        return ids, None  # nothing to ask: the tree is the whole of what there is
    rel = os.path.relpath(ledger.entries_dir, ledger.repo)
    ever = git_call(
        ledger.repo,
        "log",
        "--all",
        # `-m`, because git prints no diff for a merge commit without it and an entry
        # written while a conflict was being settled is created by one. Measured: an entry
        # added in a merge and later removed is invisible to the walk without this and
        # found with it. Over-inclusion is free here — a name that appears is a number not
        # handed out again — so the wider reading is the safe one.
        "-m",
        "--diff-filter=A",
        "--name-only",
        # `--source` names the ref each commit was reached on, behind a NUL no path under
        # the entries directory can begin with.
        "--source",
        "--pretty=format:%x00%S",
        "--",
        f":(literal){rel}",
    )
    if ever.ok:
        ref = "a ref of this repository"
        for line in ever.out.splitlines():
            if line.startswith("\0"):
                ref = line[1:] or ref
            elif line.strip():
                ids.setdefault(Path(line).stem, f"on {ref}")
    else:
        unasked.append(f"which ids the refs of this repository carry ({ever.why})")
    listed = git_call(ledger.repo, "worktree", "list", "--porcelain")
    if listed.ok:
        here = Path(ledger.entries_dir).resolve()
        for line in listed.out.splitlines():
            if not line.startswith("worktree "):
                continue
            directory = Path(line[len("worktree ") :]) / rel
            try:
                if directory.resolve() == here:
                    continue  # this checkout, whose entries the caller already has
                where = f"in the worktree at {line[len('worktree ') :]}"
                for p in directory.iterdir():
                    if p.suffix == ".md":
                        ids.setdefault(p.stem, where)
            except (FileNotFoundError, NotADirectoryError):
                continue  # a checkout that does not hold the ledger: nothing to report
            except OSError as exc:
                # A directory that is there and would not be read is the state this
                # function exists to refuse minting in, and collapsing it into the case
                # above minted over a sibling's entries exactly as if none of this were
                # here.
                # (L0256-a-checkout-that-would-not-be-listed-is-a-question-not-asked, cites-as-live)
                unasked.append(f"what {directory} holds ({exc.strerror or exc})")
    else:
        unasked.append(f"which entries the sibling worktrees hold ({listed.why})")
    return ids, ("; ".join(unasked) or None)


def next_id(entries, archived_prefixes=(), reserved=()):
    """The next free id in the highest series in use, rolling over to the next letter
    when a series is exhausted and skipping any quarantined prefix
    (L0065-the-next-id-rolls-over-and-skips-a-quarantine, cites-as-live).

    `reserved` is every other id the repository holds, which is what keeps two checkouts
    from minting one number; it is read exactly as an entry's own id is, so a number is
    taken whether it is in this tree, on a ref, or in a sibling worktree that has not
    committed it yet.
    """
    used = {}
    for name in [e.id or e.path.stem for e in entries] + list(reserved):
        m = PREFIX_RE.match(name)
        if m:
            letter, digits = m.group(1)[0], m.group(1)[1:]
            used.setdefault(letter, set()).add(int(digits))
    letters = [chr(c) for c in range(ord("A"), ord("Z") + 1) if chr(c) not in archived_prefixes]
    if not letters:
        raise AuthoringError("every series letter is quarantined")
    active = max((letter for letter in used if letter in letters), default=letters[0])
    number = max(used.get(active, {0})) + 1
    if number > 9999:
        remaining = [letter for letter in letters if letter > active]
        if not remaining:
            raise AuthoringError(f"series {active} is exhausted and there is no letter after it")
        active, number = remaining[0], 1
    return f"{active}{number:04d}"


def now_stamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def render_entry(
    ident,
    slug,
    kind="claim",
    grade="measured",
    author="main",
    stated=None,
    supersedes="none",
    credence=None,
    resolves_when=None,
    assertion=PLACEHOLDER_ASSERTION,
    scope=None,
    grounds=None,
    warrant=PLACEHOLDER_WARRANT,
    backing="none",
):
    """The text of an entry, with `verbatim_sha` computed from the Scope and Backing it
    is written with. A scaffolded entry is a draft: the checkers will have plenty to say
    about its placeholders, which is the point of writing them as placeholders."""
    scope = scope or {}
    metric = scope.get("metric", TODO_SCOPE)
    cohort = scope.get("cohort", TODO_SCOPE)
    condition = scope.get("condition", TODO_SCOPE)
    scope_text = f"metric: {metric}\ncohort: {cohort}\ncondition: {condition}"
    extra = ""
    if kind in ("prediction", "hypothesis"):
        extra = f"credence: {credence if credence is not None else 0.5}\n"
        extra += f"resolves_when: {resolves_when or 'TODO: what settles this'}\n"
    text = TEMPLATE.format(
        id=f"{ident}-{slug}",
        kind=kind,
        stated=stated or now_stamp(),
        author=author,
        grade=grade,
        extra=extra,
        supersedes=supersedes,
        sha=fingerprint(scope_text, []),
        assertion=assertion,
        metric=metric,
        cohort=cohort,
        condition=condition,
        grounds="\n".join(grounds) if grounds else PLACEHOLDER_GROUNDS,
        warrant=warrant,
        backing=backing,
        append=APPEND,
    )
    return text


def create_entry(ledger, slug, **kwargs):
    """Write a scaffolded entry and return its path.

    A slug this command cannot turn into an entry is refused as a slug: one that is not
    lowercase-and-hyphens, and one long enough that the filename would overrun what a
    filename holds. Both used to arrive as an OSError, which is a bug report asked of
    someone who mistyped a slug
    (L0066-a-slug-that-cannot-name-a-file-is-refused-as-a-slug, cites-as-live).

    Nothing is written over an entry that is already there, and nothing is written
    through a dangling symlink at the entry's path: a dangling link is not `exists()`,
    so the refusal steps aside and the entry lands wherever the link leads
    (L0067-a-new-entry-lands-on-neither-an-existing-path-nor-a-link, cites-as-live).

    An id named by hand is refused when its number is already held — in this checkout,
    on any ref, or in a sibling worktree — naming the entry that holds it and where,
    unless `force`. It used to be asked only whether the file was there, which compares
    the whole filename, so the same number under another slug was written and the
    collision surfaced at merge, when repairing it rewrites published commits. Where the
    repository could not be read, what could be read is still asked and the rest is
    added to `notes` rather than refused, because naming the id is the way past an
    unread repository
    (L0305-a-number-named-by-hand-is-refused-where-the-repository-holds-it, cites-as-live).
    """
    if not SLUG_RE.match(slug or ""):
        raise AuthoringError(f"`{slug}` is not a lowercase-and-hyphens slug")
    entries = load_entries(ledger)
    ident = kwargs.pop("ident", None)
    force = kwargs.pop("force", False)
    notes = kwargs.pop("notes", None)
    named = ident is not None
    if ident is None:
        reserved, unasked = ids_in_the_repository(ledger)
        if unasked is not None:
            # Minting over a repository that could not be read is how two checkouts come
            # to hold one number, and this is the one moment the number is chosen. An id
            # named by hand is the way past it, because then nothing was allocated
            # (L0234-a-mint-over-an-unread-repository-is-refused, cites-as-live).
            raise AuthoringError(
                f"cannot ask {unasked}, so a free id cannot be chosen: an id allocated "
                "over a repository that could not be read is the collision this asks the "
                "question to prevent. Pass --id to name one yourself."
            )
        ident = next_id(entries, ledger.config.archived_prefixes, reserved)
    name = f"{ident}-{slug}"
    if not ID_RE.match(name):
        raise AuthoringError(f"`{name}` is not <letter><four digits>-<slug>")
    if named and not force:
        refuse_a_number_already_held(ledger, name, entries, notes)
    filename = f"{name}.md"
    if len(filename.encode("utf-8")) > NAME_MAX:
        raise AuthoringError(
            f"`{slug[:32]}…` is too long: the entry would be named {filename[:38]}…, "
            f"{len(filename.encode('utf-8'))} bytes, over the {NAME_MAX} a filename holds"
        )
    path = ledger.entries_dir / filename
    try:
        # `exists()` is inside the funnel, not before it: it re-raises ENAMETOOLONG, which
        # a name that fits NAME_MAX can still provoke by overrunning PATH_MAX under a deep
        # root — an `unexpected OSError` asked of someone who chose a long slug.
        if path.exists():
            raise AuthoringError(f"{path} already exists")
        # A dangling symlink at the entry path is not `exists()`, so without this the
        # refusal above steps aside and the new entry is written wherever the link leads.
        # `restamp` and `append_verdict` have always asked; this one was clean by accident
        # rather than by a guard, which is not a property to leave resting on an accident.
        refuse_to_write_outside_the_root(ledger, path)
        path.parent.mkdir(parents=True, exist_ok=True)
        write_text_atomically(path, render_entry(ident, slug, **kwargs))
    except OSError as exc:
        raise AuthoringError(f"cannot write {path} ({exc.strerror or exc})") from exc
    return path


def refuse_a_number_already_held(ledger, name, entries, notes=None):
    """Raise AuthoringError naming where `name`'s number is held, if anywhere is.

    The number is the `A####` prefix and not the whole id, because a number names one
    entry — a citation may name it without the slug, and `validate` fails two entries
    that share one. This checkout is read first, so an entry both here and on a ref is
    named where the author can open it.
    """
    number = name.split("-", 1)[0]
    held, unasked = ids_in_the_repository(ledger)
    held.update({e.id or e.path.stem: "in this checkout" for e in entries})
    holders = sorted(
        (ident, where) for ident, where in held.items() if ident.split("-", 1)[0] == number
    )
    if unasked is not None and notes is not None:
        notes.append(
            f"cannot ask {unasked}, so whether the repository holds {number} there was not "
            "established; it was checked against what could be read"
        )
    if holders:
        named = "; ".join(f"{ident} {where}" for ident, where in holders)
        raise AuthoringError(
            f"{number} is already held: {named}. A number names one entry, and two that "
            "share one are a collision `validate` fails and `renumber` has to move. Leave "
            "--id off to be allocated a free one, or pass --force if the reuse is deliberate."
        )


def refuse_to_write_outside_the_root(ledger, path):
    """A write is refused when the file it lands on is not under the project root.

    `confined()` establishes this for the paths a configuration names; an entry file is
    the other way in. A clone carries `ledger/entries/A0001-x.md -> ../../../elsewhere` as
    readily as it carries a `claims-ledger.toml`, and following one on `sha --write` or
    `propagate --write` rewrites a file the project does not contain. Reads are left
    alone: an entry symlinked in from outside is read normally, and only the write is
    the thing this package promises not to do
    (L0068-a-write-is-refused-through-an-escaping-link-and-a-read-is-not, cites-as-live).
    """
    outside = leaves_root(ledger.config.root, path)
    if outside is not None:
        raise AuthoringError(
            f"{path} leads to {outside}, outside the project root {ledger.config.root}; "
            "nothing is written through a link that leaves the project"
        )


def computed_sha(path):
    return parse_entry(Path(path)).computed_sha()


def is_committed(ledger, path):
    """(whether some commit of this repository holds this file, why it could not be asked).

    An entry that is committed has an immutable frozen region, and rewriting its
    fingerprint there is not an edit the checkers will forgive. `git()` answers None for
    a file git does not have and for a git that could not be run, and read as the first,
    a `sha --write` with no git on PATH rewrote the frozen region of a committed entry,
    exited 0 and said nothing. The answer is None when git could not be asked, which is
    not a `no` (L0069-an-unaskable-git-is-not-read-as-not-committed, cites-as-live). One
    bit carries that here: `committed_paths` walks, and a walk that failed comes back
    without a set rather than with an empty one.

    At HEAD, once, and that was the defect. This asked `rev-parse --verify --quiet
    HEAD:<rel>`, which answers about one commit, while the reach that matters is every
    commit the repository holds — during a merge, an entry the incoming side committed is
    on `MERGE_HEAD` and not on HEAD, so it read as uncommitted, `resolve` refused the
    merge, and `sha --write` would have rewritten the Grounds of an entry already in
    history (issue #59). It is a membership read of `committed_paths` now, over every ref
    and every operation in progress.

    What `rev-parse --verify` was chosen for is kept. It resolved a name through the tree
    without checking the object is *present*, so an entry whose loose blob is gone still
    read as committed — what makes a region immutable is that a commit names it, not
    whether this checkout can still read the bytes. The walk is a tree diff and answers
    the same way: measured on git 2.43.0, with the blob deleted, `--name-only` still names
    the path while `cat-file -e` exits 1
    (L0070-committed-means-a-commit-names-it-not-that-the-bytes-are-here, cites-as-live).

    And the negative is refused a second time while an operation is in progress, which is
    where a walk this package has not been taught about would otherwise produce a `no`
    about a file that is there. (docs/audits/ARCH-AUDIT.md, QE14-4.)
    """
    repo = ledger.repo
    if not repo:
        # "No repository" is only "nothing was skipped" when there is no repository
        # anywhere. A ledger inside somebody else's repository has a history, and this
        # returning `not committed` is what let `sha --write` rewrite the frozen region of
        # an entry that repository had already committed
        # (L0071-a-ledger-inside-another-repository-still-has-a-history, cites-as-live).
        # (docs/audits/ARCH-AUDIT.md, finding 3.)
        #
        # Answered against that repository rather than refused over it: an entry path is a
        # path in the tree, not an evidence pointer read out of a pin, so nothing here
        # needs the rebasing that adopting the repository wholesale would.
        # Walked from the entry's own directory: this asks about a file, and the
        # directory holding it is the honest place to start. Handing the ledger root
        # down instead would have edited `restamp`, which L0007 pins.
        holder, why = enclosing_repository(Path(path).parent, Path(path).parent)
        if why is not None:
            return None, why
        if holder is None:
            return False, None
        repo = holder
    try:
        rel = Path(path).resolve().relative_to(Path(repo).resolve())
    except ValueError:
        return False, None  # outside the repository: git has nothing to say about it
    if (problem := git_problem(repo)) is not None:
        return None, problem
    # As git prints a path: `/`-separated from the repository root, and a string. The
    # walk's keys are what git wrote, so a Path compared against them is never equal and
    # every entry reads as uncommitted — which is the answer that licenses a rewrite.
    named = rel.as_posix()
    under = os.path.dirname(named) or "."
    seen, why = committed_paths(ledger, repo, under)
    if seen is None:
        return None, f"git could not list what it holds under {under} ({why})"
    if named in seen:
        return True, None
    heads = heads_in_progress(ledger, repo)
    if heads:
        # Nothing this run walked names the file, and a `no` here is what licenses a
        # rewrite of the frozen region. An operation in progress is exactly the state
        # where a walk can be incomplete for a reason this package did not anticipate —
        # a pseudo-ref of a git newer than this code — so inside one the negative is
        # downgraded to `could not be established` and the destructive decision is never
        # taken on it. Both callers already act on that: `sha --write` refuses and
        # `resolve` reports it rather than telling the author to recompute
        # (L0294-an-operation-in-progress-is-discovered-not-enumerated, cites-as-live).
        return None, f"{', '.join(heads)} is set, so an operation is in progress"
    return False, None  # no commit this repository holds names it: not committed


def anchors_to_fill(ledger, entry):
    """[(pointer as written, digest)] for every evidence pointer of the entry whose anchor
    is the `=?` placeholder — in the Grounds and in each verdict's evidence alike — with
    the digest of its section as the working tree has it, which is the datum the anchor
    will name.

    Computed from the tree and not from any commit, which is what lets the entry land in
    the same commit as the code it rests on. A pointer whose text the tree does not hold
    — a path that is not a file, one that cannot be read, a section that is not in it —
    is refused by name before anything is written, since an anchor filled from nothing
    would name nothing and `validate` would have no way to tell it from a real one
    (L0207-sha-write-fills-a-pending-anchor-from-the-tree, cites-as-live).
    """
    out = []
    pointers = list(entry.grounds) + [(v.pointer.raw, v.pointer) for v in entry.verdicts]
    for raw, p in pointers:
        if p is None or p.type not in ledger.config.evidence_types:
            continue
        if p.digest != PENDING_ANCHOR:
            continue
        path = ledger.tree / p.target
        if not path.is_file():
            raise AuthoringError(
                f"`{raw}`: {p.target} is not a file in the working tree, so the anchor "
                "cannot be computed; nothing was written"
            )
        text, unreachable = read_artifact(path)
        if text is None:
            why = unreachable or "it is not UTF-8 text"
            raise AuthoringError(
                f"`{raw}`: {p.target} could not be read ({why}), so the anchor cannot be "
                "computed; nothing was written"
            )
        if p.sectioned:
            digest = section_digest(text, ledger.config, p.type, p.section)
            if digest is None:
                raise AuthoringError(
                    f"`{raw}`: {p.target} has no section {p.section!r} in the working "
                    "tree, so the anchor cannot be computed; nothing was written"
                )
        else:
            digest = digest_of(text)
        out.append((raw, digest))
    return out


def restamp(ledger, path, write=False, force=False):
    """(declared, computed, changed, filled). With `write`, the declared value is replaced
    by the computed one, and every `=?` anchor is filled with the digest of its section as
    the tree has it — `filled` is those pointers as they were written. Both are refused on
    an entry git already has, unless `force`, when they would touch the frozen region: the
    fingerprint always does, an anchor in the Grounds does, and an anchor in a verdict's
    evidence sits below the APPEND marker and is filled on a committed entry as any other
    append is written there
    (L0007-sha-write-refuses-a-committed-entry, cites-as-live)
    (L0207-sha-write-fills-a-pending-anchor-from-the-tree, cites-as-live)."""
    path = Path(path)
    entry = parse_entry(path)
    declared = entry.front.get("verbatim_sha", "")
    computed = entry.computed_sha()
    if not write:
        return declared, computed, False, []
    pending = anchors_to_fill(ledger, entry)
    if declared == computed and not pending:
        return declared, computed, False, []
    in_grounds = {raw for raw, _ in entry.grounds}
    frozen = declared != computed or any(raw in in_grounds for raw, _ in pending)
    if frozen:
        committed, unasked = is_committed(ledger, path)
        if unasked is not None and not force:
            raise AuthoringError(
                f"{unasked}, so whether git already has {ledger.config.relative(path)} could "
                "not be established. The region above the APPEND marker is immutable once the "
                "entry is committed, and this run has no way to find out whether it is; "
                "nothing was written. Pass --force to write anyway."
            )
        if committed and not force:
            raise AuthoringError(
                f"{ledger.config.relative(path)} is committed: the region above the APPEND "
                "marker is immutable, and a new fingerprint or a new anchor there is a new "
                "entry. Supersede it, or pass --force if the commit is not yet pushed and you "
                "are fixing it in place."
            )
    # Read and written with the file's own line endings: `sha --write` replaces one
    # line, and every other byte of the entry — including the ones that say how its lines
    # end — is none of its business. A CRLF entry rewritten as LF is a rewrite of an
    # immutable frozen region that no checker used to be able to see.
    text = read_text_exact(path)
    new = text
    if declared != computed:
        new, n = re.subn(
            # The trailing `\r` of a CRLF line is looked at and left alone.
            rf"^verbatim_sha: {re.escape(declared)}(?=\r?$)",
            f"verbatim_sha: {computed}",
            new,
            count=1,
            flags=re.MULTILINE,
        )
        if not n:
            raise AuthoringError(f"no `verbatim_sha: {declared}` line to replace in {path}")
    for raw, digest in pending:
        # The placeholder is the pointer's last word, and only a Grounds line or a
        # verdict's evidence line is a pointer: a Warrant sentence that happens to end
        # in the same text is prose in the frozen region, and a fill that reached it
        # rewrote what check_history holds immutable, on a committed entry, at exit 0.
        stated = raw[: -len(PENDING_ANCHOR)] + digest
        new = re.sub(
            r"^(- |[ \t]+evidence: )" + re.escape(raw) + r"(?=\r?$)",
            lambda m, s=stated: m.group(1) + s,
            new,
            flags=re.MULTILINE,
        )
    refuse_to_write_outside_the_root(ledger, path)
    try:
        write_text_atomically(path, new)
    except OSError as exc:
        raise AuthoringError(f"cannot write {path} ({exc.strerror or exc})") from exc
    return declared, computed, declared != computed, [raw for raw, _ in pending]


def register_source(
    ledger,
    source_id,
    bytes_path,
    source_type,
    citation,
    authors=None,
    speaker=None,
    retrieved=None,
    url=None,
    extraction=None,
    keep_path=False,
):
    """Append a registry row and put the bytes where the resolver will look for them,
    in one call: a row whose bytes were never stored is a Backing check that cannot run
    (L0064-a-registry-row-and-its-bytes-are-written-together, cites-as-live).

    With `keep_path` the row names the file (a committed fixture); otherwise the bytes
    are copied into the cache under their sha256, which is what a real source gets:
    the row is committed and the bytes are not.

    That split is why an id already in the registry is not simply refused. A fresh clone
    has every row and none of the bytes, and `check` then fails per quotation until they
    are back; the recovery README.md documents is to re-run this on the bytes each row's
    url and extraction name. The duplicate-id refusal made that impossible, so the
    documented repair could not be performed by any command. The bytes decide now —
    offered the ones the row names, this restores the cache slot and appends nothing, and
    offered any others it refuses as before. Returns `(row, stored, restored)`.

    The registry has to be a regular file, and that is settled before anything is
    written (L0074-the-registry-must-be-a-regular-file, cites-as-live). The bytes have to
    decode as UTF-8, because a quotation resolves in text and a source nothing can read
    as text is one no Backing block could ever be checked against
    (L0075-source-bytes-decode-as-text-or-the-registration-is-refused, cites-as-live).
    """
    bytes_path = Path(bytes_path)
    if not bytes_path.is_file():
        raise AuthoringError(f"no file at {bytes_path}")
    # Checked before anything is written, and before the append that would otherwise meet
    # it: open("a") on a FIFO with no reader blocks forever, which in a hook is a wedged
    # commit with no output, and a directory there is an IsADirectoryError asking the user
    # to file a bug. The reads already refuse a registry that is not a regular file.
    if ledger.registry.exists() and not ledger.registry.is_file():
        raise AuthoringError(
            f"{ledger.config.relative(ledger.registry)} is not a regular file; "
            "the source registry is a JSON-lines file this command appends to"
        )
    rows = load_registry(ledger.registry)
    data = bytes_path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuthoringError(f"{bytes_path} is not UTF-8 text; quotations resolve in text") from exc

    # The bytes decide, because the registry is content-addressed and the row already says
    # which bytes it is about. Offered the bytes the row names, this is the fresh-clone
    # recovery README.md documents — the rows are committed, `ledger/cache/` is not, and
    # `source add` on the bytes each row's url and extraction name is how they come back.
    # Offered anything else it is a second registration under a taken id, which is what the
    # refusal was always for
    # (L0303-a-registered-source-restores-its-own-bytes, cites-as-live).
    restoring = rows.get(source_id)
    if restoring is not None:
        if restoring.get("sha256") != digest:
            raise AuthoringError(
                f"source id `{source_id}` is already registered, and these are not its "
                f"bytes: the row names sha256:{str(restoring.get('sha256'))[:12]}… and "
                f"{bytes_path} is sha256:{digest[:12]}…"
            )
        if "bytes" in restoring:
            raise AuthoringError(
                f"source id `{source_id}` names {restoring['bytes']} in the tree rather "
                "than the cache; there is nothing to restore, and a file the row names is "
                "committed with it"
            )
        if keep_path:
            raise AuthoringError(
                f"source id `{source_id}` is registered against the cache; restoring it "
                "cannot also move it into the tree"
            )
        for field, given in (("type", source_type), ("citation", citation)):
            if given is not None and given != restoring.get(field):
                raise AuthoringError(
                    f"source id `{source_id}` is already registered with {field} "
                    f"{restoring.get(field)!r}; restoring its bytes cannot restate it as "
                    f"{given!r}"
                )
        row = restoring
    else:
        for field, given in (("--type", source_type), ("--citation", citation)):
            if given is None:
                raise AuthoringError(f"{field} is required to register a new source")
        row = {"id": source_id, "type": source_type}
        if authors:
            row["authors"] = list(authors)
        if speaker:
            row["speaker"] = speaker
        row["citation"] = citation
        row["retrieved"] = retrieved or datetime.now().astimezone().date().isoformat()
        if url:
            row["url"] = url
        if extraction:
            row["extraction"] = extraction
        row["sha256"] = digest
    if keep_path:
        row["bytes"] = ledger.config.relative(bytes_path)
        stored = bytes_path
    else:
        if not ledger.cache:
            raise AuthoringError("this ledger has no cache; register with --keep-path instead")
        stored = ledger.cache / digest
        # Asked before the cache slot is so much as read. Every write in this package goes
        # through one funnel now, and the funnel's own docstring says where the link leads
        # is the caller's question — but this caller had never asked it, so a dangling
        # symlink planted at the content-addressed slot sent `source add` outside the
        # project root, exit 0, naming the in-root path it had not written to. The check
        # precedes the "are these already the right bytes" read as well, so a *live* link
        # out of the root is refused rather than quietly accepted as a cache hit.
        refuse_to_write_outside_the_root(ledger, stored)
        try:
            ledger.cache.mkdir(parents=True, exist_ok=True)
            # The cache is content-addressed, so a file already under this name should be
            # these bytes — but an interrupted `source add` leaves one that is not, and
            # trusting the name meant the retry exited 0 over bytes it never wrote and
            # wrote a row whose sha256 described nothing on disk. The bytes are checked,
            # and the copy goes through a temporary name so a second interruption cannot
            # leave a third state
            # (L0076-a-cache-slot-is-verified-rather-than-trusted-by-name, cites-as-live).
            if not stored.exists() or hashlib.sha256(stored.read_bytes()).hexdigest() != digest:
                write_bytes_atomically(stored, data)
        except OSError as exc:
            raise AuthoringError(
                f"cannot store the bytes at {ledger.config.relative(stored)} "
                f"({exc.strerror or exc})"
            ) from exc

    if restoring is None:
        append_registry_row(ledger, row)
    return row, stored, restoring is not None


def append_registry_row(ledger, row):
    """One JSON line onto `sources.jsonl`, as a line.

    The registry is JSON lines, and a line needs a newline before it. Appended without
    one — after an editor, a script, or this command's own interrupted write left the
    file without a final newline — the new row was glued onto the previous one, both were
    destroyed, every later command exited 2 with `not a JSON object`, and the run that
    did it printed `registered …` and exited 0. So the last byte is looked at, and the
    separator is supplied when it is missing
    (L0072-a-registry-row-is-appended-as-a-line, cites-as-live).

    A write that fails partway is undone rather than left: the file is put back to the
    length it had, so a registry this command could not extend is still a registry
    (L0073-a-failed-registry-append-is-undone, cites-as-live). A read-only ledger
    directory is an ordinary condition — a shared checkout, a directory owned by someone
    else — and not one to ask for a bug report over.
    """
    addition = json.dumps(row, ensure_ascii=False) + "\n"
    try:
        ledger.registry.parent.mkdir(parents=True, exist_ok=True)
        size = ledger.registry.stat().st_size if ledger.registry.exists() else 0
        if size and not _ends_in_a_newline(ledger.registry):
            addition = "\n" + addition
        try:
            with ledger.registry.open("a", encoding="utf-8") as fh:
                fh.write(addition)
        except OSError:
            with contextlib.suppress(OSError), ledger.registry.open("r+b") as fh:
                fh.truncate(size)
            raise
    except OSError as exc:
        raise AuthoringError(
            f"cannot append to {ledger.config.relative(ledger.registry)} ({exc.strerror or exc})"
        ) from exc


def _ends_in_a_newline(path):
    """The last byte of a non-empty file, read as one byte rather than as the whole
    registry: a project with thousands of sources appends to this file every time
    (L0077-the-registrys-last-byte-is-read-as-one-byte, cites-as-live)."""
    with path.open("rb") as fh:
        fh.seek(-1, os.SEEK_END)
        return fh.read(1) == b"\n"
