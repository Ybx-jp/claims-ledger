"""Enumerate every report-emitting statement in the five checkers, at this tip.

Two shapes:
  - `fail(...)` / `flag(...)` as a bare expression statement (validate.py, resolve.py):
    these are lambdas closing over a local `out`/`reports` list. Neuter by replacing the
    whole statement with `pass` at the same indentation.
  - `reports.append(Report(...))` / `out.append(Report(...))` as a bare expression
    statement (references.py, propagate.py, freshness.py): same neutering.
  - `return [Report(...), ...]` (freshness.py's two git-problem early returns): neuter by
    replacing the whole return statement with `return []`.

Writes a JSON list of sites to stdout: module, lineno, end_lineno, col_offset, kind, text.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
MODULES = ["validate.py", "resolve.py", "references.py", "propagate.py", "freshness.py"]


def is_report_call(node):
    """Call to fail(...), flag(...), or Report(...)."""
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in (
        "fail",
        "flag",
        "Report",
    )


def find_sites(tree, module):
    sites = []
    for node in ast.walk(tree):
        # Bare expression statement: fail(...) / flag(...) / x.append(Report(...))
        if isinstance(node, ast.Expr):
            v = node.value
            if is_report_call(v):
                sites.append((node, "bare-call"))
            elif (
                isinstance(v, ast.Call)
                and isinstance(v.func, ast.Attribute)
                and v.func.attr == "append"
                and v.args
                and is_report_call(v.args[0])
            ):
                sites.append((node, "append-call"))
        # return [Report(...), ...] or return [Report(...)]
        elif isinstance(node, ast.Return) and isinstance(node.value, ast.List):
            if any(is_report_call(elt) for elt in node.value.elts):
                sites.append((node, "return-list"))
    return sites


out = []
for mod in MODULES:
    path = SRC / "claims_ledger" / mod
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    for node, kind in find_sites(tree, mod):
        seg = ast.get_source_segment(text, node)
        out.append(
            {
                "module": mod,
                "lineno": node.lineno,
                "end_lineno": node.end_lineno,
                "col_offset": node.col_offset,
                "kind": kind,
                "text": seg,
            }
        )

print(json.dumps(out, indent=2))
