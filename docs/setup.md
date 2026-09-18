# Setup

## MkDocs

Install the package into the same environment as MkDocs, and use any alias
from the table on the [home page](index.md) as a fenced block language:

```yaml title="mkdocs.yml"
markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.superfences
```

```text title="requirements.txt"
mkdocs-material
pygments-switch-cli
```

Nothing goes in the `plugins:` list. These are Pygments lexers, not MkDocs
plugins, and `pymdownx.highlight` hands unknown languages straight to
Pygments.

!!! warning "Same environment, not just the same machine"

    The most common failure is installing into a different virtualenv than
    the one running `mkdocs build`. If a fence stays grey, check
    `pygmentize -L lexers | grep -i arista` using the `pygmentize` on the same
    `PATH` as your `mkdocs`.

For CI builds, Read the Docs and Netlify, add the package to the same
requirements file the build already installs — there is nothing
platform-specific to configure.

## Sphinx

```rst
.. code-block:: nvue

   nv set interface swp1-4 link state up
   nv config apply
```

## Direct use

```python
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

html = highlight(config_text, get_lexer_by_name("os10"), HtmlFormatter())
```

```console
pygmentize -l frr -f html -O full frr.conf > frr.html
```

Because each lexer declares filename patterns, `pygmentize` also guesses from
the filename alone for the distinctive ones:

```console
pygmentize frr.conf
pygmentize fabric.os10
```

## Guessing the platform

Each lexer implements `analyse_text`, keyed to markers that only appear on
one platform — `frr version` in an `frr.conf`, `vlt-domain` on OS10,
`switchname` on NX-OS, `! device: ... EOS-` in an EOS running-config. That
makes `guess_lexer` usable when you are batch-converting a directory of
configs whose origin you do not know:

```python
from pygments.lexers import guess_lexer

guess_lexer(pathlib.Path("unknown-config.txt").read_text()).name
```

The scores are deliberately modest, so a snippet that looks like something
else is left to whichever lexer is more confident.

## Troubleshooting

**A fence renders grey.** The package is not installed in the environment
running the build, or the alias is misspelled. `pygmentize -L lexers` lists
what Pygments can actually see.

**Highlighting disappeared after upgrading Pygments.** Built-in lexers win
alias lookups over plugins. None of these aliases collide with a built-in
lexer today, and a test in this repository checks that on every release, but a
future Pygments release could claim one. Switching to a second alias from the
table is the immediate fix; please
[open an issue](https://github.com/jeburks2/pygments-switch-cli/issues) so it
can be renamed.

**A word is highlighted wrong.** Vocabulary gaps are the expected kind of bug
here. Paste the line, name the platform, and say what it should have been.
