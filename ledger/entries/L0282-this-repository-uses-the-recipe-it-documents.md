---
id: L0282-this-repository-uses-the-recipe-it-documents
kind: claim
stated: 2026-09-20T12:11:42-07:00
author: main
grade: measured
supersedes: none
verbatim_sha: f0aeff20e9b73b1f4abad00d1afeb3ab3b10cf81d9f8a3d565e6d870a0963a3d
---

## Assertion

This repository's own `code` section pattern is the recipe the package documents, and a test holds the two together.

## Scope

metric: whether the configured pattern and the documented recipe are one string
cohort: the `code` key of this repository's section-patterns table
condition: the package documents a recipe for Python at all

## Grounds

- code: tests/test_section_scoping.py § "test_this_repository_uses_the_code_recipe_it_documents" =sha256:b090fe28b149bfccc2e79c7b8718813fb30bca6a47594c82480b47cba62dc64c

## Warrant

The test reads the pattern out of pyproject.toml and the recipe out of every file that documents one, and compares them. The two were different until 2026-09-20 and neither was better: the documented recipe could not reach an assignment, and this repository's could not reach a decorator. A ledger whose own entries are the argument that the checkers work cannot run a pattern it tells every other project not to use, and nothing but a test notices when one of the two is edited.

## Backing

none

<!-- APPEND BELOW THIS LINE ONLY -->

## Verdicts

## References

- CLAUDE.md · standing · cites-as-live
