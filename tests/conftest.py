"""Shared fixtures and helpers for the test suite."""

from __future__ import annotations

import pathlib

import pytest

from pygments_switch_cli import ALL_LEXERS

#: Repository root, so tests can reach ``examples/`` when run from anywhere.
ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Example configurations, named after each lexer's primary alias.
EXAMPLES = sorted((ROOT / "examples").iterdir())


def significant(lexer, text):
    """Lex ``text`` and drop the whitespace-only tokens.

    Tests care about which token a word got, not about how the whitespace
    between words was split up.
    """
    return [(token, value) for token, value in lexer.get_tokens(text)
            if value.strip()]


def token_for(lexer, text, value):
    """Return the token type ``lexer`` assigns to ``value`` in ``text``."""
    matches = [token for token, got in significant(lexer, text) if got == value]
    if not matches:
        raise AssertionError(
            f"{lexer.name} did not produce {value!r} as a single token in "
            f"{text!r}; got {significant(lexer, text)}"
        )
    return matches[0]


@pytest.fixture(params=ALL_LEXERS, ids=lambda cls: cls.aliases[0])
def lexer(request):
    """Each lexer in the distribution, one test run apiece."""
    return request.param()
