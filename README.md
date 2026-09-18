# pygments-switch-cli

[![PyPI](https://img.shields.io/pypi/v/pygments-switch-cli.svg)](https://pypi.org/project/pygments-switch-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/pygments-switch-cli.svg)](https://pypi.org/project/pygments-switch-cli/)
[![CI](https://github.com/jeburks2/pygments-switch-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/jeburks2/pygments-switch-cli/actions/workflows/ci.yml)
[![License](https://img.shields.io/pypi/l/pygments-switch-cli.svg)](LICENSE)

> **Disclaimer: this project is 100% AI-generated.** Every line of code, test
> and documentation in this repository was written by Claude Opus 5
> (Anthropic), driven through Claude Code. It ships with an automated test
> suite and CI, and the lexers have been exercised against the configurations
> in [`examples/`](examples/) — but the code has not been reviewed line by
> line by a human, and it has not been validated against a broad corpus of
> real production configurations. Treat it as you would any unreviewed
> dependency, and please
> [report anything it gets wrong](https://github.com/jeburks2/pygments-switch-cli/issues).

Pygments lexers for network switch command line interfaces, so configuration
snippets in MkDocs, Sphinx and anything else built on Pygments come out
highlighted instead of grey.

Install it and seven new languages become available to every Pygments
front end — no plugin registration, no theme changes:

```console
pip install pygments-switch-cli
```

````markdown
```eos
interface Ethernet1
   description spine1:Ethernet1/1
   no switchport
   ip address 10.1.1.1/31
```
````

## Supported platforms

| Platform | Aliases | Filenames |
| --- | --- | --- |
| Arista EOS | `eos`, `arista`, `arista-eos`, `aristaeos` | `*.eos` |
| Cisco NX-OS | `nxos`, `nx-os`, `cisco-nxos`, `nexus` | `*.nxos` |
| Dell SmartFabric OS10 | `os10`, `dell-os10`, `dellos10`, `smartfabric` | `*.os10` |
| Cumulus Linux NCLU (`net`) | `nclu`, `cumulus`, `cumulus-nclu`, `net-commands` | `*.nclu` |
| Cumulus Linux NVUE (`nv`) | `nvue`, `nv`, `cumulus-nvue` | `*.nvue` |
| SONiC (`config`/`show`) | `sonic`, `sonic-cli` | `*.sonic` |
| FRRouting / `vtysh` | `frr`, `frr-conf`, `vtysh`, `frrouting` | `frr.conf`, `bgpd.conf`, `zebra.conf`, `*.frr`, … |

Cumulus Linux ships two CLIs — NCLU (`net add ...`) through 4.x and NVUE
(`nv set ...`) from 4.4 onward — so each gets its own lexer. FRRouting is the
routing stack under Cumulus Linux, SONiC and others, and `frr.conf` is what
operators usually paste, so it is lexed separately too.

None of these aliases collide with a lexer built into Pygments, and built-in
lexers always win alias lookups, so a future Pygments release adding its own
`eos` would silently shadow this one. If a snippet suddenly loses its
highlighting after a Pygments upgrade, that is the first thing to check.

## MkDocs

Pygments finds these lexers through the `pygments.lexers` entry point group,
which means MkDocs needs nothing beyond the install — as long as the package
is installed in the *same* environment as MkDocs itself. With
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/):

```yaml
markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.superfences
```

Then use any alias from the table above as the language of a fenced block.
Requirements pinning for a docs build usually looks like:

```
mkdocs-material
pygments-switch-cli
```

Read the Docs, Netlify and GitHub Actions builds all work the same way,
because they all install from that file.

## Sphinx

Sphinx uses Pygments too, so the aliases work in `code-block` directives
once the package is installed:

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

Or from the shell:

```console
pygmentize -l frr -f html -O full frr.conf > frr.html
```

## Token scheme

All seven lexers share one token vocabulary, so a single stylesheet themes
every platform consistently and a reader learns one set of colors.

| Token | CSS class | Used for |
| --- | --- | --- |
| `Keyword.Namespace` | `.kn` | commands that enter a context: `interface`, `router bgp`, `nv set`, `config` |
| `Keyword` | `.k` | other configuration commands: `hostname`, `ip`, `feature`, `frr` |
| `Keyword.Reserved` | `.kr` | removal and negation: `no`, `default`, `net del`, `nv unset` |
| `Keyword.Constant` | `.kc` | literal values: `up`, `down`, `on`, `off`, `permit`, `deny` |
| `Name.Function` | `.nf` | interface and port names: `Ethernet1/1`, `swp1s0`, `PortChannel001` |
| `Name.Builtin` | `.nb` | option keywords: `description`, `remote-as`, `switchport` |
| `Name.Variable` | `.nv` | operator-chosen names: the `leaf1` in `hostname leaf1`, the `tenant-a` in `name tenant-a` |
| `Name.Attribute` | `.na` | command line flags: `-y`, `--min-links` |
| `Number` | `.m` | IPv4/IPv6 addresses, prefixes and route distinguishers |
| `Number.Hex` | `.mh` | MAC addresses |
| `Number.Integer` | `.mi` | VLAN IDs, AS numbers, MTUs, ranges |
| `String` | `.s` | quoted strings and free text after `description` |
| `Comment.Single` | `.c1` | `!` and `#` comments |
| `Generic.Prompt` | `.gp` | device prompts in pasted terminal sessions |

To recolor one of them in Material for MkDocs, add a stylesheet:

```css
/* Make interface names stand out more than the default green. */
.highlight .nf { color: #e36209; font-weight: 700; }
```

The same keyword can be a context command or an option depending on where it
sits, which is the point of the line-oriented design: in `vlan 100` the
`vlan` is a context keyword, while in `switchport trunk allowed vlan 100` it
is an option keyword.

Pasted prompts are recognized in both the network (`leaf1(config-if-Et1)#`)
and Linux (`cumulus@leaf01:~$`) styles, so a snippet copied straight out of a
terminal still reads correctly.

## Development

```console
python -m venv .venv && source .venv/bin/activate
pip install -e '.[test,docs]'
pytest
ruff check pygments_switch_cli/ tests/
mkdocs serve   # demo site rendering every lexer
```

`examples/` holds one configuration per platform; the test suite lexes all of
them and fails on any `Token.Error`, and the demo site embeds the same files,
so an example is both a fixture and documentation.

Adding a platform means a module with a `SwitchCLILexer` subclass, an entry
point in `pyproject.toml`, an example file and a row in the tables above.
See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

BSD 3-Clause. See [LICENSE](LICENSE).
