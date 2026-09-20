---
id: L0279-a-citation-is-read-wherever-the-text-holds-it
kind: claim
stated: 2026-09-20T10:44:22-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: 7bb08a40d0fc9e229a904f382456c5be2691e892c6ddac747d39456cc06e8cf2
---

## Assertion

A citation is read wherever a document's text holds one, with the comment syntax, markup or
quoting around it treated as text like any other.

## Scope

metric: whether a citation-shaped parenthesis is read and held to its entry's status when comment syntax, markup or a string literal surrounds it
cohort: every document the configuration reaches, in any file format
condition: the parenthesis stands complete in the document's text, with only whitespace between its comma and the act

## Grounds

- code: src/claims_ledger/schema.py § "CITATION_RE" =sha256:2b42a3fc5cbf3e14892515516ce6eea36249e1425001c84cd77928d08e8b13d9
- code: src/claims_ledger/references.py § "run" =sha256:166a79c96b6b68db961e4aeb6e8a271e668650a3181d75583405ee4478808d6f
- entry: L0157-distinguishes-is-an-act-between-entries · distinguishes
- entry: L0176-a-citation-shaped-parenthetical-names-a-citation-act · distinguishes

## Warrant

CITATION_RE constrains what stands inside the parenthesis and says nothing about what
precedes or follows it, and run matches it over the text read_document returned, with no
lexer between the two. A comment leader, a quotation mark and a markup tag are therefore
text like any other, and the rules that read a document — the act against the status, the
References row, the quarantined prefix, the placement — reach a marker in a YAML comment or
a JSON string exactly as they reach one in running prose.

What this buys is a placement a rendered document needs. A Markdown README that carries
twenty markers interrupts a reader who cannot act on any of them; inside an HTML comment
the same marker leaves the rendered page and stays where it was, in the span its entry
pins, in front of the person editing the source, who is the reader who can break the claim.
That is what separates it from a citation parked where the checker will not object.

The condition is the one shape it costs. Whitespace after the comma includes a newline, so
a comment that runs on with spaces alone is still read; a wrap that puts a `#`, a `//` or a
`*` there is not matched, and what reports it is the reverse rule, naming the entry whose
References row lists a document that does not cite it. tests/test_citation_formats.py holds
both halves against fifteen formats.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

- 2026-09-20T15:36:57-07:00 · contested · grade: measured · author: propagation
  evidence: code: src/claims_ledger/references.py § "run" =sha256:166a79c96b6b68db961e4aeb6e8a271e668650a3181d75583405ee4478808d6f
  artifact: sha256:51cf8c55f336e8fd07780a8e4509a9f7645490b4096cd3531b71f499615e89d7
  note: propagated from a moved ground

- 2026-09-20T15:36:58-07:00 · corroborated · grade: measured · author: main
  evidence: code: src/claims_ledger/references.py § "run" =sha256:51cf8c55f336e8fd07780a8e4509a9f7645490b4096cd3531b71f499615e89d7
  note: re-read after merging main into the branch that lets a marker name its entry by the number alone. Both sides edited this section: main wrote the claim this entry states, and the branch changed how each marker is resolved and collected. Neither touches what this one asserts — the pattern still runs over the document's text as it was read, with nothing parsing it, so a marker inside a comment of whatever kind the format hides text in is read exactly as one in running prose is. The document loop it sits in now resolves the id before using it, which is a question about which entry a marker names and not about where a marker may be written.


## References

- src/claims_ledger/schema.py · standing · cites-as-live
