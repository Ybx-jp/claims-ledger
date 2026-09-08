# Agent-harness hooks

Two hooks for a coding-agent harness, for projects whose ledger pins claims to code. They
are **examples, not part of the package**: nothing installs them, nothing supports them,
and they are not in the wheel or the sdist. Copy them into your project and adapt.

They are here rather than in `src/` for two reasons. The hook-configuration format below
is one vendor's, and a checker that works from a plain interpreter should not grow a
dependency on anyone's agent harness. And these need `jq`, where the package needs
nothing at all — `claims-ledger` declares no runtime dependencies and the installed
pre-commit hook runs from a bare `python3`, which is a property worth keeping.

This repository uses them on itself; `.claude/settings.json` points at these files, so
what is documented here is what is actually run.

## What they are for

The five checkers are complete about what they check and silent about two things that
happen earlier:

**A drifted pin is found at commit time, not edit time.** The pre-commit hook is the
right place to *refuse* the commit, and the wrong place to *learn*: by then the edit is
finished and its author has moved on. `pin-guard.sh` runs `freshness` read-only after an
edit and reports drift while the edit is still in hand.

**Nothing notices prose that should have been an entry.** `references` checks citations
that were written; a sentence asserting a commitment and citing nothing passes every
check. No checker can close this — telling a promise from a description is a judgement —
so `pin-guard.sh` raises it once a session, on the first edit to a configured document,
and leaves the judgement where it belongs.

**A squash or rebase merge silently destroys every commit pin.** `resolve` reports it
afterwards, at which point the repair is a supersession per entry. `merge-guard.sh`
refuses the commands that do it. See `docs/OPERATING.md`, which is the authority; this
hook is one enforcement of what that document argues.

## Installing them (Claude Code)

Copy this directory into your project and add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [{ "type": "command",
                    "command": "$CLAUDE_PROJECT_DIR/examples/agent-harness/merge-guard.sh" }] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write|MultiEdit",
        "hooks": [{ "type": "command",
                    "command": "$CLAUDE_PROJECT_DIR/examples/agent-harness/pin-guard.sh" }] }
    ]
  }
}
```

Both scripts derive the project root from their own location, two directories up. Move
them and adjust the `..` count.

For another harness, the parts to replace are the input parsing (a JSON payload on stdin
carrying an event name, a session id and either a file path or a command) and the output
(`hookSpecificOutput.additionalContext` to say something, `permissionDecision: "deny"` to
refuse). What the hooks decide is in between, and is harness-independent.

## What is repository-specific in them

Nothing, by construction, and it is worth keeping it that way:

- The interpreter is discovered — a project virtualenv, then any `python3` that can
  import the package — and invoked as `python -m claims_ledger`, never as the
  `claims-ledger` console script. A console script in a virtualenv that is not active is
  not on PATH, and a hook that names it fails on every firing.
- Which files are documents is asked of the package. `pin-guard.sh` calls the same
  `tree_documents` the checkers call, so excludes, glob semantics and the rule that the
  ledger does not cite itself come along for free. A hook that restated any of that would
  drift from the checker it serves.

## Design notes worth keeping if you adapt them

**Throttle everything, on the right key.** An always-on reminder is wallpaper. Drift is
keyed on a digest of the finding, so unchanged drift is reported once and *new* drift
still speaks, and it goes quiet by itself once a verdict discharges the flag. The
new-claim reminder is keyed once per session.

**Never write.** `pin-guard.sh` runs `freshness` without `--write`. Appending a verdict is
a judgement about the ledger; a hook firing behind the author's back is not the place for
one, and the verdict it wrote would be indistinguishable from one a person meant.

**Never block on failure.** Every error path in `pin-guard.sh` exits 0 silently — no `jq`,
no interpreter, an unreadable config. A guard that can break the session is worse than no
guard. `merge-guard.sh` is the deliberate exception: refusing is its whole purpose.

**Anchor a text match at a command position.** `merge-guard.sh` reads a shell command as
text and cannot parse it. Matching the forbidden commands anywhere in the string made the
guard refuse the commit that introduced it, because the message quoted them. It now
matches only at the start of a line or just past a shell operator, and `merge-guard.cases`
holds thirteen expected verdicts — six refusals, seven near-misses that must pass,
including that one. Run them with `merge-guard-test.sh` after touching either file. A
guard whose behaviour is asserted rather than checked is a claim like any other, and this
package's answer to those is to check them.

**Known limit of that approach:** a heredoc line that *begins* with a forbidden command
still matches. Rare and visible, where a backticked mention inside prose is neither. The
guard also cannot reach the merge button on a hosting platform; disable squash and rebase
merges there as well. On GitHub that is `allow_squash_merge` and `allow_rebase_merge`.
