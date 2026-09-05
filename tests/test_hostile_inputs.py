"""Hostile and malformed input, thrown at the package before strangers throw it first.

The oracle is narrow and it is the whole point: every input below may end only one of
two ways —

  1. a clean non-zero exit with a human-readable message on stderr, or
  2. a correct successful run.

Never acceptable: an unhandled traceback reaching a stranger, a hang, a wrong exit code,
a message that is a raw Python exception repr with no explanation, a false "0 failures"
over content that was never actually checked, or a write outside the project root.

`cli.main()` catches a broad `Exception` and prints `claims-ledger: unexpected <Type>:
...`. That string is the fingerprint of a case that fell through every specific handler,
so every test below that produces it fails the assertion on purpose — it is a bug
signal, not a pass, and was never weakened to match the behaviour it found.

The eighteen defects this file was written to record are fixed — the nine of the
2026-09-05 pre-publication audit and the nine of the second pass against those fixes
(QE-AUDIT.md, both sections) — and each is kept below as the regression test for its fix.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata

import pytest

from claims_ledger import cli, schema
from claims_ledger.config import ConfigError, load_config
from claims_ledger.corpus import run as corpus_run


def run_cli(root, *args, timeout=10, env=None):
    """The installed CLI as a real subprocess, for cases that must be watched for a hang
    rather than trusted to return at all, and for the ones whose subject is the
    environment the process starts in."""
    return subprocess.run(
        [sys.executable, "-m", "claims_ledger", "--root", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=None if env is None else {**os.environ, **env},
    )


# The C locale with every coercion turned off: stdin/stdout encode as ASCII and so does
# the codec `subprocess` decodes git's output with.
ASCII_LOCALE = {
    "LC_ALL": "C",
    "LANG": "C",
    "PYTHONUTF8": "0",
    "PYTHONCOERCECLOCALE": "0",
    "PYTHONIOENCODING": "ascii",
}


# === A. the entry parser fed hostile Markdown ========================================


def _write_entry(project, name, content_bytes):
    path = project.entries / name
    path.write_bytes(content_bytes)
    return path


@pytest.mark.parametrize(
    "name,content",
    [
        ("A0001-empty.md", b""),
        ("A0001-only-frontmatter.md", b"---\nid: A0001-only-frontmatter\n---\n"),
        ("A0001-unclosed.md", b"---\nid: A0001-unclosed\nkind: claim\nno closing fence at all\n"),
        (
            "A0001-two-blocks.md",
            b"---\nid: A0001-two-blocks\n---\n---\nid: A0001-again\n---\n\n## Assertion\n\nx\n",
        ),
        ("A0001-not-a-mapping.md", b"---\n- a\n- b\n- c\n---\n\n## Assertion\n\nx\n"),
        (
            "A0001-dup-keys.md",
            b"---\nid: A0001-dup-keys\nid: A0001-other\nkind: claim\n---\n\n## Assertion\n\nx\n",
        ),
        (
            "A0001-no-trailing-newline.md",
            b"---\nid: A0001-no-trailing-newline\n---\n\n## Assertion\n\nx",
        ),
    ],
)
def test_structurally_broken_frontmatter_is_reported_not_raised(project, capsys, name, content):
    _write_entry(project, name, content)
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert rc in (0, 1, 2)
    assert "Traceback" not in err
    assert "unexpected" not in err


def test_crlf_line_endings_do_not_crash(project, capsys):
    text = (
        "---\r\nid: A0001-crlf\r\nkind: claim\r\nstated: 2026-09-05T12:00:00Z\r\n"
        "author: main\r\ngrade: asserted\r\nsupersedes: none\r\n"
        "verbatim_sha: " + "0" * 64 + "\r\n---\r\n\r\n"
        "## Assertion\r\n\r\nSomething, stated with carriage returns.\r\n\r\n"
        "## Scope\r\n\r\nmetric: x\r\ncohort: x\r\ncondition: x\r\n\r\n"
        "## Grounds\r\n\r\n- TODO\r\n\r\n## Warrant\r\n\r\nbecause.\r\n\r\n"
        "## Backing\r\n\r\nnone\r\n\r\n<!-- APPEND BELOW THIS LINE ONLY -->\r\n\r\n"
        "## Verdicts\r\n\r\n## References\r\n"
    )
    _write_entry(project, "A0001-crlf.md", text.encode("utf-8"))
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc in (0, 1, 2)


def test_a_utf8_bom_is_reported_cleanly(project, capsys):
    """A BOM prepended to an otherwise well-formed entry defeats the `---\\n` prefix
    check, since Path.read_text(encoding="utf-8") does not strip it. The parser must
    treat that as "no frontmatter", not choke on it."""
    content = "﻿---\nid: A0001-bom\nkind: claim\n---\n\n## Assertion\n\nx\n".encode()
    _write_entry(project, "A0001-bom.md", content)
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc == 1  # a real, reported failure — not a silent pass


def test_mixed_line_endings_do_not_crash(project, capsys):
    content = b"---\r\nid: A0001-mixed\nkind: claim\r\n---\n\n## Assertion\r\n\nmixed.\n"
    _write_entry(project, "A0001-mixed.md", content)
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc in (0, 1, 2)


@pytest.mark.parametrize(
    "label,raw",
    [
        (
            "nul_byte",
            b"---\nid: A0001-nul\nkind: claim\n---\n\n## Assertion\n\nsomething\x00weird\n",
        ),
        (
            "c0_controls",
            b"---\nid: A0001-ctrl\nkind: claim\n---\n\n## Assertion\n\na\x01\x02\x03b\n",
        ),
        ("lone_continuation_byte", b"---\nid: A0001-x\n---\n\n## Assertion\n\n\x80bad\n"),
        (
            "truncated_multibyte",
            b"---\nid: A0001-x\n---\n\n## Assertion\n\n\xe2\x82\n",
        ),  # truncated €
        ("overlong_encoding", b"---\nid: A0001-x\n---\n\n## Assertion\n\n\xc0\xaf\n"),
        ("lone_surrogate_bytes", b"---\nid: A0001-x\n---\n\n## Assertion\n\n\xed\xa0\x80\n"),
    ],
)
def test_control_characters_and_invalid_utf8_are_reported_not_raised(project, capsys, label, raw):
    _write_entry(project, "A0001-bytes.md", raw)
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err
    assert "unexpected" not in err
    # Either a clean parse-and-report (1) or a LedgerError about bad bytes (2).
    assert rc in (1, 2)


UNICODE_ASSERTIONS = {
    "rtl_override": "The result holds ‮esrever ni si siht‬ and nowhere else.",
    "zero_width_joiner": "A claim about na‍ive aggregation and its error.",
    "combining_marks": "The error decréases as the stale fraction falls.",
    "homoglyph_cyrillic_a": "The errар (Cyrillic a) is bounded by the stale fraction.",  # noqa: RUF001
    "astral_emoji": "The stale fraction \U0001f4c9 drives the aggregation error.",
}


@pytest.mark.parametrize(
    "label,assertion", UNICODE_ASSERTIONS.items(), ids=list(UNICODE_ASSERTIONS)
)
def test_unicode_assertion_text_does_not_crash_the_checkers(project, capsys, label, assertion):
    project.cl("new", f"unicode-{label}".replace("_", "-"))
    path = project.entry(f"A0001-unicode-{label.replace('_', '-')}.md")
    project.write_full_entry(path)
    text = path.read_text(encoding="utf-8")
    from conftest import ASSERTION

    text = text.replace(ASSERTION, assertion)
    path.write_text(text, encoding="utf-8")
    capsys.readouterr()
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc == 0, capsys.readouterr()


def test_nfc_and_nfd_forms_of_the_same_text_fingerprint_identically(project):
    """é as one codepoint (NFC) and as e + combining acute (NFD) are the same text to a
    human. normalize() runs NFC first, so both forms of the same Scope must fingerprint
    the same way."""
    from claims_ledger.schema import fingerprint

    nfc = unicodedata.normalize("NFC", "cohort: café users")
    nfd = unicodedata.normalize("NFD", "cohort: café users")
    assert nfc != nfd  # the two byte-forms really do differ
    assert fingerprint(nfc, []) == fingerprint(nfd, [])


@pytest.mark.parametrize(
    "sections_text",
    [
        # Grounds missing entirely.
        (
            "## Assertion\n\nx\n\n## Scope\n\nmetric: x\ncohort: x\ncondition: x\n\n"
            "## Warrant\n\nbecause.\n\n## Backing\n\nnone\n\n"
            "<!-- APPEND BELOW THIS LINE ONLY -->\n\n## Verdicts\n\n## References\n"
        ),
        # Sections reordered: Warrant before Scope.
        (
            "## Assertion\n\nx\n\n## Warrant\n\nbecause.\n\n## Scope\n\nmetric: x\ncohort: x\n"
            "condition: x\n\n## Grounds\n\n- TODO\n\n## Backing\n\nnone\n\n"
            "<!-- APPEND BELOW THIS LINE ONLY -->\n\n## Verdicts\n\n## References\n"
        ),
        # Assertion duplicated.
        (
            "## Assertion\n\nx\n\n## Assertion\n\ny\n\n## Scope\n\nmetric: x\ncohort: x\n"
            "condition: x\n\n## Grounds\n\n- TODO\n\n## Warrant\n\nbecause.\n\n"
            "## Backing\n\nnone\n\n"
            "<!-- APPEND BELOW THIS LINE ONLY -->\n\n## Verdicts\n\n## References\n"
        ),
    ],
    ids=["missing-grounds", "reordered", "duplicated-assertion"],
)
def test_missing_duplicated_or_reordered_sections_are_reported(project, capsys, sections_text):
    header = (
        "---\nid: A0001-sections\nkind: claim\nstated: 2026-09-05T12:00:00Z\n"
        "author: main\ngrade: asserted\nsupersedes: none\nverbatim_sha: " + "0" * 64 + "\n---\n\n"
    )
    _write_entry(project, "A0001-sections.md", (header + sections_text).encode("utf-8"))
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc == 1


@pytest.mark.parametrize(
    "mutate",
    [
        lambda t: t.replace("<!-- APPEND BELOW THIS LINE ONLY -->\n", ""),  # absent
        lambda t: t.replace(
            "<!-- APPEND BELOW THIS LINE ONLY -->\n",
            "<!-- APPEND BELOW THIS LINE ONLY -->\n<!-- APPEND BELOW THIS LINE ONLY -->\n",
        ),  # duplicated
        lambda t: (
            t.replace("<!-- APPEND BELOW THIS LINE ONLY -->\n\n", "", 1)
            + "\n<!-- APPEND BELOW THIS LINE ONLY -->\n"
        ),  # moved to the very end
    ],
    ids=["absent", "duplicated", "moved-to-end"],
)
def test_the_append_sentinel_being_absent_duplicated_or_moved_is_reported(project, capsys, mutate):
    project.cl("new", "sentinel-games")
    path = project.write_full_entry(project.entry("A0001-sentinel-games.md"))
    text = path.read_text(encoding="utf-8")
    path.write_text(mutate(text), encoding="utf-8")
    capsys.readouterr()
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc in (0, 1)


@pytest.mark.parametrize(
    "credence,should_fail",
    [
        ("banana", True),
        ("nan", True),
        ("inf", True),
        ("-inf", True),
        ("-0.5", True),
        ("1.5", True),
        ("1e309", True),  # overflows to +inf in Python's float()
        ("0.5", False),
    ],
)
def test_hostile_credence_values_are_reported_not_raised(project, capsys, credence, should_fail):
    project.cl("new", "credence-games", "--kind", "prediction", "--resolves-when", "x")
    path = project.entry("A0001-credence-games.md")
    text = path.read_text(encoding="utf-8")
    text = text.replace("credence: 0.5", f"credence: {credence}")
    path.write_text(text, encoding="utf-8")
    capsys.readouterr()
    rc = project.cl("validate")
    out, err = capsys.readouterr()
    assert "Traceback" not in err and "unexpected" not in err
    assert rc == 1  # this entry is still a placeholder scaffold regardless of credence
    if should_fail:
        assert "credence" in out


def test_a_credence_written_in_non_ascii_digits_is_rejected(project, capsys):
    """`float()` is wider than the schema: it reads any Unicode decimal digit. A credence
    is held to ASCII digits so that what a reader sees is what the checker read."""
    project.cl("new", "unicode-credence", "--kind", "prediction", "--resolves-when", "x")
    path = project.entry("A0001-unicode-credence.md")
    text = path.read_text(encoding="utf-8")
    # Arabic-Indic zero and five read as 0.5 to a human, but they are not
    # the ASCII numerals the schema documents.
    text = text.replace("credence: 0.5", "credence: ٠.٥")  # noqa: RUF001
    path.write_text(text, encoding="utf-8")
    capsys.readouterr()
    project.cl("validate")
    out = capsys.readouterr().out
    assert "credence" in out  # flagged as not a plain decimal number


@pytest.mark.parametrize(
    "timestamp",
    [
        "not-a-timestamp",
        "0000-01-01T00:00:00Z",  # year zero
        "2026-13-45T99:99:99Z",  # nonsense calendar fields
        "2026-09-05T12:00:00+99:99",  # absurd offset
        "2026-09-05T12:00:00",  # no offset at all
    ],
)
def test_garbage_timestamps_are_reported_not_raised(project, capsys, timestamp):
    project.cl("new", "timestamp-games")
    path = project.write_full_entry(project.entry("A0001-timestamp-games.md"))
    text = path.read_text(encoding="utf-8")
    import re as _re

    text = _re.sub(r"^stated: .*$", f"stated: {timestamp}", text, count=1, flags=_re.MULTILINE)
    path.write_text(text, encoding="utf-8")
    capsys.readouterr()
    rc = project.cl("validate")
    out, err = capsys.readouterr()
    assert "Traceback" not in err and "unexpected" not in err
    assert rc == 1
    assert "stated" in out


def test_far_future_timestamp_is_accepted_as_a_valid_iso_timestamp(project, capsys):
    """9999-12-31 is within Python's datetime range and is not, on its own, malformed."""
    project.cl("new", "far-future")
    path = project.write_full_entry(project.entry("A0001-far-future.md"))
    text = path.read_text(encoding="utf-8")
    import re as _re

    text = _re.sub(
        r"^stated: .*$", "stated: 9999-12-31T23:59:59Z", text, count=1, flags=_re.MULTILINE
    )
    path.write_text(text, encoding="utf-8")
    capsys.readouterr()
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc == 0


