#!/usr/bin/env bash
# Part 3a: push past HIGH-45's two named cases at the floor of `claims-ledger corpus`.
# Run against a venv with claims-ledger installed (PATH must have it first).
set -u
say() { echo; echo "== $1 =="; }

say "seeds/ does not exist at all"
claims-ledger corpus --corpus /tmp/attack-noexist; echo "EXIT=$?"

say "seeds/ exists, empty"
rm -rf /tmp/attack-empty && mkdir -p /tmp/attack-empty/seeds
claims-ledger corpus --corpus /tmp/attack-empty; echo "EXIT=$?"

say "filter matches nothing"
claims-ledger corpus NOSUCHSEED; echo "EXIT=$?"

say "--corpus points at a plain file"
echo hi > /tmp/attack-file.txt
claims-ledger corpus --corpus /tmp/attack-file.txt; echo "EXIT=$?"

say "--corpus points at a FIFO"
rm -f /tmp/attack-fifo; mkfifo /tmp/attack-fifo
claims-ledger corpus --corpus /tmp/attack-fifo; echo "EXIT=$?"

say "seed dir with no expected.json (crashes, still non-zero)"
rm -rf /tmp/attack-noexp && mkdir -p /tmp/attack-noexp/seeds/D01-fake/entries
claims-ledger corpus --corpus /tmp/attack-noexp; echo "EXIT=$?"

say "expected.json is empty file (crashes, still non-zero)"
rm -rf /tmp/attack-emptyexp && mkdir -p /tmp/attack-emptyexp/seeds/D01-fake/entries
: > /tmp/attack-emptyexp/seeds/D01-fake/expected.json
claims-ledger corpus --corpus /tmp/attack-emptyexp; echo "EXIT=$?"

say "expected.json is [] (crashes, still non-zero)"
rm -rf /tmp/attack-list && mkdir -p /tmp/attack-list/seeds/D01-fake/entries
echo '[]' > /tmp/attack-list/seeds/D01-fake/expected.json
claims-ledger corpus --corpus /tmp/attack-list; echo "EXIT=$?"

say "expected.json is {} (crashes, still non-zero)"
rm -rf /tmp/attack-dict && mkdir -p /tmp/attack-dict/seeds/D01-fake/entries
echo '{}' > /tmp/attack-dict/seeds/D01-fake/expected.json
claims-ledger corpus --corpus /tmp/attack-dict; echo "EXIT=$?"

say "*** expected.json well-formed but expect: [] (empty entries too) -> THE HOLE ***"
rm -rf /tmp/attack-vacuous && mkdir -p /tmp/attack-vacuous/seeds/D01-fake/entries
echo '{"class":"x","known_good":true,"expect":[]}' > /tmp/attack-vacuous/seeds/D01-fake/expected.json
claims-ledger corpus --corpus /tmp/attack-vacuous; echo "EXIT=$? <-- 0, '1/1 seeds pass', over a seed that checked nothing"
