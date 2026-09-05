"""`python -m claims_ledger`.

The checkers use the standard library only, so they run from a plain `python3` on a
checkout with nothing installed — but only if there is something for `-m` to find. The
installed pre-commit hook invokes the package this way rather than by console-script
name, because git runs hooks with its own PATH.
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
