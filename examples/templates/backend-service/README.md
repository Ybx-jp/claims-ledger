# Nimbus Claims API

This synthetic Python service classifies claim-risk scores. Its threshold is pinned to
the implementation and checked against the UI contract
(B0001-service-and-ui-share-threshold, cites-as-live).

The contract snapshots under `evidence/` are copied from the UI and research
repositories during materialization and registered as immutable source bytes.
