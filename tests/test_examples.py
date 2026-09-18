"""Tests driven by the example configurations in ``examples/``.

Each example is named after its lexer's primary alias, so adding a platform
means adding one file here and these tests cover it automatically.
"""

from __future__ import annotations

import pytest
from pygments.lexers import get_lexer_by_name
from pygments.token import Error, Text

from conftest import EXAMPLES
from pygments_switch_cli import ALL_LEXERS

#: A word that no vocabulary covers is fine -- operator-chosen names such as
#: peer group or route-map names are supposed to fall through to plain text.
#: A large share of them, though, means the vocabulary has fallen behind the
#: platform, which is what this ceiling is here to catch.
MAX_PLAIN_TEXT_SHARE = 0.15


def lexer_for(path):
    return get_lexer_by_name(path.stem)


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_has_a_lexer(path):
    """The filename stem is the lexer's primary alias, by convention."""
    assert type(lexer_for(path)) in ALL_LEXERS


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_lexes_without_errors(path):
    tokens = list(lexer_for(path).get_tokens(path.read_text()))
    errors = [value for token, value in tokens if token is Error]
    assert not errors, f"{path.name} produced Error tokens: {errors}"


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_round_trips(path):
    """Concatenated token values must reproduce the input exactly.

    This is the invariant that catches a rule which drops or duplicates
    input, which is easy to do with lookahead and zero-width matches.
    """
    text = path.read_text()
    tokens = lexer_for(path).get_tokens(text)
    assert "".join(value for _, value in tokens) == text


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_is_mostly_classified(path):
    tokens = list(lexer_for(path).get_tokens(path.read_text()))
    significant = [value for _, value in tokens if value.strip()]
    plain = [value for token, value in tokens
             if token is Text and value.strip()]
    share = len(plain) / len(significant)
    assert share <= MAX_PLAIN_TEXT_SHARE, (
        f"{path.name}: {share:.0%} of tokens are unclassified "
        f"({sorted(set(plain))})"
    )


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_analyse_text_identifies_its_own_platform(path):
    """``guess_lexer`` should land on the right platform for a real config."""
    text = path.read_text()
    scores = {cls.name: cls.analyse_text(text) for cls in ALL_LEXERS}
    best = max(scores, key=scores.get)
    assert best == lexer_for(path).name, f"{path.name} scored {scores}"


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_analyse_text_scores_stay_in_range(path):
    """Pygments requires a float between 0 and 1; over-confidence hijacks."""
    text = path.read_text()
    for lexer_class in ALL_LEXERS:
        score = lexer_class.analyse_text(text)
        assert 0.0 <= score <= 1.0, f"{lexer_class.__name__} scored {score}"


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_every_lexer_survives_every_example(path, lexer):
    """Readers paste the wrong language into a fence all the time.

    Whatever the mismatch, a lexer must not emit ``Error`` tokens or lose
    input -- Pygments' ``HtmlFormatter`` would render the former as a red
    smear across the page.
    """
    text = path.read_text()
    tokens = list(lexer.get_tokens(text))
    assert not [value for token, value in tokens if token is Error]
    assert "".join(value for _, value in tokens) == text
