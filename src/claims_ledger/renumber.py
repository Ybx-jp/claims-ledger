"""Reconciling two checkouts that minted one number, before the branch merges.

Allocation asks the repository now, so two sessions are not handed the same number in
the ordinary course of work (L0233-an-id-is-allocated-above-the-whole-repository,
cites-as-live). This is what is left when it happens anyway — two branches that were cut
before the question was asked, a mint over a repository that was offline, two sessions
minting in the same second.

The repair rewrites the branch that has not merged yet, so the entry is *born* with the
id it will keep. That is the whole of why it is done here rather than in the merge: an
entry renamed after it is committed has its frozen region compared against the commit
that created the *new path*, which is the rename commit, so the comparison passes over
whatever else that commit changed. Renumbering in the merge would need that hole to stay
open. Renumbering the branch first needs nothing of the sort — every rewritten entry is
created, once, with its final id, and `validate` holds it to that commit ever after.

`docs/OPERATING.md` permits exactly this rewrite and no other: the commits are unmerged,
so nothing in the ledger's history pins them. What it warns of is the case where the
branch's *own* entries pin the branch's *own* commits by reference, and that is refused
here rather than left to the reader.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from .authoring import ids_in_the_repository, next_id
from .schema import (
    blob_text,
    git_blobs,
    git_call,
    git_env,
    git_hash_object,
    parse_entry,
    section_digest,
    selects_document,
)

OBJECT_RE = re.compile(r"\b[0-9a-f]{40}\b")


class RenumberError(Exception):
    """Something about the branch that has to be settled before it can be rewritten."""


class RepositoryUnreadable(RenumberError):
    """A question git declined, so what the repository holds is unknown.

    Told apart from every other refusal because a merge guard has to answer differently:
    a branch this checkout cannot plan is not the guard's business and the merge proceeds,
    while a repository that could not be read is the one state in which the guard knows
    nothing — and allowing a merge out of ignorance is the false pass this package exists
    to refuse (L0249-a-guard-that-could-not-read-the-repository-does-not-allow-the-merge,
    cites-as-live).
    """


@dataclass(frozen=True)
class Renumbering:
    """What a renumber would do, decided before anything is written.

    `mapping` is old id to new id, both whole ids: the slug is the author's and is kept,
    and only the number moves. `commits` is every commit the rewrite replaces, oldest
    first, which is every commit the branch has that `onto` does not — not only the ones
    that touch an entry, because a commit whose parent is rewritten is rewritten too.
    """

    onto: str
    ref: str
    branch: str
    base: str
    commits: tuple
    mapping: dict

    @property
    def empty(self):
        return not self.mapping


def _lines(answer):
    return [line for line in answer.out.splitlines() if line.strip()]


def _resolve(repo, ref):
    answer = git_call(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    if not answer.ok or not answer.out.strip():
        raise RenumberError(f"`{ref}` does not name a commit in this repository")
    return answer.out.strip()


def entry_ids_at(repo, commit, rel_entries):
    """Every entry id the tree at `commit` holds, by filename.

    The filename rather than the frontmatter, because that is what a rename has to move
    and because `validate` holds the two to each other anyway; reading the blobs to ask
    the same question would cost one object per entry per commit.
    """
    answer = git_call(
        repo, "ls-tree", "-r", "--name-only", commit, "--", f":(literal){rel_entries}"
    )
    if not answer.ok:
        raise RenumberError(f"git could not list the entries at {commit[:7]} ({answer.why})")
    return {Path(line).stem for line in _lines(answer)}


def tree_files(repo, commit):
    """[(mode, object id, path)] for every file in the tree at `commit`."""
    answer = git_call(repo, "ls-tree", "-r", "--full-tree", commit)
    if not answer.ok:
        raise RenumberError(f"git could not list the tree at {commit[:7]} ({answer.why})")
    out = []
    for line in _lines(answer):
        meta, _, path = line.partition("\t")
        mode, kind, oid = meta.split()
        if kind == "blob":
            out.append((mode, oid, path))
    return out


def substitutions(mapping):
    """[(pattern, replacement, whole id only)] for the ids that move.

    Two shapes, because a citation may name either. The whole id is distinctive enough to
    be substituted wherever it appears — a test that names one, a changelog line, a
    comment — and the bare number is not, so it is rewritten only where this package
    knows an id is what it means: the entries, and the documents a citation is read from
    (L0236-a-whole-id-is-rewritten-anywhere-and-a-bare-number-only-where-it-is-read,
    cites-as-live).
    """
    out = []
    for old, new in sorted(mapping.items()):
        # `\b` is the wrong right-hand boundary for an id: a slug ends in a word
        # character and a hyphen is not one, so `\bA0002-beta\b` matches the front of
        # `A0002-beta-claim` and renumbers a different entry. Measured: substituting
        # A0002-beta for A0003-beta over `id: A0002-beta-claim` produced
        # `id: A0003-beta-claim`. The right-hand side has to refuse a hyphen as well as a
        # word character, because either one means the id runs on
        # (L0246-an-id-is-substituted-only-where-it-is-the-whole-id, cites-as-live).
        out.append((re.compile(rf"\b{re.escape(old)}(?![\w-])"), new, False))
        old_number, new_number = old.split("-", 1)[0], new.split("-", 1)[0]
        out.append((re.compile(rf"\b{re.escape(old_number)}(?![\w-])"), new_number, True))
    return out


def substitute(text, subs, ids_are_read_here):
    """`text` with every id in `subs` rewritten. A bare number is rewritten only where a
    number is read as an id — the caller decides that, per path."""
    for pattern, replacement, number_only in subs:
        if number_only and not ids_are_read_here:
            continue
        text = pattern.sub(replacement, text)
    return text


def anchored_pointers(entry):
    """[(the text carrying it, pointer)] for every by-value anchor an entry holds.

    The Grounds *and* each verdict's evidence. `freshness` compares a ground from the
    latest corroborating verdict that names its section once one exists, and from the
    ground's own pin only until then
    (L0195-the-latest-corroboration-is-where-a-ground-was-last-read, cites-as-live), so
    re-pinning the Grounds alone would leave the pointer the checker actually compares
    against naming text the rewrite replaced — and the entry would come out of its own
    renumber flagged (L0247-a-renumber-re-pins-every-anchor-freshness-may-compare-from,
    cites-as-live).
    """
    out = [(raw, pointer) for raw, pointer in entry.grounds]
    out += [(v.evidence, v.pointer) for v in entry.verdicts if v.evidence]
    return out


def reanchor(text, before, after, config, decided=None):
    """An entry's text with every by-value anchor re-pinned that moved by the renumber
    alone, and no other.

    The proof, rather than a re-pin on trust: the anchor is recomputed over the section
    as the rewritten tree has it, *with the substitution undone*. When that reproduces the
    anchor the entry already carries, the only thing that changed inside the section was
    the id, and the new digest is the same reading of the same text. When it does not,
    something else in the span moved too, the anchor is left exactly as written, and
    `freshness` flags it for a person to read — which is the report this package exists to
    make rather than one to absorb
    (L0238-an-anchor-is-re-pinned-only-where-the-id-is-proved-to-be-the-whole-change,
    cites-as-live).

    `before` and `after` are `{path: text}` for the artifacts this entry may rest on, as
    the tree held them and as the rewrite leaves them.

    `decided` carries the answer across commits, and it is not an optimisation. The
    rewrite visits each commit with that commit's own tree, and the same entry's span can
    be one thing where the entry is created and another two commits later — a second
    citation landing in it, say. Deciding per commit then writes one frozen region at the
    creating commit and a different one after it, which is exactly what `validate`
    refuses; measured before this, a branch that renumbered two entries citing one
    section came out of its own rewrite with `differs from the blob at the creating
    commit`. So each anchor is decided once, at the first commit that carries it, and
    every later commit is given the same answer — which is also what the original history
    did, since a frozen anchor never moved on its own
    (L0252-an-anchor-is-decided-once-for-the-whole-rewrite, cites-as-live).
    """
    entry = parse_entry(Path("in-memory.md"), text)
    out = text
    for raw, pointer in anchored_pointers(entry):
        if pointer is None or not pointer.by_value or not pointer.section:
            continue
        if not config.is_sectioned(pointer.type) or pointer.target not in after:
            continue
        key = (entry.id, raw)
        if decided is not None and key in decided:
            settled = decided[key]
            if settled is not None:
                out = out.replace(raw, settled, 1)
            continue
        anchored = pointer.anchor.lstrip("=")
        now = section_digest(after[pointer.target], config, pointer.type, pointer.section)
        was = section_digest(before[pointer.target], config, pointer.type, pointer.section)
        settled = None
        if now is not None and now != anchored and was == anchored:
            # the section as the rewrite leaves it, with the substitution undone, is the
            # text the anchor already names: the id was the whole of the change
            settled = raw.replace(pointer.anchor, f"={now}")
            out = out.replace(raw, settled, 1)
        if decided is not None:
            decided[key] = settled
    return out


def _commit_meta(repo, commit):
    """(environment naming the original author and committer, message)."""
    answer = git_call(repo, "log", "-1", "--format=%an%x00%ae%x00%aI%x00%cn%x00%ce%x00%cI", commit)
    if not answer.ok:
        raise RenumberError(f"git could not read {commit[:7]} ({answer.why})")
    an, ae, ai, cn, ce, ci = answer.out.strip("\n").split("\0")
    message = git_call(repo, "log", "-1", "--format=%B", commit)
    if not message.ok:
        raise RenumberError(f"git could not read the message of {commit[:7]} ({message.why})")
    return {
        "GIT_AUTHOR_NAME": an,
        "GIT_AUTHOR_EMAIL": ae,
        "GIT_AUTHOR_DATE": ai,
        "GIT_COMMITTER_NAME": cn,
        "GIT_COMMITTER_EMAIL": ce,
        "GIT_COMMITTER_DATE": ci,
    }, message.out


def _parents(repo, commit):
    answer = git_call(repo, "rev-list", "--parents", "-n", "1", commit)
    if not answer.ok:
        raise RenumberError(f"git could not read the parents of {commit[:7]} ({answer.why})")
    return answer.out.split()[1:]


def plan(ledger, onto, branch="HEAD"):
    """What renumbering this branch would move, or a RenumberError saying why it cannot.

    The receiving side keeps its ids. That is what "merged first wins" means once it is
    stated so that it decides anything: a merge is never symmetric, so the branch being
    merged is the one that moves, three open branches are three sequential merges, and no
    arbiter is needed (L0239-the-receiving-side-keeps-its-ids, cites-as-live).
    """
    repo = ledger.repo
    if not repo:
        raise RenumberError("not a git repository; there is no branch to rewrite")
    onto_commit, tip = _resolve(repo, onto), _resolve(repo, branch)
    merge_base = git_call(repo, "merge-base", onto_commit, tip)
    if not merge_base.ok or not merge_base.out.strip():
        raise RenumberError(f"`{branch}` and `{onto}` share no history")
    base = merge_base.out.strip()
    if base == tip:
        raise RenumberError(
            f"`{branch}` is already an ancestor of `{onto}`; these commits are merged, and "
            "rewriting merged history is what this repository forbids"
        )
    listed = git_call(repo, "rev-list", "--reverse", "--topo-order", f"{onto_commit}..{tip}")
    if not listed.ok:
        raise RenumberError(f"git could not list the commits to rewrite ({listed.why})")
    commits = tuple(_lines(listed))
    if not commits:
        raise RenumberError(f"`{branch}` has no commits `{onto}` does not")

    rel_entries = os.path.relpath(ledger.entries_dir, repo)
    at_tip = entry_ids_at(repo, tip, rel_entries)
    introduced = at_tip - entry_ids_at(repo, base, rel_entries)
    receiving = {ident.split("-", 1)[0] for ident in entry_ids_at(repo, onto_commit, rel_entries)}
    # A number the receiving side holds, and a number the branch manages to hold twice by
    # itself — two sessions that both minted into one branch. `check_numbers` names this
    # command for either, so this command answers for either; the first id in sort order
    # keeps the number and the rest move, which is the same rule as "the receiving side
    # keeps its ids" applied where there is no other side
    # (L0250-a-number-a-branch-holds-twice-is-a-collision-too, cites-as-live).
    seen, doubled = set(), set()
    for ident in sorted(at_tip):
        number = ident.split("-", 1)[0]
        if number in seen:
            doubled.add(ident)
        seen.add(number)
    colliding = sorted(
        {i for i in introduced if i.split("-", 1)[0] in receiving} | (doubled & introduced)
    )

    mapping = {}
    if colliding:
        held, unasked = ids_in_the_repository(ledger)
        if unasked is not None:
            raise RepositoryUnreadable(
                f"cannot ask {unasked}, so a free id cannot be chosen; a renumber that "
                "allocates over a repository it could not read moves one collision onto "
                "another"
            )
        taken = [_Stem(name) for name in held | introduced | entry_ids_at(repo, tip, rel_entries)]
        for old in colliding:
            fresh = next_id(taken, ledger.config.archived_prefixes)
            mapping[old] = f"{fresh}-{old.split('-', 1)[1]}"
            taken.append(_Stem(mapping[old]))
    return Renumbering(
        onto=onto_commit, ref=branch, branch=tip, base=base, commits=commits, mapping=mapping
    )


@dataclass(frozen=True)
class _Stem:
    """An id standing in for an entry, for the allocator, which reads only the id."""

    id: str

    @property
    def path(self):
        return Path(self.id)


def refusals(ledger, renumbering):
    """Everything that makes this rewrite the wrong thing to do, as sentences.

    Asked before anything is written and reported together, because a reader who has to
    decide whether to rewrite a branch wants the whole list rather than the first item of
    it.

    The one `docs/OPERATING.md` warns of is the branch whose own entries pin the branch's
    own commits: a ground stated by reference names a commit, the rewrite replaces that
    commit, and the evidence is then gone from the repository. That costs a supersession
    per ground rather than the re-read a moved section costs, so it is refused here with
    the entry and the commit named rather than left for `resolve` to report afterwards
    (L0237-a-rewrite-that-would-drop-a-pinned-commit-is-refused, cites-as-live).
    """
    repo, out = ledger.repo, []
    rewritten = set(renumbering.commits)

    mine = git_call(repo, "rev-parse", "--symbolic-full-name", renumbering.ref)
    ours = mine.out.strip() if mine.ok else ""
    others = git_call(
        repo, "for-each-ref", "--format=%(refname)", "--contains", renumbering.commits[0]
    )
    if others.ok:
        shared = sorted(ref for ref in _lines(others) if ref != ours)
        if shared:
            out.append(
                "the commits to rewrite are also reachable from "
                + ", ".join(shared)
                + "; rewriting moves one ref and leaves the others holding the commits this "
                "replaces, which is how a rewrite comes to be merged back in later"
            )

    rel_entries = os.path.relpath(ledger.entries_dir, repo)
    files = [p for _m, _o, p in tree_files(repo, renumbering.branch) if p.startswith(rel_entries)]
    blobs, _failed = git_blobs(repo, [f"{renumbering.branch}:{p}" for p in files], env=git_env())
    pinned = set()
    for spec, data in blobs.items():
        for found in OBJECT_RE.findall(blob_text(data)):
            if found in rewritten:
                pinned.add((spec.split(":", 1)[1], found))
    for path, commit in sorted(pinned):
        out.append(
            f"{path} names commit {commit[:7]} by reference, and this rewrite replaces it; "
            "a ground stated by reference into a commit the rewrite drops loses the evidence "
            "it rests on, and that costs a supersession rather than a re-read"
        )

    config_file = ledger.config.source
    if config_file is not None:
        rel_config = os.path.relpath(config_file, repo)
        changed = git_call(
            repo,
            "rev-list",
            f"{renumbering.base}..{renumbering.branch}",
            "--",
            f":(literal){rel_config}",
        )
        if changed.ok and changed.out.strip():
            out.append(
                f"{rel_config} changes on this branch, and the rewrite reads one "
                "configuration for every commit; which paths are documents would be "
                "decided by the wrong one"
            )
    return out


def rewrite(ledger, renumbering, index_path):
    """Replace every commit on the branch with one that carries the new ids, and return
    the new tip.

    Each entry is *created* in the commit that first carried it, under the id it will
    keep, which is the whole reason the repair is done to the branch rather than to the
    merge: `validate` compares an entry's frozen region against the blob at the commit
    that created its path, so an entry renamed after it is committed is compared against
    the rename commit and whatever else that commit changed rides in unchecked. A branch
    rewritten before it merges never opens that window
    (L0235-a-renumber-rewrites-the-branch-rather-than-the-merge, cites-as-live).

    Nothing is written to the working tree and no ref is moved here: the caller does
    that, so a rewrite that fails half way leaves the branch exactly where it was, with
    the commits it managed to write unreferenced and collectable
    (L0240-a-rewrite-builds-every-commit-before-it-moves-the-branch, cites-as-live).
    """
    repo, config = ledger.repo, ledger.config
    subs = substitutions(renumbering.mapping)
    rel_entries = os.path.relpath(ledger.entries_dir, repo)
    replaced, decided = {}, {}

    for commit in renumbering.commits:
        files = tree_files(repo, commit)
        blobs, failed = git_blobs(repo, [f"{commit}:{p}" for _m, _o, p in files], env=git_env())
        if failed:
            raise RenumberError(
                f"git did not answer for {len(failed)} object(s) at {commit[:7]}: "
                + "; ".join(f"{spec} ({why})" for spec, why in sorted(failed.items())[:3])
            )
        before, after, modes = {}, {}, {}
        for mode, _oid, path in files:
            data = blobs[f"{commit}:{path}"]
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                continue  # not text; an id is not in it and nothing here can rewrite it
            modes[path] = mode
            before[path] = text
            read_here = path.startswith(rel_entries) or selects_document(path, config)
            after[path] = substitute(text, subs, read_here)

        for path, text in list(after.items()):
            if path.startswith(rel_entries):
                after[path] = reanchor(text, before, after, config, decided)

        env = git_env(index=True) | {"GIT_INDEX_FILE": str(index_path)}
        read = git_call(repo, "read-tree", commit, env=env)
        if not read.ok:
            raise RenumberError(f"git could not read the tree of {commit[:7]} ({read.why})")
        for path, text in sorted(after.items()):
            renamed = _renamed(path, rel_entries, renumbering.mapping)
            if text == before[path] and renamed is None:
                continue
            blob = git_hash_object(repo, text.encode("utf-8"), env=env)
            if blob is None:  # pragma: no cover - hash-object failing is git failing
                raise RenumberError(f"git could not store the rewritten {path}")
            if renamed is not None:
                _update_index(repo, env, "--force-remove", path)
                _update_index(repo, env, "--add", "--cacheinfo", f"{modes[path]},{blob},{renamed}")
            else:
                _update_index(repo, env, "--add", "--cacheinfo", f"{modes[path]},{blob},{path}")
        tree = git_call(repo, "write-tree", env=env)
        if not tree.ok:
            raise RenumberError(f"git could not write the rewritten tree ({tree.why})")

        identity, message = _commit_meta(repo, commit)
        parents = [replaced.get(p, p) for p in _parents(repo, commit)]
        args = ["commit-tree", tree.out.strip()]
        for parent in parents:
            args += ["-p", parent]
        made = git_call(repo, *args, "-m", message.rstrip("\n"), env=git_env() | identity)
        if not made.ok:
            raise RenumberError(f"git could not write the rewritten commit ({made.why})")
        replaced[commit] = made.out.strip()
    return replaced[renumbering.commits[-1]]


def _update_index(repo, env, *args):
    answer = git_call(repo, "update-index", *args, env=env)
    if not answer.ok:
        raise RenumberError(f"git could not update the index ({answer.why})")


def _renamed(path, rel_entries, mapping):
    """The path an entry moves to, or None when it does not move."""
    if not path.startswith(rel_entries):
        return None
    stem = Path(path).stem
    if stem not in mapping:
        return None
    return str(Path(path).parent / f"{mapping[stem]}{Path(path).suffix}")


def describe(renumbering, refused):
    """The plan as lines for a reader, whether or not it is going to be carried out."""
    lines = []
    if renumbering.empty:
        lines.append("no number on this branch is held anywhere else in the repository")
        return lines
    lines.append(
        f"{len(renumbering.mapping)} id(s) collide with `{renumbering.onto[:7]}` and would move, "
        f"rewriting {len(renumbering.commits)} commit(s):"
    )
    lines += [f"  {old}  ->  {new}" for old, new in sorted(renumbering.mapping.items())]
    for refusal in refused:
        lines.append(f"REFUSED: {refusal}")
    return lines


def checkout_holding(repo, ref, commits=()):
    """The checkout that would be stranded by this rewrite, or None.

    Two ways to be stranded, and the second is the one a `branch` line cannot show. A
    worktree with the branch checked out by name moves under it; a worktree sitting
    *detached* on one of the commits being replaced keeps a HEAD that no ref will name
    once the rewrite lands, and `git worktree list --porcelain` reports that one as
    `detached` with no branch at all
    (L0251-a-rewrite-refuses-a-checkout-it-would-strand-by-name-or-detached,
    cites-as-live).
    """
    listed = git_call(repo, "worktree", "list", "--porcelain")
    if not listed.ok:
        raise RenumberError(f"git could not list the checkouts of this repository ({listed.why})")
    full = git_call(repo, "rev-parse", "--symbolic-full-name", ref)
    wanted = full.out.strip() if full.ok else ref
    replaced = set(commits)
    here, at, named, holders = None, None, False, []
    for line in [*listed.out.splitlines(), ""]:
        if line.startswith("worktree "):
            here, at, named = line[len("worktree ") :], None, False
        elif line.startswith("HEAD "):
            at = line[len("HEAD ") :].strip()
        elif line.startswith("branch "):
            named = line[len("branch ") :].strip() == wanted
        elif not line.strip() and here is not None:
            if named or at in replaced:
                holders.append(here)
            here, at, named = None, None, False
    # Every candidate, not the first: the first is this checkout, which is the one being
    # reset rather than the one being stranded, and stopping there hid every other.
    mine = Path(repo).resolve()
    return next((h for h in holders if Path(h).resolve() != mine), None)


def working_tree_changes(repo):
    """Whether this checkout has anything uncommitted, tracked or staged."""
    answer = git_call(repo, "status", "--porcelain", "--untracked-files=no")
    if not answer.ok:
        raise RenumberError(f"git could not read the state of the working tree ({answer.why})")
    return bool(answer.out.strip())


def branch_ref(repo, ref):
    """The full refname `ref` names, or a RenumberError when it does not name a branch.

    A detached HEAD is the case this exists for. `rev-parse --symbolic-full-name HEAD`
    answers `HEAD` when nothing is checked out by name, and moving *that* moves the
    detached head rather than a branch: the rewritten commits end up reachable only from
    HEAD, the branch that was being renumbered still names the originals, and the working
    tree is left holding the old content with the rewrite staged against it — reported, at
    the time, as a rewrite that had succeeded. A rewrite whose result no branch would name
    is refused before anything is written
    (L0248-a-rewrite-moves-a-branch-or-it-is-refused, cites-as-live).
    """
    full = git_call(repo, "rev-parse", "--symbolic-full-name", ref)
    name = full.out.strip() if full.ok else ""
    if not name.startswith("refs/heads/"):
        detached = " HEAD is detached" if name == "HEAD" or not name else ""
        raise RenumberError(
            f"`{ref}` does not name a branch{detached}; a rewrite has to leave its commits "
            "on a branch, so name one with --branch"
        )
    return name


def move_branch(repo, renumbering, tip):
    """Point the branch at the rewritten tip and put this checkout on it.

    `update-ref` is given the old value as well as the new, so a branch that moved while
    the rewrite was running is not overwritten by it — the rewrite read one history and
    would be writing over another.
    """
    ref = branch_ref(repo, renumbering.ref)
    moved = git_call(repo, "update-ref", ref, tip, renumbering.branch)
    if not moved.ok:
        raise RenumberError(f"git would not move {ref} ({moved.why})")
    head = git_call(repo, "symbolic-ref", "--quiet", "HEAD")
    if head.ok and head.out.strip() == ref:
        reset = git_call(repo, "reset", "--hard", "--quiet", tip)
        if not reset.ok:
            raise RenumberError(
                f"{ref} now names {tip[:7]}, but this checkout could not be put on it "
                f"({reset.why}); `git reset --hard {tip[:7]}` finishes it"
            )