def test_a_very_long_assertion_line_does_not_crash(project, capsys):
    project.cl("new", "long-line")
    path = project.write_full_entry(project.entry("A0001-long-line.md"))
    text = path.read_text(encoding="utf-8")
    from conftest import ASSERTION

    huge = ("word " * 700_000).strip()  # ~3.5MB, one line, no quote marks
    text = text.replace(ASSERTION, huge)
    path.write_text(text, encoding="utf-8")
    capsys.readouterr()
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc == 0


def test_thousands_of_verdict_lines_do_not_crash_or_hang(project, capsys):
    project.cl("new", "many-verdicts")
    path = project.write_full_entry(project.entry("A0001-many-verdicts.md"))
    text = path.read_text(encoding="utf-8")
    blocks = []
    for i in range(3000):
        blocks.append(
            f"- 2026-09-05T12:00:{i % 60:02d}Z · contested · grade: measured · author: main\n"
            f"  evidence: entry: A0001-many-verdicts · challenges\n"
        )
    text = text.replace("## Verdicts\n", "## Verdicts\n\n" + "\n".join(blocks) + "\n")
    path.write_text(text, encoding="utf-8")
    capsys.readouterr()
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc in (0, 1)


def test_filename_id_disagreement_is_reported(project, capsys):
    project.cl("new", "filename-mismatch")
    path = project.entry("A0001-filename-mismatch.md")
    text = path.read_text(encoding="utf-8").replace(
        "id: A0001-filename-mismatch", "id: A0001-something-else"
    )
    path.write_text(text, encoding="utf-8")
    capsys.readouterr()
    rc = project.cl("validate")
    out = capsys.readouterr().out
    assert rc == 1
    assert "does not match filename" in out


