"""The tally, computed from the records rather than read off them.

The first version of this write-up said 39 of 43. It was wrong, and the disqualifying
evidence was already in `results-by-hunk.jsonl`: two `schema.py` hunks are pure additions
whose names are only referenced inside function bodies, so reverting one alone leaves the
module importable — `run_one.sh`'s import control passes — and every call site then raises
`NameError`. A run that errors is not a run in which a regression detected the loss of its
own fix; it is a run in which nothing ran. Five regressions drew their only credit from
one such cascade, and every one of them holds a rule in `validate.py`, which does not
appear in this commit's diff at all.

So the second control: a hunk's credit is disqualified when its own summary reports
collection or call errors. The number this prints is the one the write-up carries.
"""

from __future__ import annotations

import collections
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def load(name):
    return [json.loads(line) for line in (HERE / name).read_text().splitlines()]


def main():
    manifest = {
        int(line.split("\t")[0]): line.split("\t")[1]
        for line in (HERE / "hunk-manifest.tsv").read_text().splitlines()
    }
    regressions = [line.strip() for line in (HERE / "regressions.txt").read_text().splitlines()]
    clean, disqualified = collections.defaultdict(set), collections.defaultdict(set)
    errored = []
    for row in load("results-by-hunk.jsonl") + load("results-by-file.jsonl"):
        if row["status"] != "ran":
            continue
        label = row["label"]
        bucket = disqualified if " errors" in row.get("summary", "") else clean
        if bucket is disqualified:
            errored.append(
                (
                    label,
                    manifest.get(int(label.split("-")[1]) if label.startswith("hunk-") else -1, ""),
                )
            )
        for name in (f for f in row["failed"].split(",") if f):
            bucket[name].add(label)
    print(f"regressions: {len(regressions)}")
    print(f"red under a revert whose run was clean: {len(clean)}")
    print("\nruns disqualified for collection or call errors:")
    for label, path in errored:
        print(f"   {label}  {path}")
    print("\ncredited only by a disqualified run:")
    for name in regressions:
        if name not in clean and name in disqualified:
            print(f"   {name}  ({', '.join(sorted(disqualified[name]))})")
    print("\nnever red under any revert:")
    for name in regressions:
        if name not in clean and name not in disqualified:
            print(f"   {name}")


if __name__ == "__main__":
    main()
