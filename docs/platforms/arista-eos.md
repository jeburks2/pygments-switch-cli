# Arista EOS

Aliases: `eos`, `arista`, `arista-eos`, `aristaeos` · Filenames: `*.eos`

EOS configuration and CLI snippets. The lexer knows the short interface forms
EOS accepts and prints — `Et1`, `Po10`, `Ma1`, `Vl100` — alongside the long
ones, and handles subinterfaces (`Ethernet1.100`) and the platform-specific
types (`Vxlan1`, `Recirc-Channel501`, `Peer-Ethernet1`, `Dps1`).

`analyse_text` recognizes the `! device: … EOS-…` header that
`show running-config` writes, so `guess_lexer` identifies a saved EOS config
without a filename.

````markdown
```eos
--8<-- "examples/eos.eos"
```
````

```eos
--8<-- "examples/eos.eos"
```
