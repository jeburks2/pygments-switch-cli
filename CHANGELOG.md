# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
