"""Tests for how the lexers register themselves with Pygments.

These are the tests that catch a packaging mistake: a lexer that works when
imported directly but never reaches MkDocs because its entry point is missing
or misspelled.
"""

from __future__ import annotations

import os
import pathlib
import stat
import subprocess
import sys
import sysconfig
from importlib.metadata import distribution

import pytest
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename

import pygments_switch_cli
from pygments_switch_cli import ALL_LEXERS, SwitchCLILexer

DISTRIBUTION = "pygments-switch-cli"


def declared_entry_points():
    """The ``pygments.lexers`` entry points this distribution installs."""
    return [ep for ep in distribution(DISTRIBUTION).entry_points
            if ep.group == "pygments.lexers"]


def test_every_lexer_has_an_entry_point():
    """An unregistered lexer is invisible to MkDocs, Sphinx and pygmentize."""
    registered = {ep.load() for ep in declared_entry_points()}
    assert registered == set(ALL_LEXERS)


def test_every_lexer_is_exported():
    for lexer_class in ALL_LEXERS:
        assert lexer_class.__name__ in pygments_switch_cli.__all__
        assert getattr(pygments_switch_cli, lexer_class.__name__) is lexer_class


@pytest.mark.parametrize("lexer_class", ALL_LEXERS,
                         ids=lambda cls: cls.aliases[0])
def test_aliases_resolve_through_pygments(lexer_class):
    """Every documented alias has to work as a fenced code block language."""
    for alias in lexer_class.aliases:
        assert isinstance(get_lexer_by_name(alias), lexer_class)


def test_aliases_are_unique_within_the_distribution():
    seen = {}
    for lexer_class in ALL_LEXERS:
        for alias in lexer_class.aliases:
            assert alias not in seen, (
                f"{alias!r} is claimed by both {seen.get(alias)} and "
                f"{lexer_class.__name__}"
            )
            seen[alias] = lexer_class.__name__


def test_aliases_do_not_collide_with_builtin_pygments_lexers():
    """Built-in lexers win alias lookups, so a collision silently wins.

    ``pygments.lexers._mapping`` is private, but it is the only listing of
    built-in lexers that excludes plugins -- including this one.
    """
    from pygments.lexers._mapping import LEXERS

    builtin = {alias.lower(): name
               for name, _, aliases, _, _ in LEXERS.values()
               for alias in aliases}
    for lexer_class in ALL_LEXERS:
        for alias in lexer_class.aliases:
            assert alias.lower() not in builtin, (
                f"{alias!r} is already a built-in Pygments alias for "
                f"{builtin.get(alias.lower())}, which would shadow "
                f"{lexer_class.__name__}"
            )


@pytest.mark.parametrize("lexer_class", ALL_LEXERS,
                         ids=lambda cls: cls.aliases[0])
def test_filename_patterns_resolve(lexer_class):
    for pattern in lexer_class.filenames:
        filename = pattern.replace("*", "config")
        assert isinstance(get_lexer_for_filename(filename), lexer_class)


@pytest.mark.parametrize("lexer_class", ALL_LEXERS,
                         ids=lambda cls: cls.aliases[0])
def test_lexer_metadata_is_complete(lexer_class):
    assert lexer_class.name
    assert lexer_class.aliases
    assert lexer_class.filenames
    assert lexer_class.mimetypes
    assert lexer_class.url.startswith("https://")


def test_base_class_is_not_registered():
    """``SwitchCLILexer`` is shared machinery, not a language of its own."""
    assert not SwitchCLILexer.aliases
    assert SwitchCLILexer not in ALL_LEXERS
    assert SwitchCLILexer not in {ep.load() for ep in declared_entry_points()}


def hidden_pth_files():
    """Editable-install ``.pth`` files that macOS has flagged hidden.

    Since Python 3.13, ``site`` skips a ``.pth`` file carrying the macOS
    ``UF_HIDDEN`` flag, so an editable install that picks the flag up stops
    putting the project on ``sys.path`` -- silently, and only for processes
    that do not already have the source directory there.
    """
    purelib = pathlib.Path(sysconfig.get_paths()["purelib"])
    return [pth for pth in sorted(purelib.glob("*.pth"))
            if getattr(pth.stat(), "st_flags", 0)
            & getattr(stat, "UF_HIDDEN", 0)]


def test_aliases_resolve_outside_the_project_directory(tmp_path):
    """The check the tests above cannot make, because they run in the source.

    Every other test here imports this package from the working directory,
    which during a test run is the source tree, so they pass whether or not
    the installed distribution is importable.  MkDocs, Sphinx and pygmentize
    are console scripts: they run with the script's own directory on
    ``sys.path``, never the project, and reach the lexers only through the
    install.  When that install is unimportable they do not fail -- Pygments
    falls back to the plain text lexer and every snippet on the site renders
    grey, which is indistinguishable from a lexer that matched nothing.
    """
    script = tmp_path / "resolve.py"
    script.write_text(
        "from pygments.lexers import get_lexer_by_name\n"
        "print(type(get_lexer_by_name('eos')).__name__)\n"
    )
    # PYTHONPATH would put the source tree back on the path and hide exactly
    # the breakage this test is looking for.
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run([sys.executable, str(script)], cwd=tmp_path,
                            env=env, capture_output=True, text=True)

    if result.returncode != 0 and hidden_pth_files():
        pytest.skip(
            "the editable install in this environment is invisible to "
            f"console scripts: {hidden_pth_files()[0].name} carries the "
            "macOS hidden flag, which site.py has skipped since Python 3.13. "
            "Clear it with `chflags nohidden` or run tools with "
            "PYTHONPATH=$PWD; see CONTRIBUTING.md."
        )

    assert result.returncode == 0, (
        "the installed distribution is not importable outside the project "
        "directory, so MkDocs and pygmentize cannot load these lexers:\n"
        f"{result.stderr}"
    )
    assert "AristaEOSLexer" in result.stdout


def test_version_is_importable():
    assert pygments_switch_cli.__version__
    assert distribution(DISTRIBUTION).version == pygments_switch_cli.__version__
