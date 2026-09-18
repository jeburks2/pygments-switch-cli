# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- A test that resolves an alias in a subprocess outside the project
  directory, which is the only place the rest of the suite does not look.
  Every other test imports the package from the source tree, so they pass
  even when the installed distribution is unimportable and MkDocs is
  rendering every snippet with the plain text lexer.
- A CONTRIBUTING section for that failure, including the macOS editable
  install whose `.pth` file carries the hidden flag that `site.py` skips from
  Python 3.13 on.
- `po` as an OS10 interface type. The CLI expands it to `port-channel`, so it
  is what runbooks are written with, but only Arista, Cisco and FRR knew the
  abbreviation.

### Fixed

- An interface range written as a list of spans -- `interface range Po
  1-19,31-32`, `interface Ethernet1-4,7` -- was highlighted up to the first
  comma, and the rest fell out of the name as a separate number. A VLAN list
  such as `switchport trunk allowed vlan 100,200-300` is still a number,
  because the spaced pattern only applies after an `interface` keyword.

- Link aggregation vocabulary, which the lexers knew only as part of an
  interface name: `port-channel`, `channel-group`, `min-links`,
  `port-priority`, `fallback`, `interfaces` and `timeout` are shared words
  now, the LACP rate values `fast`, `normal` and `slow` are constants, and
  each platform gained its own: `fields` and the `src-mac`/`dst-mac`/
  `src-ip`/`dst-ip` hash fields on EOS, `force`, `src-dst`, `ip-l4port`,
  `rotate`, `asymmetric`, `max-bundle`, `suspend-individual` and
  `graceful-convergence` on NX-OS, `lacp-rate` and `lacp-bypass` on NVUE,
  `slaves` on NCLU.
- `interface_reference()`, a rule for an interface named in the tail of a
  line rather than at its start.
- Port-channel, MLAG and vPC configuration in the EOS, NX-OS, NCLU and NVUE
  examples, which had none.

### Fixed

- A bare `port-channel` -- the word with no number after it, as in
  `port-channel load-balance fields mac dst-mac` or `port-channel min-links
  2` -- was left as plain text, because the word existed only inside the
  interface name patterns. Same for `channel-group` on the platforms whose
  vocabulary did not list it.
- An interface named away from the start of a line with a space before its
  number -- `show interface port-channel 10`,
  `show running-config interface ethernet 1/1` -- is highlighted as an
  interface name. Only the line-initial form was recognized.

## [0.1.0] - 2026-09-17

### Added

- Lexers for Arista EOS, Cisco NX-OS and Dell SmartFabric OS10 configuration.
- Lexers for both Cumulus Linux CLIs: NCLU (`net`) and NVUE (`nv`).
- Lexer for the SONiC `config`/`show` utilities, including command line flags.
- Lexer for FRRouting `frr.conf` files and `vtysh` snippets.
- A shared token scheme across all lexers, documented in the README, so one
  stylesheet themes every platform.
- Recognition of pasted device prompts in both network and Linux styles.
- `analyse_text` implementations so `guess_lexer` can identify a snippet from
  platform-specific markers such as `frr version` or `vlt-domain`.

[Unreleased]: https://github.com/jeburks2/pygments-switch-cli/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jeburks2/pygments-switch-cli/releases/tag/v0.1.0
