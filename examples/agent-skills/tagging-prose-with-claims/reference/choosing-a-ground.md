# Choosing a ground

A ground is evidence, and it should name what makes the claim true and nothing else. Two
failures are common, and both are cheap to avoid while the entry is being written — which
is the only cheap moment there is, because a ground cannot be edited once the entry is in
history.

## Name what carries the rule

A claim about what something does is grounded in the thing that does it, not in everything
that relies on it. A ground on a consumer goes stale for every edit to that consumer, none
of which the claim cares about.

If the claim's cohort really is "everywhere this happens", say so in the Scope and let the
Warrant name the pattern. Scope is prose a reader checks, and it does not go stale.

## Name no more than the claim needs

A section is the unit, and by default a section is a whole top-level thing — a definition,
a table, a heading and what follows it. A claim about one setting, resting on the table
that holds it, is flagged when an unrelated key beside it changes.

Section patterns are how a project makes a type narrower. Print what this one uses:

    python -c "from claims_ledger import open_ledger; print(open_ledger().config.section_patterns)"

## Check what a narrow pattern actually spans

One pattern usually decides both ends of a section — the same pattern, widened, is what
finds the end — so a section runs to the next line the pattern matches, whatever that line
is. Two consequences, and the first is the dangerous one:

- **Over a value written across several lines, a key-shaped pattern can span the key's own
  first line and nothing else.** The result is a ground that can never go stale, which is
  worse than one that goes stale too often, because nothing will ever tell you.
- **A name is matched wherever it first appears.** A pattern that cannot say *which* table
  or *which* file a name lives in will take the first match. If the claim depends on
  which, say so in the Warrant.

`claims-ledger references` prints what it read. Comparing a ground's span against the
claim before the entry is committed is the whole of the check, and it takes a minute.

## Grade honestly

    claims-ledger new --help          the grades and what each requires

`measured` and above are for a claim that something *does* what is said, and take a pin
that `freshness` watches. `asserted` is for a choice the project *made*; it forbids an
evidence ground and never goes stale.

A preference recorded as `measured` is flagged every time the file around it is
reformatted, in exchange for nothing.

## What the width costs, plainly

Every meaningful edit to a pinned span flags every entry pinned there. Narrow sections
make that rare — a ground on one definition is flagged only when that definition changes,
where a ground on a whole file is flagged by every commit that touches it — but the cost
does not reach zero, and it scales with how many entries are pinned rather than with how
many real changes of meaning occur.

That is the trade the ledger makes. `repair-a-drifted-pin` covers what to do when a flag
appears, including the case where the flag is real and the claim is untouched.
