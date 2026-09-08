# Draft scratchpad

This file is excluded from citation scanning to demonstrate `document-excludes`.

The exclusion is load-bearing rather than decorative, and the line below is what makes
it so. This repository quarantines the `Z` series with `archived-prefixes = ["Z"]`, and
no document the checker scans may cite the archive — so `claims-ledger check` passes
here only for as long as this file is genuinely excluded. Take `docs/draft-*.md` out of
`document-excludes` and the next check fails, naming this file.

Superseded by the archive: Z0001, the legacy review window.
