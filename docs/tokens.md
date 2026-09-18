# Token scheme

All seven lexers emit the same token types for the same kinds of thing. One
stylesheet themes every platform, and a reader who learns the colors on an
EOS page reads a SONiC page the same way.

| Token | CSS class | Used for |
| --- | --- | --- |
| `Keyword.Namespace` | `.kn` | commands that enter a context: `interface`, `router bgp`, `nv set`, `config` |
| `Keyword` | `.k` | other configuration commands: `hostname`, `ip`, `feature`, `frr` |
| `Keyword.Reserved` | `.kr` | removal and negation: `no`, `default`, `net del`, `nv unset` |
| `Keyword.Constant` | `.kc` | literal values: `up`, `down`, `on`, `off`, `permit`, `deny` |
| `Name.Function` | `.nf` | interface and port names: `Ethernet1/1`, `swp1s0`, `PortChannel001` |
| `Name.Builtin` | `.nb` | option keywords: `description`, `remote-as`, `switchport` |
| `Name.Variable` | `.nv` | operator-chosen names: the `leaf1` in `hostname leaf1` |
| `Name.Attribute` | `.na` | command line flags: `-y`, `--min-links` |
| `Number` | `.m` | IPv4/IPv6 addresses, prefixes and route distinguishers |
| `Number.Hex` | `.mh` | MAC addresses |
| `Number.Integer` | `.mi` | VLAN IDs, AS numbers, MTUs, ranges such as `100,200-300` |
| `String` | `.s` | quoted strings and the free text after `description` |
| `Comment.Single` | `.c1` | `!` and `#` comments |
| `Generic.Prompt` | `.gp` | device prompts in pasted terminal sessions |

## Position decides the meaning

These CLIs reuse the same word as a context keyword and as an option, so the
lexers are line oriented: the first word of a line is read as a command, and
everything after it as options and values.

```eos
vlan 100
   name tenant-a
!
interface Ethernet48
   switchport access vlan 100
```

The `vlan` on line 1 is a context keyword (`.kn`); the `vlan` on line 5 is an
option keyword (`.nb`). Same word, different token, because of where it sits.

## Pasted sessions

Prompts are recognized in both the network and Linux styles, so a snippet
copied straight out of a terminal reads correctly without editing:

```eos
leaf1#show interfaces Ethernet1 status
leaf1(config)#interface Ethernet1
leaf1(config-if-Et1)#no shutdown
```

```sonic
admin@leaf1:~$ show interfaces status
admin@leaf1:~$ sudo config save -y
```

## Recoloring

Any Pygments style works unchanged. To adjust one token, add a stylesheet
rather than writing a whole style — the class names above are stable:

```css title="docs/stylesheets/extra.css"
/* Interface names are what readers scan a config for. */
.highlight .nf {
  color: #e36209;
  font-weight: 700;
}

/* Push prompts into the background of a pasted session. */
.highlight .gp {
  opacity: 0.6;
  user-select: none;
}
```

```yaml title="mkdocs.yml"
extra_css:
  - stylesheets/extra.css
```

This site uses exactly that, minus the color change.

## What stays unhighlighted

Operator-chosen identifiers — peer group names, route-map names, VRF names —
are left as plain text, with two exceptions: the name after `hostname` or
`name`, and anything after `description`. A lexer cannot tell `SPINE` in
`neighbor SPINE activate` from any other bare word without tracking what has
been declared, and guessing produces worse results than leaving it alone.
