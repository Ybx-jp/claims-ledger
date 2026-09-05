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
signal, not a pass, and is recorded with `xfail(strict=True)` rather than accepted.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile
import unicodedata

import pytest

from claims_ledger import cli
from claims_ledger.config import ConfigError, load_config


def run_cli(root, *args, timeout=10):
    """The installed CLI as a real subprocess, for cases that must be watched for a hang
    rather than trusted to return at all."""
    return subprocess.run(
        [sys.executable, "-m", "claims_ledger", "--root", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


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
    from tests.conftest import ASSERTION

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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: float() accepts non-ASCII Unicode decimal digits, so a "
    "credence written with e.g. Arabic-Indic digits is silently treated as an "
    "ordinary number instead of being reported as malformed",
)
def test_a_credence_written_in_non_ascii_digits_is_rejected(project, capsys):
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
    assert "credence" in out  # expected: flagged as not a plain number; actually: silently accepted


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
    from tests.conftest import ASSERTION

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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: ID_RE and PREFIX_RE use bare `\\d`, which matches any Unicode decimal "
    "digit (category Nd), not just ASCII 0-9. `claims-ledger new --id A０００１ "  # noqa: RUF001
    "slug` (fullwidth digits) is accepted and produces an id that is visually confusable "
    "with A0001 but is a distinct string, and it passes validate's id-format check.",
)
def test_an_id_written_in_non_ascii_digits_is_refused(project, capsys):
    fullwidth_id = "A０００１"  # looks like "A0001"  # noqa: RUF001
    rc = project.cl("new", "homoglyph-id", "--id", fullwidth_id)
    err = capsys.readouterr().err
    # expected: refused as not <letter><four ascii digits>-<slug>
    # actual: rc == 0 and the file is created
    assert rc != 0, err
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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: an absolute `ledger` path in claims-ledger.toml is not confined to "
    '`root` — pathlib\'s `Path(root) / "/abs/path"` discards `root` entirely — so '
    "`claims-ledger new` writes real files outside the project root with no warning.",
)
def test_an_absolute_ledger_path_cannot_escape_the_project_root(tmp_path, capsys):
    root = tmp_path / "proj"
    root.mkdir()
    outside = tmp_path / "outside-root"
    cfg = root / "claims-ledger.toml"
    cfg.write_text(f'[tool.claims-ledger]\nledger = "{outside}"\n', encoding="utf-8")
    rc = cli.main(["--root", str(root), "--config", str(cfg), "new", "escape-attempt"])
    capsys.readouterr()
    # expected: refused, or at least confined under root; actual: files land in `outside`
    assert rc != 0 or not outside.exists()


@pytest.mark.xfail(
    strict=True,
    reason="BUG: a `..`-traversal `ledger` path in claims-ledger.toml is not confined "
    "to `root` either; nothing in from_table() normalizes or contains the path.",
)
def test_a_traversal_ledger_path_cannot_escape_the_project_root(tmp_path, capsys):
    root = tmp_path / "a" / "b" / "proj"
    root.mkdir(parents=True)
    cfg = root / "claims-ledger.toml"
    cfg.write_text('[tool.claims-ledger]\nledger = "../../../outside-root"\n', encoding="utf-8")
    cli.main(["--root", str(root), "--config", str(cfg), "new", "escape-attempt"])
    capsys.readouterr()
    config = load_config(root=root, config_path=cfg)
    resolved = config.ledger_dir.resolve()
    # expected: confined to root; actual: resolves outside `root` entirely
    assert str(resolved).startswith(str(root.resolve()))


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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: when the *entries directory itself* is a symlink loop, is_dir()/glob() "
    "raise OSError(ELOOP) uncaught, and it surfaces through the generic exception "
    "handler as 'unexpected RuntimeError: Symlink loop from ...' instead of a specific, "
    "documented diagnostic.",
)
def test_entries_dir_itself_being_a_symlink_loop_is_reported_cleanly(project, capsys):
    import shutil

    shutil.rmtree(project.entries)
    os.symlink("entries", project.entries)
    rc = project.cl("status")
    err = capsys.readouterr().err
    assert "unexpected" not in err, err
    assert rc == 2


@pytest.mark.xfail(
    strict=True,
    reason="BUG: a FIFO named *.md in the entries directory hangs every command that "
    "loads entries (status, validate, check, ...) forever — Path.read_text() blocks "
    "opening the FIFO for reading with no writer on the other end. There is no timeout "
    "and no specific handling; the process simply never returns.",
)
def test_a_fifo_named_dot_md_does_not_hang_the_tool(project):
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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: `--root ''` is silently treated as 'no --root given' (config.py does "
    "`root or Path.cwd()`, and '' is falsy), so the command silently runs against the "
    "process's actual current working directory instead of refusing the empty value.",
)
def test_an_empty_root_is_refused_rather_than_silently_using_cwd(tmp_path, monkeypatch, capsys):
    unrelated_cwd = tmp_path / "unrelated-cwd"
    unrelated_cwd.mkdir()
    monkeypatch.chdir(unrelated_cwd)
    rc = cli.main(["--root", "", "status"])
    err = capsys.readouterr().err
    # expected: refused (nonzero, explaining --root was empty)
    # actual: rc == 0, having silently used the cwd
    assert rc != 0, err


@pytest.mark.xfail(
    strict=True,
    reason="BUG: cmd_status() never calls guard(), so unlike validate/resolve/references/"
    "propagate/check it does not distinguish a misconfigured root (no entries directory "
    "at all) from a real, empty ledger — both print '0 entries' / 'no entries under ...' "
    "and exit 0. This is exactly the 'clean report over content that was never checked' "
    "failure mode guard()'s own docstring says must never happen.",
)
def test_status_treats_a_missing_entries_directory_like_validate_does(tmp_path, capsys):
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


@pytest.mark.xfail(
    strict=True,
    reason="BUG: an absurdly long slug is accepted by SLUG_RE and only fails at "
    "path.write_text() with OSError(ENAMETOOLONG), which is not one of the specifically "
    "handled exceptions in cli.main() and so surfaces as 'unexpected OSError' instead of "
    "a clean, specific 'slug is too long' diagnostic.",
)
def test_an_absurdly_long_slug_is_refused_with_a_specific_message(project, capsys):
    rc = project.cl("new", "x" * 300)
    err = capsys.readouterr().err
    assert rc != 0
    assert "unexpected" not in err, err


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
