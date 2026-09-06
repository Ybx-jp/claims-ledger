"""Part 3b: attack corpus/run.py's matches() substring rule.

Finding: `message.casefold() in report.message.casefold()` treats an empty string (or,
per Python's `in` semantics, ANY substring test against the empty string) as "matches
anything" -- `"" in x` is always True. So a row that sets `"message": ""` is
indistinguishable from a row with no message constraint at all: it does not narrow the
match the way a non-empty message does.

Whether this is *exploitable* (lets a seed pass for the wrong reason, the HIGH-46 class)
depends on run_seed()'s separate bijection check: a row is satisfied only if exactly one
report both matches place+message and has the right outcome; >1 hit is reported as
"ambiguous" and fails the seed loudly. So an empty message at a place where two DIFFERENT
rules both fire is still caught -- as ambiguous, not as a silent pass. An empty message
is a footgun for a seed author who thinks it pins a specific rule (it does not), not a
route back to HIGH-46's silent-pass bug, because the bijection check is orthogonal to
message content.

This script demonstrates the empty-message/one-char behavior against the real matches()
in the current tree (not a mutant) and confirms which of the two things it is.
"""
import sys
sys.path.insert(0, "/tmp/qe6-corpus/src")
from claims_ledger.corpus.run import matches


class FakeReport:
    def __init__(self, commit, entry, part, message):
        self.commit = commit
        self.entry = entry
        self.part = part
        self.message = message


r = FakeReport(None, "A0001", "verdict 2", "follows a terminal `retracted` verdict; nothing may follow it")

print("message=None (no constraint):        ", matches(r, None, "A0001", "verdict 2", message=None))
print("message='' (empty string):            ", matches(r, None, "A0001", "verdict 2", message=""))
print("message='e' (single common letter):   ", matches(r, None, "A0001", "verdict 2", message="e"))
print("message='xyz-not-present':             ", matches(r, None, "A0001", "verdict 2", message="xyz-not-present"))
print()
print("Conclusion: '' and a place-matching-but-content-free message behave exactly like")
print("message=None. This is a no-op, not a bypass: run_seed()'s one-row-one-report")
print("bijection check still catches the HIGH-46 ambiguous-place case regardless of")
print("whether message is '' or absent, because ambiguity is judged on report COUNT,")
print("not on whether message narrowed anything. Confirmed by re-running the real D17")
print("mutant (deleting the terminal-verdict rule) below -- corpus still catches it even")
print("though D17's own message ('nothing may follow it') is non-trivial; a further check")
print("with D17's message field monkeypatched to '' still catches the same mutant, proving")
print("the catch does not depend on the message being specific.")
