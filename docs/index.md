# pygments-switch-cli

Pygments lexers for network switch command line interfaces, so configuration
snippets in MkDocs, Sphinx and anything else built on Pygments come out
highlighted instead of grey.

!!! warning "This project is 100% AI-generated"

    Every line of code, test and documentation here was written by Claude
    Opus 5 (Anthropic), driven through Claude Code. It ships with an
    automated test suite and CI, and the lexers have been exercised against
    the configurations shown on the platform pages — but the code has not
    been reviewed line by line by a human, and it has not been validated
    against a broad corpus of real production configurations. Treat it as you
    would any unreviewed dependency, and please
    [report anything it gets wrong](https://github.com/jeburks2/pygments-switch-cli/issues).

```console
pip install pygments-switch-cli
```

That is the whole setup. Pygments discovers the lexers through an entry point,
so seven new languages become available to every Pygments front end with no
plugin list to edit and no theme to change:

````markdown
```eos
interface Ethernet1
   description spine1:Ethernet1/1
   no switchport
   ip address 10.1.1.1/31
```
````

renders as

```eos
interface Ethernet1
   description spine1:Ethernet1/1
   no switchport
   ip address 10.1.1.1/31
```

## Supported platforms

| Platform | Aliases | Filenames |
| --- | --- | --- |
| [Arista EOS](platforms/arista-eos.md) | `eos`, `arista`, `arista-eos`, `aristaeos` | `*.eos` |
| [Cisco NX-OS](platforms/cisco-nxos.md) | `nxos`, `nx-os`, `cisco-nxos`, `nexus` | `*.nxos` |
| [Dell SmartFabric OS10](platforms/dell-os10.md) | `os10`, `dell-os10`, `dellos10`, `smartfabric` | `*.os10` |
| [Cumulus Linux NCLU](platforms/cumulus.md) | `nclu`, `cumulus`, `cumulus-nclu`, `net-commands` | `*.nclu` |
| [Cumulus Linux NVUE](platforms/cumulus.md) | `nvue`, `nv`, `cumulus-nvue` | `*.nvue` |
| [SONiC](platforms/sonic.md) | `sonic`, `sonic-cli` | `*.sonic` |
| [FRRouting](platforms/frr.md) | `frr`, `frr-conf`, `vtysh`, `frrouting` | `frr.conf`, `bgpd.conf`, `*.frr`, … |

Every page under **Platforms** shows a full example config rendered by its
lexer, so you can see what your docs will look like before installing
anything. All seven share [one token scheme](tokens.md), which means a single
stylesheet themes them consistently and a reader learns one set of colors.

## Why these platforms

Pygments has excellent coverage of programming languages and almost none of
network operating systems. A datacenter fabric runbook tends to mix several at
once — a leaf config, the FRR stanza underneath it, and the `nv set` commands
that produced them — and all three arrive as unhighlighted text.

[Get set up →](setup.md){ .md-button .md-button--primary }
