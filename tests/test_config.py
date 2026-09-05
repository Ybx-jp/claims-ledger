"""Configuration is discovered, validated, and refused when it says something impossible.

A misconfigured ledger that checks nothing is worse than none, so the loader raises
rather than defaulting past a key it does not understand.
"""

import pytest

from claims_ledger.config import (
    ConfigError,
    default_config,
    find_config_file,
    from_table,
    load_config,
)


def write(path, text):
    path.write_text(text, encoding="utf-8")
    return path


def test_defaults_put_the_ledger_under_the_root(tmp_path):
    config = default_config(tmp_path)
    assert config.entries_dir == tmp_path / "ledger" / "entries"
    assert config.registry == tmp_path / "ledger" / "sources.jsonl"
    assert config.cache == tmp_path / "ledger" / "cache"
    assert config.evidence_types == ("lab", "experiment")
    assert config.ground_types == ("lab", "experiment", "entry", "source", "search")


def test_a_standalone_file_is_found_from_a_subdirectory(tmp_path):
    write(tmp_path / "claims-ledger.toml", 'ledger = "record"\n')
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    assert find_config_file(deep) == tmp_path / "claims-ledger.toml"
    assert load_config(root=tmp_path).ledger_dir == tmp_path / "record"


def test_a_pyproject_counts_only_when_it_carries_the_table(tmp_path):
    write(tmp_path / "pyproject.toml", '[project]\nname = "unrelated"\n')
    assert find_config_file(tmp_path) is None
    write(
        tmp_path / "pyproject.toml",
        '[project]\nname = "unrelated"\n\n[tool.claims-ledger]\nledger = "claims"\n',
    )
    assert find_config_file(tmp_path) == tmp_path / "pyproject.toml"
    assert load_config(root=tmp_path).ledger_dir == tmp_path / "claims"


def test_the_table_may_be_nested_or_bare_in_a_standalone_file(tmp_path):
    write(tmp_path / "claims-ledger.toml", '[tool.claims-ledger]\nledger = "nested"\n')
    assert load_config(root=tmp_path).ledger_dir == tmp_path / "nested"


def test_an_unknown_key_is_an_error(tmp_path):
    with pytest.raises(ConfigError, match="unknown key"):
        from_table({"ledgers": "typo"}, tmp_path)


def test_a_key_of_the_wrong_type_is_an_error(tmp_path):
    with pytest.raises(ConfigError, match="documents is str"):
        from_table({"documents": "*.md"}, tmp_path)


def test_an_evidence_type_may_not_shadow_a_reserved_pointer(tmp_path):
    with pytest.raises(ConfigError, match="reserved pointer type"):
        from_table({"evidence-plain": ["source"]}, tmp_path)


def test_an_evidence_type_is_sectioned_or_plain_but_not_both(tmp_path):
    with pytest.raises(ConfigError, match="both sectioned and plain"):
        from_table({"evidence-sectioned": ["run"], "evidence-plain": ["run"]}, tmp_path)


def test_there_must_be_some_evidence_type(tmp_path):
    with pytest.raises(ConfigError, match="no evidence types"):
        from_table({"evidence-sectioned": [], "evidence-plain": []}, tmp_path)


def test_the_propagation_author_must_be_allowed_to_write_a_verdict(tmp_path):
    with pytest.raises(ConfigError, match="propagation-author"):
        from_table({"verdict-authors": ["me"], "propagation-author": "machine"}, tmp_path)


def test_an_archived_prefix_is_one_uppercase_letter(tmp_path):
    with pytest.raises(ConfigError, match="archived prefix"):
        from_table({"archived-prefixes": ["CP"]}, tmp_path)


def test_a_missing_named_configuration_file_is_an_error(tmp_path):
    with pytest.raises(ConfigError, match="no configuration file"):
        load_config(config_path=tmp_path / "absent.toml")
