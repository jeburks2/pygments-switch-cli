"""Lexer for the Dell SmartFabric OS10 command line interface."""

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

__all__ = ["DellOS10Lexer"]

#: Interface types.  OS10 writes ``ethernet1/1/1`` in its running
#: configuration but accepts ``ethernet 1/1/1`` interactively; the
#: ``interface`` context rule below handles the spaced form.  ``po`` is the
#: abbreviation the CLI expands to ``port-channel``, and the form runbooks are
#: written in: ``interface range Po 1-19,31-32``.
INTERFACES = (
    "ethernet", "mgmt", "po", "port-channel", "vlan", "loopback",
    "virtual-network", "nve", "tunnel", "vlt-port-channel", "breakout",
)

#: Commands that enter a configuration context.
MODE_KEYWORDS = (
    "address-family", "class-map", "evpn", "interface", "nve", "policy-map",
    "qos-map",
    "route-map", "router", "support-assist", "trust-map", "virtual-network",
    "vlt-domain", "vrf", "vlan",
)

#: Context commands that are followed by an operator-chosen name.
NAMED_MODES = ("class-map", "policy-map", "qos-map", "route-map", "trust-map")

#: Top-level commands that stay on one line.
COMMANDS = (
    "aaa", "banner", "boot", "clock", "commit", "copy", "dcbx", "do", "dot1x",
    "end", "eula-consent", "exit", "feature", "hardware", "hostname", "image",
    "ip", "ipv6", "iscsi", "lacp", "license", "lldp", "logging", "mac",
    "management", "monitor", "ntp", "radius-server", "reload", "service",
    "show", "snmp-server", "spanning-tree", "ssh-server", "system",
    "system-user", "tacacs-server", "telnet-server", "terminal", "track",
    "username", "write",
)

#: OS10 vocabulary on top of the shared networking words in ``_common``.
OPTIONS = (
    "backup-destination", "discovery-interface", "ebgp",
    "evi", "flow-based", "hash-algorithm", "linuxadmin", "map",
    "member-interface", "mst", "mtu-name", "peer-routing", "policy-based",
    "rapid-pvst", "role", "sflow", "sha2-256-password", "tagged",
    "untagged", "virtual-network", "virtual-router", "vlan-tunnel",
    "vlt-domain", "vlt-mac", "vlt-port-channel", "vn-node-id", "vrrp-group",
    "vxlan-vni",
)


class DellOS10Lexer(SwitchCLILexer):
    """Lexer for Dell SmartFabric OS10 configuration and CLI snippets."""

    name = "Dell OS10"
    url = "https://www.dell.com/support/kbdoc/en-us/000127641/dell-emc-networking-os10-info-hub"
    aliases = ["os10", "dell-os10", "dellos10", "smartfabric"]
    filenames = ["*.os10"]
    mimetypes = ["text/x-dell-os10"]

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
        """VLT and virtual-network are OS10's signature features."""
        score = 0.0
        for pattern, weight in (
            (r"^\s*vlt-domain \d", 0.4),
            (r"^\s*interface breakout \S", 0.3),
            (r"^\s*virtual-network \d", 0.2),
            (r"^\s*system-user linuxadmin", 0.2),
            (r"^\s*interface ethernet1/1/\d", 0.2),
        ):
            if re.search(pattern, text, re.M):
                score += weight
        return min(score, 1.0)
