"""Lexer for FRRouting configuration and the ``vtysh`` CLI.

FRR is the routing stack underneath Cumulus Linux, SONiC and several other
platforms in this package, and its ``frr.conf`` is the file operators most
often paste into documentation, so it gets its own lexer rather than being
folded into a vendor one.
"""

from __future__ import annotations

import re

from pygments.lexer import default, include, inherit
from pygments.token import Keyword, Name, Whitespace

from ._common import (
    NEGATIONS,
    SwitchCLILexer,
    interface_header,
    interface_re,
    interface_reference,
    keyword_rule,
    named_object,
    option_rule,
)

__all__ = ["FRRLexer"]

#: FRR names interfaces the way the kernel does, but it also runs on
#: platforms that use vendor-style names.
INTERFACES = (
    "swp", "eth", "ens", "eno", "enp", "enx", "bond", "br", "vlan", "vx",
    "vxlan", "vni", "dummy", "tun", "tap", "gre", "sit", "wg", "veth",
    "ethernet", "port-channel", "po",
)

#: Interface names that carry no number.
BARE_INTERFACES = ("lo",)

#: Commands that enter a configuration context.
MODE_KEYWORDS = (
    "address-family", "bfd", "interface", "key", "line", "mpls-te", "pbr-map",
    "route-map", "router", "segment-routing", "srv6", "vni", "vrf",
)

#: Context commands that are followed by an operator-chosen name.
NAMED_MODES = ("route-map", "pbr-map")

#: Top-level commands that stay on one line.
COMMANDS = (
    "access-list", "agentx", "allow-external-route-update", "banner", "bgp",
    "debug", "domainname", "dump", "enable", "end", "exit",
    "exit-address-family", "exit-vni", "exit-vrf", "fpm", "frr", "hostname",
    "ip", "ipv6", "log", "mpls", "nht", "password", "ptm-enable", "router-id",
    "service", "table", "username", "vrrp", "write", "zebra",
)

#: FRR vocabulary on top of the shared networking words in ``_common``.
OPTIONS = (
    "advertise-default-gw", "advertise-svi-ip", "alerts", "as-notation",
    "as-override", "attribute-unchanged", "bestpath", "coalesce-time",
    "confed", "critical", "datacenter", "debugging", "defaults",
    "deterministic-med", "dont-capability-negotiate",
    "ebgp-requires-policy", "emergencies", "enforce-first-as", "errors",
    "flowspec", "informational", "integrated-vtysh-config", "ipv4-unicast",
    "labeled-unicast", "local-role", "multipath-relax",
    "network-import-check", "notifications", "opaque", "read-quanta",
    "route-server-client", "rpki", "sid", "solo", "strict-capability-match",
    "suppress-fib-pending", "syslog", "traditional", "ttl-security",
    "unnumbered", "update-delay", "vrf-lite", "vty", "vtysh", "warnings",
    "write-quanta", "zebra",
)


class FRRLexer(SwitchCLILexer):
    """Lexer for FRRouting ``frr.conf`` files and ``vtysh`` snippets."""

    name = "FRRouting"
    url = "https://docs.frrouting.org/"
    aliases = ["frr", "frr-conf", "vtysh", "frrouting"]
    filenames = [
        "frr.conf", "vtysh.conf", "bgpd.conf", "zebra.conf", "ospfd.conf",
        "ospf6d.conf", "staticd.conf", "isisd.conf", "pimd.conf", "*.frr",
    ]
    mimetypes = ["text/x-frr"]

    tokens = {
        "root": [
            (r"[ \t]+", Whitespace),
            (r"\n", Whitespace),
            include("comments"),
            include("prompt"),
            keyword_rule(NEGATIONS, Keyword.Reserved, state=None),
            interface_header(INTERFACES, bare=BARE_INTERFACES),
            named_object(("hostname", "domainname")),
            named_object(NAMED_MODES, keyword_token=Keyword.Namespace),
            keyword_rule(MODE_KEYWORDS, Keyword.Namespace),
            keyword_rule(COMMANDS, Keyword),
            default("line"),
        ],
        "line": [
            include("prelude"),
            interface_reference(INTERFACES, bare=BARE_INTERFACES),
            (interface_re(INTERFACES, bare=BARE_INTERFACES), Name.Function),
            option_rule(OPTIONS),
            inherit,
        ],
    }

    def analyse_text(text):
        """``frr version``/``frr defaults`` head almost every frr.conf."""
        score = 0.0
        if re.search(r"^frr version \d", text, re.M):
            score += 0.5
        for pattern, weight in (
            (r"^frr defaults (?:traditional|datacenter)", 0.3),
            (r"^\s*exit-address-family\b", 0.2),
            (r"^\s*service integrated-vtysh-config", 0.2),
        ):
            if re.search(pattern, text, re.M):
                score += weight
        return min(score, 1.0)
