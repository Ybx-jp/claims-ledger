---
id: L0220-an-object-id-is-as-wide-as-the-repository-makes-it
kind: claim
stated: 2026-09-11T19:30:15-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 546b0e949f053a84b1f3998db52f89e6524ca7607614aeb9a5fafb50c158fd68
---

## Assertion

An object id is recognised at either of the two widths git prints one in, so a repository created with the wider hash format is read the same as any other.

## Scope

metric: which object-id widths this package recognises when it reads what git printed
cohort: every repository a ledger may be held in, at either object format
condition: what a caller then does with the ids it recognised is that caller's own claim

## Grounds

- code: src/claims_ledger/schema.py § "OBJECT_ID_RE" =sha256:839f612a1927030849314c6a1fc1edeac16800b4e55ae033fb73889b32521948
- code: src/claims_ledger/resolve.py § "digest_in_history" =sha256:75047ccad1a470ef72c17a05d8453b51ab1364e869757765003a8204c2ec4efa
- entry: L0151-the-artifact-shape-is-defined-where-it-is-checked · distinguishes
- entry: L0093-a-propagated-verdicts-artifact-is-checked-in-every-state · distinguishes
- entry: L0206-the-search-for-an-anchors-text-reads-every-version-git-holds · distinguishes

## Warrant

A hash width is the repository's business and not the ledger's: git creates a repository with forty-hex object names by default and sixty-four when it is asked for the wider format, and prints whichever it holds. The pattern here admitted only the narrow one. The tell that this was an oversight rather than a decision is that the commit pattern in the history walk has admitted both since it was written. Measured, the narrow pattern bit one caller and not the one it was predicted to. The search for an anchor's text collects blob ids out of a raw log and filters them through this pattern, so in a wide repository every id was discarded, the set came back empty, no version was read, and a ground whose text had left the tree was reported as held by no version the repository has, blaming a rewritten history that had not happened. Three surfaces predicted to fail there were each measured to work before the widening: the immutable-region check caught a rewritten frozen region and named the creating commit, the fingerprint command refused a committed entry, and a clean ledger checked clean. So what this repairs is one false report and not a package that does not run in such a repository. The three entries named above hold other claims over the same two sections: where the artifact shape is defined, when it is checked, and what the search reads. This is a fourth, about what counts as an id at all.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/resolve.py · standing · cites-as-live
