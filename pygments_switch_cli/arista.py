"""Lexer for the Arista EOS command line interface."""

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

__all__ = ["AristaEOSLexer"]

#: Interface types, including the short forms EOS accepts and emits
#: (``Et1``, ``Po10``, ``Ma1``).
INTERFACES = (
    "ethernet", "et", "management", "ma", "vlan", "vl", "port-channel", "po",
    "loopback", "lo", "vxlan", "vx", "tunnel", "tu", "recirc-channel",
    "peer-ethernet", "fabric", "dps", "unconnected",
)

#: Commands that enter a configuration context.
MODE_KEYWORDS = (
    "address-family", "class-map", "daemon", "event-handler", "interface",
    "maintenance", "management", "mlag", "monitor", "patch", "peer-filter",
    "policy-map", "queue-monitor", "role", "route-map", "router", "tap", "vrf",
    "vlan",
)

#: Context commands that are followed by an operator-chosen name.
NAMED_MODES = (
    "class-map", "event-handler", "peer-filter", "policy-map", "route-map",
    "role",
)

#: Top-level commands that stay on one line.
COMMANDS = (
    "aaa", "agent", "aqm", "arp", "banner", "bash", "boot", "clock", "comment",
    "configure", "copy", "dir", "dns", "domain-name", "dot1x", "enable", "end",
    "errdisable", "event-monitor", "exit", "hardware", "ip", "ipv6", "lacp",
    "ldap", "lldp", "load-interval", "logging", "mac", "netconf", "ntp",
    "platform", "poe", "qos", "radius-server", "redundancy", "reload",
    "schedule", "service", "sflow", "show", "snmp-server", "spanning-tree",
    "ssl", "switchport", "system", "tacacs-server", "terminal", "trace",
    "transceiver", "username", "virtual-router", "vmtracer", "write",
)

#: EOS vocabulary on top of the shared networking words in ``_common``.
OPTIONS = (
    "accounting", "api", "authorization", "bgp-ls", "bpdufilter",
    "console", "counters", "database", "dcbx", "default-mode", "delay",
    "dhcpv6", "directed-broadcast", "dst-ip", "dst-mac", "ecmp",
    "error-correction", "failover", "fields", "flow-spec", "garp", "http",
    "http-commands", "https", "igmpv3", "l2-protocol", "lag", "lanz",
    "learned", "listen", "mlag-peer", "model", "mst", "mstp", "multi-agent",
    "no-autostate", "number", "protocols", "ptp", "qsfp",
    "redistribute-internal", "reload-delay", "rfc5549", "rip",
    "sparse-mode", "src-ip", "src-mac", "ssh", "storm-control", "tcam",
    "tracking", "trap",
    "trigger", "ucmp", "udp-port", "unix-socket", "update", "virtual",
    "vxlan-source-interface", "watchdog", "xmpp",
)


class AristaEOSLexer(SwitchCLILexer):
    """Lexer for Arista EOS configuration and CLI snippets."""

    name = "Arista EOS"
    url = "https://www.arista.com/en/products/eos"
    aliases = ["eos", "arista", "arista-eos", "aristaeos"]
    filenames = ["*.eos"]
    mimetypes = ["text/x-arista-eos"]

    tokens = {
        "root": [
            (r"[ \t]+", Whitespace),
            (r"\n", Whitespace),
            include("comments"),
            include("prompt"),
            keyword_rule(NEGATIONS, Keyword.Reserved, state=None),
            interface_header(INTERFACES),
            named_object(("hostname",)),
            named_object(NAMED_MODES, keyword_token=Keyword.Namespace),
            keyword_rule(MODE_KEYWORDS, Keyword.Namespace),
            keyword_rule(COMMANDS, Keyword),
            default("line"),
        ],
        "line": [
            include("prelude"),
            interface_reference(INTERFACES),
            (interface_re(INTERFACES), Name.Function),
            option_rule(OPTIONS),
            inherit,
        ],
    }

    def analyse_text(text):
        """Recognize the header EOS writes above ``show running-config``."""
        score = 0.0
        if re.search(r"^! device: .*EOS-", text, re.M):
            score += 0.6
        for pattern, weight in (
            (r"^\s*management api http-commands", 0.2),
            (r"^\s*service routing protocols model", 0.2),
            (r"^\s*transceiver qsfp default-mode", 0.2),
            (r"^\s*interface (?:Ethernet|Vxlan|Port-Channel)\d", 0.1),
        ):
            if re.search(pattern, text, re.M):
                score += weight
        return min(score, 1.0)
