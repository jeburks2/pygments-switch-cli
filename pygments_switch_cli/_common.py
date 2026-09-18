"""Shared regexes, vocabulary and lexer states for the switch CLI lexers.

Network operating system CLIs differ in vocabulary but share a structure: one
command per line, an optional leading negation (``no``/``del``/``unset``), a
command or context keyword, then a tail of option keywords and values.  The
:class:`SwitchCLILexer` base class below encodes that structure once so each
vendor module only has to supply its own keywords and interface naming scheme.

Every lexer is line oriented.  The ``root`` state is only ever entered at the
start of a line (or after leading indentation), which is what lets ``vlan`` be
highlighted as a context keyword in ``vlan 100`` but as an option keyword in
``switchport access vlan 100``.  Each ``root`` rule pushes the ``line`` state,
which pops on the newline.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from pygments.lexer import RegexLexer, bygroups, include, words
from pygments.token import (
    Comment,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
)

#: A Pygments token rule: a pattern, a token or callback, and optionally the
#: state to switch to.
Rule = tuple[Any, ...]

__all__ = [
    "COMMON_OPTIONS",
    "CONSTANTS",
    "IPV4",
    "IPV4_PREFIX",
    "IPV6",
    "MAC",
    "NEGATIONS",
    "PROMPT",
    "Rule",
    "WORD_END",
    "WORD_START",
    "SwitchCLILexer",
    "interface_re",
    "interface_header",
    "interface_reference",
    "keyword_rule",
    "named_object",
    "option_rule",
]

# --------------------------------------------------------------------------
# Word boundaries
# --------------------------------------------------------------------------

# Network CLI keywords are full of hyphens, and ``\b`` treats a hyphen as a
# boundary: ``\brouter\b`` happily matches the first half of ``router-id``,
# leaving ``-id`` behind as unhighlighted text.  Every keyword rule in this
# package uses these instead.
WORD_START = r"(?<![\w-])"
WORD_END = r"(?![\w-])"

# --------------------------------------------------------------------------
# Value patterns
# --------------------------------------------------------------------------

_OCTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"

#: Dotted quad, e.g. ``10.0.0.1``.
IPV4 = rf"{_OCTET}(?:\.{_OCTET}){{3}}"

#: Dotted quad with a prefix length, e.g. ``10.0.0.0/24``.
IPV4_PREFIX = rf"{IPV4}/(?:3[0-2]|[12]?\d)"

#: Route distinguisher or route target in ``A.B.C.D:NN`` form.
RD = rf"{IPV4}:\d+"

#: Deliberately permissive: real configs contain ``::``, ``fe80::1%eth0`` and
#: ``2001:db8::/32``, and a strict RFC 4291 pattern buys nothing for coloring.
IPV6 = r"(?:[0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}(?:%[\w.-]+)?(?:/\d{1,3})?"

#: Colon, dash and Cisco dotted-triplet MAC formats.  Must be tried before
#: :data:`IPV6`, which also matches the colon form.
MAC = (
    r"\b(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}\b"
    r"|\b(?:[0-9a-f]{4}\.){2}[0-9a-f]{4}\b"
)

#: Device prompts, so a snippet pasted straight out of a terminal still reads
#: correctly.  Covers ``leaf1#``, ``leaf1(config-if-Et1)#`` and the Linux-style
#: ``cumulus@leaf01:mgmt:~$`` prompt used by Cumulus Linux and SONiC.
#:
#: The trailing lookahead allows the command to follow the prompt character
#: with no space, which is how a device echoes it back: ``leaf1#show version``.
#: A letter is as permissive as it gets -- every command in these CLIs starts
#: with one -- because without some restriction any first word ending in ``#``
#: would read as a prompt.  Requiring a space, as this once did, left the
#: whole echoed line to the ``#`` comment rule instead.
PROMPT = (
    r"^(?:[\w.-]+@[\w.-]+:\S*[#$]|[\w.-]+(?:\([^)]*\))?[>#])"
    r"(?=[ \t]|$|[A-Za-z])"
)

# --------------------------------------------------------------------------
# Shared vocabulary
# --------------------------------------------------------------------------

#: Words that remove or revert configuration.  Highlighted as
#: ``Keyword.Reserved`` so a reader can spot them at a glance.
NEGATIONS = ("default", "del", "delete", "no", "purge", "remove", "unset")

#: Literal values rather than option names.  Kept disjoint from the option
#: vocabulary below so ``enable`` in ``ip pim sparse-mode enable`` reads as a
#: value while a top-level ``enable password`` still reads as a command.
CONSTANTS = (
    "absent", "active", "all", "any", "auto", "both", "default", "deny",
    "disable", "disabled", "down", "drop", "enable", "enabled", "false",
    "fast", "forbidden", "inactive", "none", "normal", "off", "on", "permit",
    "present", "slow", "true", "up", "yes",
)

#: Networking vocabulary shared by every platform in this package.  Vendor
#: modules add their own words on top; they must not repeat these.
COMMON_OPTIONS = (
    "access", "access-group", "access-list", "activate", "address",
    "address-family", "advertise", "advertise-all-vni",
    "advertisement-interval", "aggregate-address", "allowas-in", "allowed",
    "always", "area", "arp", "as-path", "attribute", "authentication",
    "autoneg", "autonomous-system", "backup", "bandwidth", "bfd", "bgp",
    "bpduguard", "bridge", "broadcast", "capability", "channel-group",
    "client", "community", "community-list", "confederation", "connected",
    "cost", "dead-interval", "default-information", "default-metric",
    "default-originate", "destination", "dhcp", "distance", "distribute-list",
    "dns", "domain", "domain-name", "dot1q", "downstream", "duplex",
    "ebgp-multihop", "echo", "edge", "egress", "encapsulation", "encrypted",
    "eq", "established", "evpn", "export", "extended", "external", "fabric",
    "fall-over", "fallback", "fast-external-failover", "filter", "flood",
    "flowcontrol", "forward", "forwarding", "gateway", "ge",
    "graceful-restart", "group", "gt", "hello-interval", "hold-time",
    "holdtime", "host", "host-reachability", "id", "identifier", "igmp",
    "import", "ingress", "instance", "interface", "interfaces", "interval",
    "ip", "ip-address", "ipv4", "ipv6", "isis", "keepalive", "key", "l2vpn",
    "label", "lacp", "le", "level", "link", "lldp", "load-balance", "local-as",
    "local-interface", "local-preference", "log", "log-adjacency-changes",
    "log-neighbor-changes", "loopback", "lt", "mac", "mac-address",
    "management", "match", "max-metric", "maximum", "maximum-paths",
    "maximum-prefix", "maximum-routes", "md5", "member", "members", "metric",
    "min-links", "minimum", "mode", "mtu", "multicast", "multihop",
    "multipath", "name", "native", "neighbor", "network", "next-hop",
    "next-hop-self", "no-prepend", "nssa", "origin", "ospf", "out", "override",
    "passive", "passive-interface", "password", "path", "peer", "peer-group",
    "peer-link", "pim", "point-to-point", "policy", "pool", "port",
    "port-channel", "port-priority", "portfast", "preempt", "prefix",
    "prefix-list", "primary", "priority", "profile", "protocol", "proxy-arp",
    "pvid", "range", "rate", "rd", "receive", "redistribute",
    "reference-bandwidth", "remote-as", "replace-as", "retry", "rib", "root",
    "route", "route-map", "route-reflector-client", "route-target", "router",
    "router-id", "routing", "rp-address", "secondary", "security", "send",
    "send-community", "seq", "server", "service-policy", "set", "severity",
    "shared", "shutdown", "snooping", "soft-reconfiguration", "source",
    "source-interface", "speed", "state", "static", "statistics", "sticky",
    "stub", "subnet", "summary-address", "switchport", "sync", "table", "tag",
    "target", "tcp", "template", "threshold", "timeout", "timer", "timers",
    "traffic", "transport", "trunk", "trust", "tunnel", "type", "udp",
    "unicast", "update-source", "uplink", "version", "vids", "vlan", "vni",
    "vrf", "vrrp", "vtep", "vxlan", "weight",
)

#: Keywords whose remainder of line is free text rather than more keywords.
TAIL_STRING_KEYWORDS = (
    "description", "alias", "remark", "comment", "motd", "contact", "location",
)

#: Keywords followed by a single operator-chosen identifier.
NAME_KEYWORDS = ("hostname", "name")


# --------------------------------------------------------------------------
# Rule builders
# --------------------------------------------------------------------------

def _alternation(names: Iterable[str]) -> str:
    """Longest-first alternation, so ``vlan`` wins over ``vl``."""
    return "|".join(sorted((re.escape(n) for n in names), key=len, reverse=True))


def interface_re(names: Iterable[str], bare: Iterable[str] = ()) -> str:
    """Build a regex for interface identifiers.

    ``names`` are prefixes that are always followed by a number, such as
    ``ethernet`` in ``Ethernet1/1.100`` or ``swp`` in ``swp1s0``.  ``bare``
    are complete names that carry no number, such as Cumulus ``lo`` and
    ``peerlink``.  No space is permitted between the prefix and the number:
    that is what keeps the option keyword in ``switchport access vlan 100``
    from being mistaken for an interface name.
    """
    parts = [
        rf"(?:{_alternation(names)})"
        r"\d+(?:s\d+)?(?:[/:]\d+(?:s\d+)?)*(?:\.\d+)?"
        r"(?:-\d+(?:[/:]\d+)*)?"
    ]
    if bare:
        parts.append(rf"(?:{_alternation(bare)})(?:\.\d+)?")
    return WORD_START + r"(?:" + "|".join(parts) + r")" + WORD_END


def _spaced_interface(names: Iterable[str], bare: Iterable[str] = ()) -> str:
    """Interface identifier that tolerates one space before the number.

    Dell OS10 and the interactive form of most CLIs accept a space between the
    interface type and its number, which :func:`interface_re` rejects on
    purpose.  This pattern is only safe where a preceding keyword such as
    ``interface`` says that what follows names an interface: without one,
    ``vlan 100`` in ``switchport access vlan 100`` would match it.
    """
    alt = _alternation(names)
    bare_alt = rf"|(?:{_alternation(bare)})(?:\.\d+)?" if bare else ""
    return (
        rf"(?:(?:{alt})[ \t]?\d+(?:s\d+)?(?:[/:]\d+(?:s\d+)?)*(?:\.\d+)?"
        rf"(?:-[\d/:]+)?){bare_alt}"
    )


def interface_header(
    names: Iterable[str],
    keywords: Iterable[str] = ("interface", "range"),
    bare: Iterable[str] = (),
) -> Rule:
    """Rule for a context line such as ``interface ethernet 1/1/1``.

    Belongs in ``root``: the keyword opens an interface configuration
    context, and the rule pushes ``line`` like every other ``root`` rule.
    """
    return (
        rf"{WORD_START}({_alternation(keywords)})([ \t]+)"
        rf"({_spaced_interface(names, bare)}){WORD_END}",
        bygroups(Keyword.Namespace, Whitespace, Name.Function),
        "line",
    )


def interface_reference(
    names: Iterable[str],
    keywords: Iterable[str] = ("interface", "interfaces", "range"),
    bare: Iterable[str] = (),
) -> Rule:
    """Rule for an interface named in the tail of a line.

    The same spaced spelling :func:`interface_header` accepts also shows up
    away from the start of a line -- ``show interface port-channel 10``,
    ``show running-config interface ethernet 1/1`` -- where the keyword is an
    option rather than a context, so this emits ``Name.Builtin`` for it and
    changes no state.  It belongs in ``line`` ahead of :func:`option_rule`,
    which would otherwise claim the keyword and leave the interface type as
    plain text.
    """
    return (
        rf"{WORD_START}({_alternation(keywords)})([ \t]+)"
        rf"({_spaced_interface(names, bare)}){WORD_END}",
        bygroups(Name.Builtin, Whitespace, Name.Function),
    )


def named_object(keywords: Iterable[str], keyword_token: Any = Keyword) -> Rule:
    """Rule for ``<keyword> <user-chosen-name>``, e.g. ``hostname leaf1``.

    The name is emitted as ``Name.Variable`` so operator-supplied identifiers
    are visually distinct from vocabulary the platform defines.
    """
    return (
        rf"{WORD_START}({_alternation(keywords)})([ \t]+)([^\s!#]+)",
        bygroups(keyword_token, Whitespace, Name.Variable),
        "line",
    )


def keyword_rule(
    keywords: Iterable[str],
    token: Any,
    state: str | None = "line",
) -> Rule:
    """Hyphen-aware rule for a list of command keywords.

    ``state`` is the state to push, or ``None`` to stay put -- which is what
    the leading negation needs, so that the command keyword after ``no`` is
    still matched by the rules that follow.
    """
    rule = (words(keywords, prefix=WORD_START, suffix=WORD_END), token)
    return rule if state is None else rule + (state,)


def option_rule(extra: Iterable[str] = ()) -> Rule:
    """One rule covering the shared vocabulary plus a platform's own words.

    The two vocabularies have to be compiled into a single alternation rather
    than two rules: :func:`pygments.lexer.words` prefers the longest
    alternative, so ``maximum-paths`` wins over ``maximum``, which separate
    rules in priority order could not guarantee.
    """
    merged = tuple(sorted(set(COMMON_OPTIONS) | set(extra)))
    return (words(merged, prefix=WORD_START, suffix=WORD_END), Name.Builtin)


# --------------------------------------------------------------------------
# Base lexer
# --------------------------------------------------------------------------

class SwitchCLILexer(RegexLexer):
    """Base class for the switch CLI lexers; not registered with Pygments.

    Subclasses define a ``root`` state whose rules push ``line``, and a
    ``line`` state ending in ``inherit`` so the shared value, comment and
    fallback rules below apply after the vendor-specific ones.  That ``line``
    state must open with ``include("prelude")`` and must contain an
    :func:`option_rule`, both of which have to outrank the shared rules.
    """

    name = "Switch CLI"
    aliases: list[str] = []
    filenames: list[str] = []
    url = "https://github.com/jeburks2/pygments-switch-cli"

    # Commands are conventionally lowercase, but ``show running-config`` output
    # and vendor documentation are inconsistent about interface name casing.
    flags = re.MULTILINE | re.IGNORECASE

    tokens = {
        "comments": [
            (r"!.*$", Comment.Single),
            (r"#.*$", Comment.Single),
        ],
        "prompt": [
            (PROMPT, Generic.Prompt),
        ],
        "strings": [
            (r'"[^"\n]*"?', String.Double),
            (r"'[^'\n]*'?", String.Single),
        ],
        "constants": [
            (words(CONSTANTS, prefix=WORD_START, suffix=WORD_END),
             Keyword.Constant),
        ],
        "values": [
            (MAC, Number.Hex),
            (RD, Number),
            (IPV4_PREFIX, Number),
            (IPV4, Number),
            (IPV6, Number),
            (r"\b0x[0-9a-f]+\b", Number.Hex),
            (r"\b\d+(?:\.\d+)+\b", Number),
            (r"\b\d+(?:[-,:]\d+)+\b", Number.Integer),
            (r"\b\d+\b", Number.Integer),
        ],
        "flags": [
            (r"(?<![\w-])--?[a-z][\w-]*", Name.Attribute),
        ],
        # Rules that have to be tried before a platform's own vocabulary,
        # because the keyword they start with is in that vocabulary.
        "prelude": [
            (rf"{WORD_START}({_alternation(TAIL_STRING_KEYWORDS)})([ \t]+)"
             r"([^\n]*)",
             bygroups(Name.Builtin, Whitespace, String)),
            (rf"{WORD_START}({_alternation(NAME_KEYWORDS)})([ \t]+)([^\s!#]+)",
             bygroups(Name.Builtin, Whitespace, Name.Variable)),
        ],
        "line": [
            (r"\n", Whitespace, "#pop"),
            (r"[ \t]+", Whitespace),
            include("comments"),
            include("strings"),
            include("constants"),
            include("values"),
            include("flags"),
            (r"[{}\[\](),;]", Punctuation),
            (r"[=<>|+]", Operator),
            (r"[^\s{}\[\](),;=<>|!#]+", Text),
            (r"[!#]", Text),
        ],
    }