def test_a_unicode_filename_is_reported_cleanly_when_its_id_does_not_match(project, capsys):
    src = project.entry("A0001-plain.md")
    project.cl("new", "plain")
    dest = project.entries / "A0001-ééé.md"  # "A0001-ééé.md"
    src.rename(dest)
    capsys.readouterr()
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc == 1


def _filesystem_allows_newlines_in_filenames() -> bool:
    """Probed once at import rather than skipped from inside the test.

    A runtime `pytest.skip` here needed a version-specific `ty: ignore`, since older
    and newer ty disagree about the signature of pytest's `@_with_exception`-wrapped
    helpers, and an ignore that one version needs the other reports as unused. A
    module-level probe behind `skipif` needs no ignore on either.
    """
    with tempfile.TemporaryDirectory() as tmp:
        try:
            (pathlib.Path(tmp) / "a\nb").touch()
        except OSError:
            return False
        return True


FILENAMES_MAY_CONTAIN_NEWLINES = _filesystem_allows_newlines_in_filenames()


@pytest.mark.skipif(
    not FILENAMES_MAY_CONTAIN_NEWLINES,
    reason="this filesystem does not allow newlines in filenames",
)
def test_a_filename_containing_a_newline_does_not_crash(project, capsys):
    """A newline is legal in a POSIX filename. It must not be legal in an id, but the
    tool has to say so instead of falling over on the byte."""
    project.cl("new", "newline-victim")
    src = project.entry("A0001-newline-victim.md")
    dest = project.entries / "A0001-new\nline.md"
    src.rename(dest)
    capsys.readouterr()
    rc = project.cl("check")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc in (0, 1, 2)


