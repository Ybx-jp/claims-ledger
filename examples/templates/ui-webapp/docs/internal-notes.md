# Internal notes

This excluded file shows how generated or private prose can be kept out of document
citation scanning.

As in `documentation-repo`, the exclusion is checked by what it holds back: the
citation below names an entry this ledger does not have, so a check that scanned this
file would fail on it. `document-excludes = ["docs/internal-*.md"]` is the only reason
it does not.

Superseded internally by (U0009-banner-copy-rewritten, cites-as-live).
