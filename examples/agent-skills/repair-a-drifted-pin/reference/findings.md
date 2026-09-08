# The findings, and what each one means

    claims-ledger freshness              compare every pinned ground against its revision
    claims-ledger freshness --cached     compare the index rather than the working tree
    claims-ledger freshness --write      append the verdict a drift is owed

## fresh

The span the ground names reads the same now as at the revision it pins. Silent.

## moved — a flag

The span exists and differs. This is the ordinary case, and most instances are immaterial:
a reformat, a comment added, a neighbouring change that shifted the lines a pattern spans.

It is a flag rather than a failure on purpose. In a project whose grounded artifacts are
edited daily, a checker that refused every commit touching a grounded file until someone
wrote a verdict is a checker that gets switched off.

Discharged by any of the four outcomes in the skill.

## withdrawn — a failure

The path the ground names is not in the working tree at all.

**A rename lands here, not in `moved`.** The comparison stats the literal path the ground
carries; once the file is at a different path, that path is gone, and no rename detection
is consulted. Moving a section to a different file produces the same finding.

It is a failure rather than a flag because there is no noise floor: a reformat happens
constantly and a path disappearing does not. The artifact is recorded as `absent` in the
verdict `--write` appends.

Discharged the same four ways. Where the move was a rename and the claim is untouched,
the corroborating verdict naming the new path is the record of where it went.

## unstable pin — a flag, and no verdict discharges it

The ground names no revision, so the comparison has nothing to compare against. There is
no drift to record and no judgement to write; a verdict here would discharge a finding
that was never made.

The repair is to pin the ground at a revision. Since a ground cannot be edited once the
entry is in history, that is a supersession if the entry is already committed, and a
correction to the draft if it is not.

## unknown — a failure, and no verdict discharges it

Version control declined to answer — a missing object, a shallow or partial clone, a
timeout, a repository the run could not reach. The finding names the reason.

Nothing about the claim is in question. The repair is to the repository, not to the ledger.
A verdict written over an `unknown` records a comparison that never happened, and
`claims-ledger validate` treats a discharge that no run caused as an orphan.

## What a discharge is held to

The verdict `--write` appends carries what the artifact read as when the drift was seen.
That value is what separates a discharge this checker caused from one written ahead of
time, and it is checked: a verdict claiming a state the artifact has never been in does not
silence the finding.

This is why the contested verdict is written with `claims-ledger freshness --write` rather
than by hand. A verdict under the propagation author asserts that a check ran.

## Once a drift is recorded

A discharge is against the drift in front of it. Once the verdict recording it is in
history, that ground reports no further drift — the name is the reading: `freshness` is
about what has changed *since the pin*, and a change already recorded is not new.

The consequence worth knowing when choosing an outcome: an entry returned to a live status
carries a ground that will not report again. Superseding or letting the claim fall retires
the entry instead, and a retired entry is not walked.
