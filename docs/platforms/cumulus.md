# Cumulus Linux

Cumulus Linux ships two generations of CLI, so this package has two lexers.
Both are verb-first rather than context-based: the leading command word
decides how the rest of the line reads, and there is no configuration mode to
track.

Interface names follow Linux conventions — `swp1`, breakout subports
(`swp1s0`), ranges (`swp1-48`), `bond0`, `vlan100`, `peerlink.4094` and bare
`lo`.

## NVUE — `nv`

Aliases: `nvue`, `nv`, `cumulus-nvue` · Filenames: `*.nvue`

The CLI introduced in Cumulus Linux 4.4 and the only one in 5.x. `nv set` and
`nv config apply` read as commands, `nv unset` as a removal, and the values
`on`/`off`/`up`/`down` as literals.

```nvue
--8<-- "examples/nvue.nvue"
```

## NCLU — `net`

Aliases: `nclu`, `cumulus`, `cumulus-nclu`, `net-commands` · Filenames: `*.nclu`

The CLI through Cumulus Linux 4.x, still what most existing runbooks contain.
`net add` and `net commit` read as commands; `net del`, `net clear` and
`net abort` are highlighted as removals, since those are the lines a reader
needs to notice before pasting.

```nclu
--8<-- "examples/nclu.nclu"
```

!!! tip "The routing config underneath"

    On both generations, `net show configuration commands` and
    `nv config show` describe the switch, but BGP itself is FRRouting. When
    you are quoting `/etc/frr/frr.conf` rather than the CLI that produced it,
    use the [`frr` lexer](frr.md).
