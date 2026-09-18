# FRRouting

Aliases: `frr`, `frr-conf`, `vtysh`, `frrouting`

Filenames: `frr.conf`, `vtysh.conf`, `bgpd.conf`, `zebra.conf`, `ospfd.conf`,
`ospf6d.conf`, `staticd.conf`, `isisd.conf`, `pimd.conf`, `*.frr`

FRR is the routing stack under Cumulus Linux, SONiC and several other
platforms in this package, and `frr.conf` is what operators actually paste
into a runbook, so it gets its own lexer rather than being folded into a
vendor one. Because the filename patterns cover the daemon config files
directly, `pygmentize frr.conf` works with no `-l` flag.

Interface names cover kernel conventions (`swp1`, `eth0`, `ens192`, `bond0`,
`vlan100`, bare `lo`) as well as the vendor-style names FRR sees on other
platforms.

`frr version` and `frr defaults` head almost every `frr.conf` and drive
`analyse_text`.

```frr
--8<-- "examples/frr.frr"
```
