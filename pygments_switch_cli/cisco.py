"""Lexer for the Cisco NX-OS command line interface."""

from __future__ import annotations

import re

from pygments.lexer import default, include, inherit
from pygments.token import Keyword, Name, Whitespace

from ._common import (
    NEGATIONS,
    SwitchCLILexer,
    interface_header,
    interface_re,
    keyword_rule,
    named_object,
    option_rule,
)

__all__ = ["CiscoNXOSLexer"]

#: Interface types, including the short forms NX-OS accepts (``Eth1/1``,
#: ``Po10``) and the storage and virtual types on Nexus platforms.
INTERFACES = (
    "ethernet", "eth", "mgmt", "vlan", "port-channel", "po", "loopback", "lo",
    "nve", "tunnel", "vethernet", "veth", "bdi", "vfc", "fc",
    "san-port-channel", "overlay", "sup-eth",
)

#: Commands that enter a configuration context.
MODE_KEYWORDS = (
    "address-family", "class-map", "control-plane", "evpn", "fabric",
    "interface", "line", "monitor", "policy-map", "port-profile", "role",
    "route-map", "router", "table-map", "template", "vdc", "vlan", "vni",
    "vpc", "vrf",
)

#: Context commands that are followed by an operator-chosen name.
NAMED_MODES = (
    "class-map", "policy-map", "route-map", "table-map", "port-profile",
    "template", "vdc",
)

#: Top-level commands that stay on one line.
COMMANDS = (
    "aaa", "banner", "boot", "callhome", "cdp", "cfs", "cli", "clock",
    "configure", "copy", "crypto", "dcbx", "errdisable", "exit", "feature",
    "fex", "hostname", "icam", "install", "ip", "ipv6", "key", "license",
    "lldp", "logging", "mac", "ngoam", "no", "ntp", "nv", "nxapi", "poweroff",
    "radius-server", "rmon", "scheduler", "service", "show", "slot",
    "snmp-server", "spanning-tree", "ssh", "switchname", "switchto", "system",
    "tacacs-server", "telemetry", "terminal", "track", "udld", "username",
    "vrf", "vtp", "write",
)

#: NX-OS vocabulary on top of the shared networking words in ``_common``.
OPTIONS = (
    "anycast-gateway", "anycast-gateway-mac", "associate-vrf", "bash-shell",
    "channel-group", "context", "direct", "fabric-forwarding",
    "feature-set", "hsrp", "ingress-replication", "interface-vlan",
    "ip-forward", "isolate", "l2", "l3", "limit-resource", "mcast-group",
    "mst", "nv", "nxapi", "overlay", "peer-gateway", "peer-keepalive",
    "peer-switch", "peer-vtep", "ptp", "pvlan", "rise", "scp-server",
    "sftp-server", "spine-anycast-gateway", "suppress-arp",
    "system-priority", "tacacs+", "telnet", "vn-segment",
    "vn-segment-vlan-based", "vpc", "vpc+", "vtp",
)


class CiscoNXOSLexer(SwitchCLILexer):
    """Lexer for Cisco NX-OS configuration and CLI snippets."""

    name = "Cisco NX-OS"
    url = "https://www.cisco.com/c/en/us/products/ios-nx-os-software/nx-os/index.html"
    aliases = ["nxos", "nx-os", "cisco-nxos", "nexus"]
    filenames = ["*.nxos"]
    mimetypes = ["text/x-cisco-nxos"]

    tokens = {
        "root": [
            (r"[ \t]+", Whitespace),
            (r"\n", Whitespace),
            include("comments"),
            include("prompt"),
            keyword_rule(NEGATIONS, Keyword.Reserved, state=None),
            interface_header(INTERFACES),
            named_object(("hostname", "switchname")),
            named_object(NAMED_MODES, keyword_token=Keyword.Namespace),
            keyword_rule(MODE_KEYWORDS, Keyword.Namespace),
            keyword_rule(COMMANDS, Keyword),
            default("line"),
        ],
        "line": [
            include("prelude"),
            (interface_re(INTERFACES), Name.Function),
            option_rule(OPTIONS),
            inherit,
        ],
    }

    def analyse_text(text):
        """``feature`` lines and ``nv overlay`` are distinctly NX-OS."""
        score = 0.0
        if re.search(r"^\s*feature \w", text, re.M):
            score += 0.3
        for pattern, weight in (
            (r"^\s*switchname \S", 0.3),
            (r"^\s*nv overlay evpn", 0.3),
            (r"^\s*vpc domain \d", 0.2),
            (r"^\s*vdc \S+ id \d", 0.2),
            (r"^\s*interface (?:Ethernet\d+/|nve\d)", 0.1),
        ):
            if re.search(pattern, text, re.M):
                score += weight
        return min(score, 1.0)