def test_an_id_written_in_non_ascii_digits_is_refused(project, capsys):
    """`\\d` matches any Unicode decimal digit, so a fullwidth id used to be accepted and
    to pass validate's id check while being a different string from the A0001 it looks
    like. The id patterns are ASCII-only."""
    fullwidth_id = "A０００１"  # looks like "A0001"  # noqa: RUF001
    rc = project.cl("new", "homoglyph-id", "--id", fullwidth_id)
    err = capsys.readouterr().err
    assert rc != 0, err  # refused as not <letter><four ascii digits>-<slug>
    assert not any(project.entries.glob("A*homoglyph-id.md"))


# === B. the config layer ==============================================================


def test_invalid_toml_syntax_is_a_clean_config_error(tmp_path, capsys):
    root = tmp_path / "proj"
    root.mkdir()
    (root / "claims-ledger.toml").write_text("this is not [ valid toml\n", encoding="utf-8")
    rc = cli.main(["--root", str(root), "status"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "Traceback" not in err
    assert "unexpected" not in err


@pytest.mark.parametrize(
    "key,bad_value",
    [
        ("ledger", 5),
        ("entries", ["a", "list"]),
        ("registry", 3.14),
        ("cache", 5),
        ("documents", "*.md"),
        ("document-excludes", "not-a-list"),
        ("roster", ["ROSTER.md"]),
        ("archived-prefixes", "A"),
        ("evidence-sectioned", "lab"),
        ("evidence-plain", "experiment"),
        ("verdict-authors", "main"),
        ("propagation-author", ["propagation"]),
    ],
)
def test_every_config_key_rejects_the_wrong_type(tmp_path, key, bad_value):
    root = tmp_path / "proj"
    root.mkdir()
    from claims_ledger.config import from_table

    with pytest.raises(ConfigError):
        from_table({key: bad_value}, root)


def test_an_empty_string_ledger_path_is_handled_one_way_or_the_other(tmp_path, capsys):
    root = tmp_path / "proj"
    root.mkdir()
    (root / "claims-ledger.toml").write_text(
        '[tool.claims-ledger]\nledger = ""\n', encoding="utf-8"
    )
    rc = cli.main(["--root", str(root), "status"])
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc in (0, 2)


def test_a_config_that_is_a_directory_is_refused(tmp_path, capsys):
    root = tmp_path / "proj"
    root.mkdir()
    cfg_dir = root / "claims-ledger.toml"
    cfg_dir.mkdir()
    rc = cli.main(["--root", str(root), "--config", str(cfg_dir), "status"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "Traceback" not in err and "unexpected" not in err


def test_a_symlinked_config_file_works_normally(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    real = tmp_path / "real-config.toml"
    real.write_text('[tool.claims-ledger]\nledger = "record"\n', encoding="utf-8")
    link = root / "claims-ledger.toml"
    os.symlink(real, link)
    config = load_config(root=root)
    assert config.ledger_dir == root / "record"


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores file permissions")
def test_an_unreadable_config_is_a_clean_error_not_a_crash(tmp_path, capsys):
    root = tmp_path / "proj"
    root.mkdir()
    cfg = root / "claims-ledger.toml"
    cfg.write_text('[tool.claims-ledger]\nledger = "ledger"\n', encoding="utf-8")
    cfg.chmod(0o000)
    try:
        rc = cli.main(["--root", str(root), "status"])
        err = capsys.readouterr().err
        assert rc == 2
        assert "Traceback" not in err and "unexpected" not in err
    finally:
        cfg.chmod(0o644)


def test_a_config_with_a_bom_is_a_clean_toml_error(tmp_path, capsys):
    root = tmp_path / "proj"
    root.mkdir()
    (root / "claims-ledger.toml").write_bytes(
        b'\xef\xbb\xbf[tool.claims-ledger]\nledger = "ledger"\n'
    )
    rc = cli.main(["--root", str(root), "status"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "Traceback" not in err and "unexpected" not in err


def test_an_absolute_ledger_path_cannot_escape_the_project_root(tmp_path, capsys):
    """A cloned repository carries its own claims-ledger.toml. It does not get to name
    where this tool writes."""
    root = tmp_path / "proj"
    root.mkdir()
    outside = tmp_path / "outside-root"
    cfg = root / "claims-ledger.toml"
    cfg.write_text(f'[tool.claims-ledger]\nledger = "{outside}"\n', encoding="utf-8")
    rc = cli.main(["--root", str(root), "--config", str(cfg), "new", "escape-attempt"])
    err = capsys.readouterr().err
    # `Path(root) / "/abs"` discards `root`, so this used to write real files outside the
    # project with no warning. Refused, per the audit's agreed fix.
    assert rc == 2
    assert "ledger" in err and "outside the project root" in err
    assert not outside.exists()


def test_a_traversal_ledger_path_cannot_escape_the_project_root(tmp_path, capsys):
    """`..` walks out of the root as surely as an absolute path does, and is refused the
    same way rather than silently normalized into something inside it."""
    root = tmp_path / "a" / "b" / "proj"
    root.mkdir(parents=True)
    outside = tmp_path / "outside-root"
    cfg = root / "claims-ledger.toml"
    cfg.write_text('[tool.claims-ledger]\nledger = "../../../outside-root"\n', encoding="utf-8")
    rc = cli.main(["--root", str(root), "--config", str(cfg), "new", "escape-attempt"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "ledger" in err and "outside the project root" in err
    assert not outside.exists()
    with pytest.raises(ConfigError):
        load_config(root=root, config_path=cfg)


def test_root_overrides_the_directory_the_config_file_lives_in(tmp_path):
    """--root and --config disagreeing: --root wins for path resolution, per
    load_config's documented contract."""
    config_home = tmp_path / "elsewhere"
    config_home.mkdir()
    cfg = config_home / "claims-ledger.toml"
    cfg.write_text('[tool.claims-ledger]\nledger = "ledger"\n', encoding="utf-8")
    project_root = tmp_path / "actual-project"
    project_root.mkdir()
    config = load_config(root=project_root, config_path=cfg)
    assert config.root == project_root.resolve()
    assert config.ledger_dir == project_root.resolve() / "ledger"


# === C. path and filesystem hostility =================================================


def test_entries_dir_being_a_symlink_to_a_real_directory_works(project, capsys):
    real = project.root / "real-entries"
    real.mkdir()
    import shutil

    shutil.rmtree(project.entries)
    os.symlink(real, project.entries)
    rc = project.cl("new", "via-symlinked-dir")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc == 0
    assert (real / "A0001-via-symlinked-dir.md").is_file()


def test_an_entry_file_symlinked_from_outside_the_root_is_read_normally(project, capsys):
    project.cl("new", "will-be-replaced")
    real_path = project.root.parent / "outside-entry.md"
    original = project.entry("A0001-will-be-replaced.md")
    real_path.write_text(original.read_text(encoding="utf-8"), encoding="utf-8")
    original.unlink()
    os.symlink(real_path, original)
    capsys.readouterr()
    rc = project.cl("status")
    err = capsys.readouterr().err
    assert "Traceback" not in err and "unexpected" not in err
    assert rc == 0


def test_a_dangling_symlink_entry_is_reported_cleanly(project, capsys):
    target = project.root.parent / "does-not-exist.md"
    os.symlink(target, project.entry("A0001-dangling.md"))
    rc = project.cl("status")
    err = capsys.readouterr().err
    assert rc == 2
    assert "Traceback" not in err and "unexpected" not in err
    assert "A0001-dangling.md" in err


def test_a_directory_named_dot_md_is_reported_cleanly(project, capsys):
    (project.entries / "A0001-a-directory.md").mkdir()
    rc = project.cl("status")
    err = capsys.readouterr().err
    assert rc == 2
    assert "Traceback" not in err and "unexpected" not in err
    assert "A0001-a-directory.md" in err


def test_a_looping_symlink_entry_is_reported_cleanly(project, capsys):
    """A single entry file that is a symlink loop (not the whole entries directory)."""
    loop = project.entry("A0001-loop.md")
    os.symlink(loop, loop)
    rc = project.cl("status")
    err = capsys.readouterr().err
    assert rc == 2
    assert "Traceback" not in err
    assert "unexpected" not in err  # expected: a clean "cannot read entry"; see below


def test_entries_dir_itself_being_a_symlink_loop_is_reported_cleanly(project, capsys):
    """is_dir() on a loop raises rather than answering; there is still no directory to
    read, and that is a misconfigured root, not an internal error."""
    import shutil

    shutil.rmtree(project.entries)
    os.symlink("entries", project.entries)
    rc = project.cl("status")
    err = capsys.readouterr().err
    assert "unexpected" not in err, err
    assert rc == 2


def test_a_fifo_named_dot_md_does_not_hang_the_tool(project):
    """read_text() on a FIFO with no writer blocks forever, which in a pre-commit hook
    wedges the commit with no output at all. Nothing but a regular file is opened."""
    fifo_path = project.entries / "A0001-fifo.md"
    os.mkfifo(fifo_path)
    try:
        proc = run_cli(project.root, "status", timeout=5)
        assert proc.returncode != 0
        assert "Traceback" not in proc.stderr
    except subprocess.TimeoutExpired as exc:
        # The point being demonstrated: it never returns. Fail explicitly rather than
        # letting the suite hang.
        raise AssertionError(f"claims-ledger status hung reading a FIFO entry: {exc}") from exc


# === D. CLI argument hostility =========================================================


def test_an_unknown_subcommand_is_a_clean_argparse_error(project, capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--root", str(project.root), "not-a-real-command"])
    assert exc.value.code == 2
    assert "Traceback" not in capsys.readouterr().err


def test_root_pointing_at_a_nonexistent_directory_is_a_clean_error(tmp_path, capsys):
    rc = cli.main(["--root", str(tmp_path / "does" / "not" / "exist"), "validate"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "Traceback" not in err and "unexpected" not in err


def test_root_pointing_at_a_plain_file_is_a_clean_error(tmp_path, capsys):
    a_file = tmp_path / "im-a-file"
    a_file.write_text("hi", encoding="utf-8")
    rc = cli.main(["--root", str(a_file), "validate"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "Traceback" not in err and "unexpected" not in err


def test_an_empty_root_is_refused_rather_than_silently_using_cwd(tmp_path, monkeypatch, capsys):
    unrelated_cwd = tmp_path / "unrelated-cwd"
    unrelated_cwd.mkdir()
    monkeypatch.chdir(unrelated_cwd)
    rc = cli.main(["--root", "", "status"])
    err = capsys.readouterr().err
    # `root or Path.cwd()` read the empty string as "no --root given" and ran against
    # whatever directory the process happened to be in.
    assert rc == 2, err
    assert "root is empty" in err


def test_status_treats_a_missing_entries_directory_like_validate_does(tmp_path, capsys):
    """status is a report over the entries, so a root with no entries directory stops it
    at 2 like the five checkers, rather than printing a clean nothing and exiting 0."""
    nowhere = tmp_path / "nowhere"
    status_rc = cli.main(["--root", str(nowhere), "status"])
    capsys.readouterr()
    validate_rc = cli.main(["--root", str(nowhere), "validate"])
    capsys.readouterr()
    assert status_rc == validate_rc == 2


def test_sha_with_zero_paths_is_a_clean_argparse_error(project, capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--root", str(project.root), "sha"])
    assert exc.value.code == 2
    assert "Traceback" not in capsys.readouterr().err


def test_sha_on_a_nonexistent_path_is_a_clean_error(project, capsys):
    rc = project.cl("sha", str(project.root / "no-such-file.md"))
    err = capsys.readouterr().err
    assert rc == 2
    assert "Traceback" not in err and "unexpected" not in err


@pytest.mark.parametrize(
    "slug",
    ["", "UPPERCASE", "has/slash", "..", "-leading-dash", "unicøde"],
)
def test_hostile_slugs_are_refused_cleanly(project, capsys, slug):
    try:
        rc = cli.main(["--root", str(project.root), "new", slug])
    except SystemExit as exc:  # argparse itself may refuse a leading-dash token
        rc = exc.code
    err = capsys.readouterr().err
    assert rc != 0
    assert "Traceback" not in err
    assert not list(project.entries.glob("*.md"))


def test_an_absurdly_long_slug_is_refused_with_a_specific_message(project, capsys):
    """ENAMETOOLONG used to reach the catch-all handler, which asks the user to file a
    bug report over a mistyped slug."""
    rc = project.cl("new", "x" * 300)
    err = capsys.readouterr().err
    assert rc == 2
    assert "unexpected" not in err, err
    assert "too long" in err


def test_credence_outside_0_1_via_new_is_accepted_at_scaffold_time_and_caught_at_check(
    project, capsys
):
    """`new` does not validate credence — that is `check`'s job, and it does it."""
    rc = project.cl(
        "new",
        "wild-credence",
        "--kind",
        "prediction",
        "--credence",
        "5.0",
        "--resolves-when",
        "x",
    )
    assert rc == 0
    capsys.readouterr()
    rc = project.cl("validate")
    out = capsys.readouterr().out
    assert rc == 1
    assert "credence" in out and "outside" in out


def test_source_add_on_a_nonexistent_file_is_refused_cleanly(project, capsys):
    rc = project.cl(
        "source",
        "add",
        str(project.root / "nope.txt"),
        "--id",
        "missing-src",
        "--type",
        "paper",
        "--citation",
        "x",
    )
    err = capsys.readouterr().err
    assert rc == 2
    assert "Traceback" not in err and "unexpected" not in err


def test_source_add_on_a_binary_file_is_refused_cleanly(project, capsys):
    binary = project.root / "binary.dat"
    binary.write_bytes(bytes(range(256)))
    rc = project.cl(
        "source",
        "add",
        str(binary),
        "--id",
        "binary-src",
        "--type",
        "paper",
        "--citation",
        "x",
    )
    err = capsys.readouterr().err
    assert rc == 2
    assert "not UTF-8 text" in err


def test_source_add_on_an_empty_file_succeeds(project, capsys):
    empty = project.root / "empty.txt"
    empty.write_text("", encoding="utf-8")
    rc = project.cl(
        "source",
        "add",
        str(empty),
        "--id",
        "empty-src",
        "--type",
        "paper",
        "--citation",
        "x",
    )
    err = capsys.readouterr().err
    assert rc == 0, err


def test_source_add_on_a_directory_is_refused_cleanly(project, capsys):
    a_dir = project.root / "a-directory"
    a_dir.mkdir()
    rc = project.cl(
        "source",
        "add",
        str(a_dir),
        "--id",
        "dir-src",
        "--type",
        "paper",
        "--citation",
        "x",
    )
    err = capsys.readouterr().err
    assert rc == 2
    assert "Traceback" not in err and "unexpected" not in err


def test_credence_outside_the_argparse_range_is_a_clean_argparse_type_or_check_error(
    project, capsys
):
    """--credence takes any float argparse can parse; nonsense strings are argparse's
    own clean usage error."""
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "--root",
                str(project.root),
                "new",
                "not-a-float-credence",
                "--kind",
                "prediction",
                "--credence",
                "not-a-number-at-all-nor-inf-nor-nan",
                "--resolves-when",
                "x",
            ]
        )
    assert exc.value.code == 2
    assert "Traceback" not in capsys.readouterr().err


# === E. the environment the process starts in ==========================================


def _committed_entry_carrying_a_bullet(project):
    """A committed entry whose text contains the schema's own `·` separator — the
    character every history check has to read back out of git."""
    project.cl("new", "bullet-bearing")
    path = project.entry("A0001-bullet-bearing.md")
    project.write_full_entry(path)  # its Grounds and Backing are written with `·`
    project.git("init", "-q")
    project.git("add", "-A")
    project.git("commit", "-qm", "first")
    return path


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
def test_under_an_ascii_locale_the_history_checks_still_read_git(project):
    """`text=True` alone decodes git's output with the locale's codec, so under LC_ALL=C
    an entry carrying `·` took the frozen-region and append-only checks down with a
    UnicodeDecodeError — and the crash landed on the check, not on the entry."""
    _committed_entry_carrying_a_bullet(project)
    proc = run_cli(project.root, "validate", env=ASCII_LOCALE)
    assert "UnicodeDecodeError" not in proc.stderr
    assert "unexpected" not in proc.stderr, proc.stderr
    assert proc.returncode == 0, proc.stdout + proc.stderr


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
def test_under_an_ascii_locale_a_failing_diagnostic_still_prints(project):
    """The failure message names the entry text, which carries `·`. An encoding error
    there replaces the explanation with `this is a bug` on exactly the path that was
    about to say what was wrong."""
    path = _committed_entry_carrying_a_bullet(project)
    # A malformed References line, below the append marker. The diagnostic quotes it
    # back, so the message itself carries `·` — the character an ASCII stdout cannot
    # encode, on the one line that was about to explain the failure.
    with path.open("a", encoding="utf-8") as fh:
        fh.write("- 2026-09-05T12:00:00Z · corroborated · grade: measured · author: main\n")
    proc = run_cli(project.root, "validate", env=ASCII_LOCALE)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "UnicodeEncodeError" not in proc.stderr
    assert "unexpected" not in proc.stderr, proc.stderr
    assert "References" in proc.stdout


def test_the_corpus_without_git_says_so_instead_of_asking_for_a_bug_report(project):
    """The corpus applies its history seeds as commits. Without git it cannot run at
    all, and a self-proof that did not run is a refusal, not a crash."""
    proc = run_cli(project.root, "corpus", env={"PATH": "/nonexistent"})
    assert proc.returncode == 2
    assert "git is not on PATH" in proc.stderr
    assert "unexpected" not in proc.stderr and "Traceback" not in proc.stderr


def test_a_ledger_path_naming_a_regular_file_is_a_clean_error(tmp_path, capsys):
    """`ledger = "not-a-dir"` pointing at a file used to reach mkdir() and come back as
    an unexpected NotADirectoryError."""
    root = tmp_path / "proj"
    root.mkdir()
    (root / "not-a-dir").write_text("i am a file", encoding="utf-8")
    cfg = root / "claims-ledger.toml"
    cfg.write_text('[tool.claims-ledger]\nledger = "not-a-dir"\n', encoding="utf-8")
    rc = cli.main(["--root", str(root), "--config", str(cfg), "new", "nowhere-to-write"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "unexpected" not in err and "Traceback" not in err


# === F. the fixes themselves, attacked =================================================
#
# Every case below was found by probing the 2026-09-05 fixes rather than the code they
# replaced, and every one is now the regression test for a second fix. The oracle for
# most of them is metamorphic and blunt — making a thing unreadable must never turn a
# check that fails into a check that passes.

ROOT_USER = os.geteuid() == 0


@pytest.mark.skipif(ROOT_USER, reason="root ignores the permission bits under test")
def test_an_unreadable_entries_directory_is_not_a_clean_pass(project, capsys):
    """A failing check must not become a passing one because the checker lost the right
    to read. The entry below fails validate; taking the read bit off its directory must
    not turn that failure into `0 failure(s)`."""
    path = project.entry("A0001-unreadable-dir.md")
    project.cl("new", "unreadable-dir")
    capsys.readouterr()
    assert project.cl("validate") == 1, "the scaffolded entry is expected to fail validate"
    capsys.readouterr()

    os.chmod(project.entries, 0o111)
    try:
        rc = project.cl("validate")
        out = capsys.readouterr()
    finally:
        os.chmod(project.entries, 0o755)
    assert path.name  # the entry is still there; only the directory's read bit went away
    # It read `validate (0 entries): 0 failure(s)` at rc 0: is_dir() answered True and
    # glob() swallowed the EACCES from scandir. guard() now lists the directory itself.
    assert rc != 0, out.out + out.err
    assert "cannot be listed" in out.err, out.out + out.err


def test_a_fifo_registry_does_not_hang_source_add(project, tmp_path):
    """read_text_or_raise() guards the reads. Nothing guards the append."""
    registry = project.root / "ledger" / "sources.jsonl"
    registry.unlink()
    os.mkfifo(registry)
    source = tmp_path / "a-source.txt"
    source.write_text("Some source text.\n", encoding="utf-8")
    proc = run_cli(
        project.root,
        "source",
        "add",
        str(source),
        "--id",
        "fifo-registry",
        "--type",
        "paper",
        "--citation",
        "X 2020",
        timeout=8,
    )  # it used to never return: open("a") on a FIFO blocks with no reader
    assert proc.returncode in (0, 1, 2)
    assert "not a regular file" in proc.stderr, proc.stdout + proc.stderr


def test_a_ledger_symlinked_out_of_the_root_does_not_write_outside_it(tmp_path, capsys):
    """The config string stays under the root; the directory it names does not."""
    root = tmp_path / "proj"
    root.mkdir()
    outside = tmp_path / "outside-root"
    outside.mkdir()
    (root / "ledger").symlink_to(outside, target_is_directory=True)
    rc = cli.main(["--root", str(root), "new", "escape-by-symlink"])
    out = capsys.readouterr()
    # It used to write A0001-escape-by-symlink.md into `outside` at rc 0 — the very thing
    # confined()'s docstring says must not happen. The check follows symlinks now.
    assert rc != 0 or not list(outside.rglob("*.md")), out.out + out.err
    assert not list(outside.rglob("*.md")), "a file was written outside the root"


def test_document_patterns_cannot_address_files_outside_the_root(tmp_path, capsys):
    """Confinement is a property of the tool, not of four particular keys."""
    root = tmp_path / "proj"
    root.mkdir()
    outside = tmp_path / "outside-root"
    outside.mkdir()
    (outside / "private.md").write_text("cites (A0001-nothing, cites-as-live)\n", encoding="utf-8")
    cfg = root / "claims-ledger.toml"
    cli.main(["--root", str(root), "init"])  # init writes the config; configure after it
    cfg.write_text('[tool.claims-ledger]\ndocuments = ["../outside-root/*.md"]\n', encoding="utf-8")
    capsys.readouterr()
    rc = cli.main(["--root", str(root), "--config", str(cfg), "references"])
    out = capsys.readouterr()
    # It used to print `FAIL ../outside-root/private.md` and that file's citations.
    assert "outside-root/private.md" not in out.out + out.err
    assert rc == 2, out.out + out.err


@pytest.mark.skipif(ROOT_USER, reason="root ignores the permission bits under test")
def test_an_unreadable_document_is_not_silently_treated_as_empty(project, capsys):
    """The document count says it was checked. It was not read."""
    doc = project.root / "cites-a-ghost.md"
    doc.write_text("This cites (A9999-no-such-entry, cites-as-live).\n", encoding="utf-8")
    capsys.readouterr()
    assert project.cl("references") == 1, "a citation of a nonexistent entry must fail"
    before = capsys.readouterr().out
    assert "2 documents" in before, before  # this one and the fixture's docs/note-001.md

    os.chmod(doc, 0o000)
    try:
        rc = project.cl("references")
        out = capsys.readouterr()
    finally:
        os.chmod(doc, 0o644)
    # The failure used to disappear at rc 0 while the document was still counted. It is
    # reported as a document that was not read, and it is out of the count.
    assert rc != 0, out.out + out.err
    assert "cites-a-ghost.md" in out.out, out.out + out.err
    assert "1 document" in out.out, out.out  # and it is no longer counted as checked


def test_init_over_a_file_named_entries_is_a_clean_error(tmp_path, capsys):
    root = tmp_path / "proj"
    (root / "ledger").mkdir(parents=True)
    (root / "ledger" / "entries").write_text("i am a file", encoding="utf-8")
    rc = cli.main(["--root", str(root), "init"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "unexpected" not in err, err


def test_a_directory_named_sources_jsonl_is_a_clean_error(project, tmp_path, capsys):
    registry = project.root / "ledger" / "sources.jsonl"
    registry.unlink()
    registry.mkdir()
    source = tmp_path / "a-source.txt"
    source.write_text("Some source text.\n", encoding="utf-8")
    rc = project.cl(
        "source",
        "add",
        str(source),
        "--id",
        "dir-registry",
        "--type",
        "paper",
        "--citation",
        "X 2020",
    )
    err = capsys.readouterr().err
    assert rc == 2
    assert "unexpected" not in err, err


@pytest.mark.skipif(ROOT_USER, reason="root ignores the permission bits under test")
@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
def test_hook_install_into_a_read_only_hooks_dir_is_a_clean_error(project, capsys):
    project.git("init")
    hooks = project.root / ".git" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    os.chmod(hooks, 0o555)
    try:
        rc = project.cl("hook", "--install")
        err = capsys.readouterr().err
    finally:
        os.chmod(hooks, 0o755)
    assert rc == 2
    assert "unexpected" not in err, err


def test_git_that_never_returns_is_given_up_on_rather_than_waited_for(tmp_path, monkeypatch):
    """LOW-15, which the audit read from the code rather than reproducing: `schema.git()`
    ran without a timeout, so a git that blocks — a credential prompt, a pack it wants to
    recover — hung `validate --cached`, `check`, `resolve` and `sha` with no way out."""
    shim = tmp_path / "bin"
    shim.mkdir()
    # It sleeps rather than blocking forever, so that an unfixed `git()` fails this test
    # instead of hanging the suite it is meant to protect.
    (shim / "git").write_text("#!/bin/sh\nsleep 5\n", encoding="utf-8")
    (shim / "git").chmod(0o755)
    # Prepended, not replaced: the shim's own `sleep` has to be findable, or it exits
    # 127 at once and the test passes without ever exercising the timeout.
    monkeypatch.setenv("PATH", f"{shim}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setattr(schema, "GIT_TIMEOUT", 1)
    started = time.monotonic()
    assert schema.git(tmp_path, "status") is None
    assert time.monotonic() - started < 3, "git() waited out a git that had stopped"


def test_the_corpus_runs_git_the_way_the_checkers_do(monkeypatch):
    """The corpus keeps its own `git()`, and the audit found it had neither the timeout
    nor the explicit codec that `schema.git()` was given."""
    seen = {}

    def fake_run(argv, **kwargs):
        seen.update(kwargs)
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(corpus_run.subprocess, "run", fake_run)
    corpus_run.git(pathlib.Path("."), "status")
    assert seen["timeout"] == corpus_run.GIT_TIMEOUT
    assert seen["encoding"] == "utf-8" and seen["errors"] == "replace"


@pytest.mark.skipif(ROOT_USER, reason="root ignores the permission bits under test")
def test_source_add_into_a_read_only_cache_is_a_clean_error(project, tmp_path, capsys):
    cache = project.root / "ledger" / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    source = tmp_path / "a-source.txt"
    source.write_text("Some source text.\n", encoding="utf-8")
    os.chmod(cache, 0o555)
    try:
        rc = project.cl(
            "source",
            "add",
            str(source),
            "--id",
            "ro-cache",
            "--type",
            "paper",
            "--citation",
            "X 2020",
        )
        err = capsys.readouterr().err
    finally:
        os.chmod(cache, 0o755)
    assert rc == 2
    assert "unexpected" not in err, err
