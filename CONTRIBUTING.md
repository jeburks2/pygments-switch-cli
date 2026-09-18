# Contributing

Bug reports about a mis-highlighted line are welcome and easy to act on:
paste the line, say which platform it came from, and say what it should have
been highlighted as. Vocabulary gaps are the expected kind of bug here.

## Getting set up

```console
python -m venv .venv && source .venv/bin/activate
pip install -e '.[test,docs]'
pytest
```

The lexers reach MkDocs and Sphinx through a `pygments.lexers` entry point,
which only exists once the distribution is installed — importable is not
enough. After editing `pyproject.toml`, reinstall.

### If every snippet renders grey

`mkdocs`, `pygmentize` and `sphinx-build` are console scripts: they run with
their own directory on `sys.path`, never the project, so they load these
lexers only through the installed distribution. When that install is not
importable they do not fail. Pygments falls back to its plain text lexer and
the whole site renders unhighlighted, which looks exactly like a lexer that
matched nothing. `pytest` does not notice either, because it imports the
package from the working directory — `test_aliases_resolve_outside_the_project_directory`
is the one test that runs outside it and does.

On macOS the usual cause is the editable install itself. `pip install -e .`
writes `site-packages/_editable_impl_pygments_switch_cli.pth`, and if that
file picks up the macOS `hidden` flag, `site.py` skips it — Python 3.13 and
later ignore hidden `.pth` files deliberately. Some managed Macs re-apply the
flag within seconds of it being cleared.

```console
ls -lO .venv/lib/python*/site-packages/*.pth   # look for "hidden"
chflags nohidden .venv/lib/python*/site-packages/*.pth
```

If the flag keeps coming back, put the project on the path for the command
that needs it instead, which needs no install at all:

```console
PYTHONPATH=$PWD mkdocs serve
```

A plain `pip install .` also works, at the cost of reinstalling after every
edit to a lexer.

## Adding a platform

1. Add a module with a `SwitchCLILexer` subclass. `pygments_switch_cli/arista.py`
   is the model for a context-based CLI (Cisco-style configuration) and
   `pygments_switch_cli/cumulus.py` for a verb-first one (`net add …`,
   `nv set …`).
2. Export the class from `pygments_switch_cli/__init__.py` and add it to
   `ALL_LEXERS`.
3. Register it in the `[project.entry-points."pygments.lexers"]` table in
   `pyproject.toml`. A test checks that this table and `ALL_LEXERS` agree.
4. Add a realistic configuration to `examples/`, named after the lexer's
   primary alias — `examples/eos.eos`. `tests/test_examples.py` picks it up
   automatically and fails if it produces any `Token.Error`, loses input, or
   leaves more than 15% of its words unclassified.
5. Add a page under `docs/platforms/`, a row in `mkdocs.yml`'s nav, and a row
   in the tables in `README.md` and `docs/index.md`.

## Conventions worth knowing

- **The `root` state is the start of a line.** Every `root` rule pushes
  `line`, which pops at the newline. That is what lets the same word be a
  context keyword at the start of a line and an option keyword inside one:
  `vlan 100` versus `switchport access vlan 100`.
- **A `line` state opens with `include("prelude")`** and contains exactly one
  `option_rule(...)`, then ends with `inherit`. The prelude holds the rules
  that must outrank platform vocabulary, such as the free text after
  `description`.
- **Use `keyword_rule()` and `option_rule()`** rather than calling `words()`
  directly. They apply the hyphen-aware word boundaries — a plain `\b`
  matches `router` inside `router-id`, leaving `-id` as unhighlighted text —
  and `option_rule` compiles the shared and platform vocabularies into a
  single alternation, because Pygments prefers the longest alternative within
  one rule but not across two.
- **Vocabulary lists stay disjoint.** A word belongs either to
  `COMMON_OPTIONS` in `_common.py` or to one platform's list, never both, and
  never to both a platform list and `CONSTANTS`. Tests enforce this. A
  verb-first platform may deliberately override a shared word — SONiC reads
  `set` and `shutdown` as verbs — and does so with its own rule ahead of
  `option_rule`, not by duplicating the word.
- **Interface patterns must not allow a space** before the number, or the
  `vlan 100` in `switchport access vlan 100` is mistaken for an interface.
  The relaxed, spaced form belongs in `interface_header()`, where a preceding
  `interface` keyword makes it unambiguous.
- **Leave operator-chosen names alone.** Peer group, route-map and VRF names
  stay plain text. A lexer cannot tell `SPINE` in `neighbor SPINE activate`
  from any other bare word without tracking declarations, and guessing reads
  worse than not guessing.
- **Keep `analyse_text` scores modest.** They only matter to `guess_lexer`,
  and an over-confident score hijacks other people's snippets.

## Before opening a pull request

```console
pytest
ruff check pygments_switch_cli/ tests/
mypy --ignore-missing-imports pygments_switch_cli/
python -m build && twine check --strict dist/*
mkdocs build --strict
```

Do not run `ruff format`. The vocabulary tuples are hand-wrapped, and the
formatter's magic trailing comma would put each of the several hundred words
on its own line.

## Releasing

1. Update `__version__` in `pygments_switch_cli/__about__.py` and move the
   `CHANGELOG.md` entries from Unreleased into a new version heading.
2. Tag `vX.Y.Z` and publish a GitHub release. `.github/workflows/publish.yml`
   builds, checks that the tag matches `__version__`, and uploads to PyPI
   through Trusted Publishing — there is no API token.
