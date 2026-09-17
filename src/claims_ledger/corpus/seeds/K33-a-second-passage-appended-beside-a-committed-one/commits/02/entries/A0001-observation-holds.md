---
id: A0001-observation-holds
kind: claim
stated: 2026-09-08T15:00:00-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: ee4e31a4e98fb33148155e47268635357b533786f473365dd2e87a2cfab5767a
---

## Assertion

The measured error at a stale fraction of one tenth is four hundredths.

## Scope

metric: measured error at the centre node
cohort: the sweep note 300 reports
condition: one layer, mean aggregation, untrained weights, eval mode

## Grounds

- lab: docs/note-300.md § "Observation" =sha256:bd418dc218ba9557bdc3ceec47e11119cefd9ef6d6772336c66d7cb105ffb34d
- lab: docs/note-300.md § "Method" =sha256:de921148875341f9649d9616139952d8156f48051c7f29b5d3ab9f229a94423e

## Warrant

The Observation section carries the measurement and the Method section says what it was measured over; this entry states no more than the two together.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-09T10:00:00-07:00 · corroborated · grade: measured · author: main
  evidence: lab: docs/note-300.md § "Observation" =sha256:f491b27cbc5e698f9d51e23ad7b6bf91b4ad7b3af9c06c92239240ca17893c79
  note: re-read after the narrative under the measurement was lifted onto this entry; the measurement itself is untouched and the claim is unchanged.

## References

- docs/note-300.md · standing · cites-as-live

## Passages

- 2026-09-09T10:00:00-07:00 · author: main
  lifted: lab: docs/note-300.md § "Observation" =sha256:bd418dc218ba9557bdc3ceec47e11119cefd9ef6d6772336c66d7cb105ffb34d
  passage:
      The sweep ran over star graphs of degree ten, twenty and fifty, and the error at the
      centre node tracked the fraction rather than the count at every degree.
