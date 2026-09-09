---
id: L0176-a-citation-shaped-parenthetical-names-a-citation-act
kind: claim
stated: 2026-09-08T18:44:38-07:00
author: main
grade: measured
supersedes: L0159-a-citation-shaped-parenthetical-names-a-citation-act
verbatim_change: the condition named the word after the comma and nothing else; it now names the id before it too — minted by this ledger, in a series it does not quarantine — which is the population the rule actually reads and the predecessor left to a gloss in its Warrant
verbatim_sha: 74b32fb1006714766d96460c0d7a1d57835aaea98317227e1d2b8740d1d1e8a7
---

## Assertion

A parenthesis in a document holding an entry id, a comma and an act-shaped word is reported
when that word is not a citation act, rather than passing as prose.

## Scope

metric: whether a citation-shaped parenthesis with an illegal act is reported
cohort: every document the configuration reaches
condition: the word after the comma is lowercase letters and hyphens and is not a citation act, and the id before it is one this ledger minted in a series it does not quarantine

## Grounds

- code: src/claims_ledger/schema.py § "MISCITATION_RE" @6865d617f85111766795cb98b2075d5bde81822d
- code: src/claims_ledger/references.py § "run" @6865d617f85111766795cb98b2075d5bde81822d
- entry: L0175-an-unminted-id-is-not-a-citation-shape · distinguishes

## Warrant

CITATION_RE is built from the citation acts, so a mistyped act matches nothing and no other
rule reads documents: before this the sentence sat in a checked document as text nothing looked
at, which is the one report this package must never withhold. MISCITATION_RE matches the same
shape with any act-shaped word, and run reports the matches it can tell from prose. Which those
are is the correction this entry carries and the reason it supersedes L0159, whose Warrant said
run reports every match the citation acts do not cover: it does not, and by the time L0159 was
written it already did not, because an id in a quarantined series was the archive rule's finding
even then. The population is now stated rather than glossed — the word is not a citation act,
the series is not quarantined, and the id is one the ledger minted, which is what keeps a lint
code in a source comment from failing a commit. The rule stays narrow for the reason it always
was: an id in a parenthesis of its own, or in running prose, is a document naming an entry
rather than citing it, and is left alone.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- src/claims_ledger/schema.py · standing · cites-as-live
- src/claims_ledger/references.py · standing · cites-as-live
