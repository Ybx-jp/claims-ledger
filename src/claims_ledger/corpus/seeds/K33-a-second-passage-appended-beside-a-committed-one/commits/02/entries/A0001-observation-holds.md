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

- lab: docs/note-300.md § "Observation" =sha256:4486bb1016f57db4d7511fe49238b85f9b9a38d8da870211fc3022c38d2aa492
- lab: docs/note-300.md § "Method" =sha256:f936594fba0a648edc3afef0bbe3c0a0ecb754adc7c0b667e53d8a3da84fbc2e

## Warrant

The Observation section carries the measurement and the Method section says what it was measured over; this entry states no more than the two together.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-09T10:00:00-07:00 · corroborated · grade: measured · author: main
  evidence: lab: docs/note-300.md § "Observation" =sha256:274d45734e28877a5672e0e4cfc1e2348ac45e82b53d75a691645f14f30c10cd
  note: re-read after the narrative under the measurement was lifted onto this entry; the measurement itself is untouched and the claim is unchanged.

## References

- docs/digest-300.md · standing · cites-as-live

## Passages

- 2026-09-09T10:00:00-07:00 · author: main
  lifted: lab: docs/note-300.md § "Observation" =sha256:4486bb1016f57db4d7511fe49238b85f9b9a38d8da870211fc3022c38d2aa492
  passage:
      The sweep ran over star graphs of degree ten, twenty and fifty, and the error at the
      centre node tracked the fraction rather than the count at every degree.
