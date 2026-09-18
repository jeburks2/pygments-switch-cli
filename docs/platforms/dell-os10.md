# Dell SmartFabric OS10

Aliases: `os10`, `dell-os10`, `dellos10`, `smartfabric` · Filenames: `*.os10`

OS10 writes `interface ethernet1/1/1` in its running configuration but accepts
`interface ethernet 1/1/1` interactively, and both spellings are highlighted
as interface names. Ranges work too, which matters for
`discovery-interface ethernet1/1/29-1/1/30` and `interface range`.

VLT (`vlt-domain`, `vlt-port-channel`, `vlt-mac`), `virtual-network` and
`interface breakout` are the OS10-specific vocabulary, and the first two drive
`analyse_text`.

```os10
--8<-- "examples/os10.os10"
```
