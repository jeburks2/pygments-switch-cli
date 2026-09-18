# SONiC

Aliases: `sonic`, `sonic-cli` · Filenames: `*.sonic`

SONiC's CLI is a set of Linux utilities rather than a configuration grammar,
so this lexer reads lines verb-first: the utility (`config`, `show`,
`sonic-clear`, `sonic-cfggen`, `sonic-installer`, `vtysh`) comes first, then a
subcommand, then arguments.

Two things are highlighted that the other lexers have no use for: command line
flags such as `-y` and `--min-links`, and the `sudo` most SONiC documentation
puts in front of `config`. Subcommands that remove or stop something (`del`,
`remove`, `shutdown`, `disable`) get the removal token, the same one `no` gets
on a Cisco-style platform.

Port names cover the chassis and multi-ASIC types as well as the front panel
ones: `Ethernet0`, `PortChannel001`, `Vlan100`, `Ethernet-BP0`.

```sonic
--8<-- "examples/sonic.sonic"
```

!!! note "config_db.json"

    SONiC's persisted configuration is JSON, which Pygments already
    highlights — use `json` for those blocks. This lexer is for the commands
    that read and write it.
