"""Invariants the keyword lists have to keep.

The lexers compile one alternation per line state out of the shared
vocabulary plus a platform's own words, and a word that appears in both lists
makes the intended token for it ambiguous. These tests keep the lists honest.
"""

from __future__ import annotations

import pytest

from pygments_switch_cli import arista, cisco, cumulus, dell, frr, sonic
from pygments_switch_cli._common import (
    COMMON_OPTIONS,
    CONSTANTS,
    NEGATIONS,
    WORD_END,
    WORD_START,
)

#: Every platform vocabulary, by the name it is documented under.
VOCABULARIES = {
    "arista": arista.OPTIONS,
    "cisco": cisco.OPTIONS,
    "dell": dell.OPTIONS,
    "frr": frr.OPTIONS,
    "sonic": sonic.OPTIONS,
    "cumulus.shared": cumulus.SHARED_OPTIONS,
    "cumulus.nclu": cumulus.NCLU_OPTIONS,
    "cumulus.nvue": cumulus.NVUE_OPTIONS,
}


@pytest.mark.parametrize("name", sorted(VOCABULARIES))
def test_platform_words_do_not_repeat_the_shared_vocabulary(name):
    overlap = sorted(set(VOCABULARIES[name]) & set(COMMON_OPTIONS))
    assert not overlap, (
        f"{name} repeats words already in COMMON_OPTIONS: {overlap}"
    )


@pytest.mark.parametrize("name", sorted(VOCABULARIES))
def test_platform_words_do_not_shadow_constants(name):
    """A word cannot be both an option name and a literal value."""
    overlap = sorted(set(VOCABULARIES[name]) & set(CONSTANTS))
    assert not overlap, f"{name} shadows CONSTANTS: {overlap}"


@pytest.mark.parametrize("name", sorted(VOCABULARIES))
def test_platform_words_are_unique(name):
    words = VOCABULARIES[name]
    assert len(words) == len(set(words)), f"{name} has duplicates"


@pytest.mark.parametrize("vocabulary", [COMMON_OPTIONS, CONSTANTS, NEGATIONS],
                         ids=["common_options", "constants", "negations"])
def test_shared_vocabularies_are_sorted_and_unique(vocabulary):
    assert list(vocabulary) == sorted(vocabulary)
    assert len(vocabulary) == len(set(vocabulary))


@pytest.mark.parametrize("name", sorted(VOCABULARIES))
def test_words_are_lowercase(name):
    """Lists are matched case-insensitively; mixed case hides duplicates."""
    assert all(word == word.lower() for word in VOCABULARIES[name])


def test_word_boundaries_treat_hyphens_as_word_characters():
    """The regression that makes ``router-id`` lex as ``router`` + ``-id``."""
    import re

    pattern = re.compile(WORD_START + "router" + WORD_END)
    assert pattern.search("router bgp 65001")
    assert not pattern.search("bgp router-id 10.0.0.1")
    assert not pattern.search("inter-router link")
