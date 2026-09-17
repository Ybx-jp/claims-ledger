# Concurrent authoring

This template is not a fifth member of the portfolio. It carries the note two independent
lines of work both write claims about, so `materialize.py` can build the one situation the
other four repositories cannot show: two sessions that each minted the same number, and
the rewrite that repairs it before the merge.

There is no configuration file here on purpose. `claims-ledger init` writes it, which is
how a project that has never seen this repository starts, and the materializer then appends
the one key this demonstration is about — `merge-renumber` — before either branch is cut. A
configuration that changes *on* the branch is one of the things a rewrite refuses, because
the rewrite reads one configuration for every commit it replaces.
