"""Lexer for the SONiC command line interface."""

from __future__ import annotations

import re

from pygments.lexer import default, include, inherit
from pygments.token import Keyword, Name, Whitespace

from ._common import (
    WORD_END,
    WORD_START,
    SwitchCLILexer,
    interface_re,
    keyword_rule,
    option_rule,
)

__all__ = ["SONiCLexer"]

#: SONiC port names.  ``Ethernet-BP``/``-IB``/``-Rec`` are the backplane,
#: inband and recirculation ports on chassis and multi-ASIC platforms.
INTERFACES = (
    "ethernet-bp", "ethernet-ib", "ethernet-rec", "ethernet", "portchannel",
    "vlan", "loopback", "eth", "bond",
)

#: The utilities a SONiC snippet starts with.
UTILITIES = (
    "config", "show", "sonic-clear", "sonic-cfggen", "sonic-installer",
    "sonic-db-cli", "sonic-package-manager", "redis-cli", "vtysh",
    "systemctl", "docker",
)

#: Subcommands that remove or stop something.
DESTRUCTIVE_VERBS = ("del", "delete", "remove", "disable", "shutdown", "stop",
                     "clear", "unbind")

#: Subcommands that create, change or start something.
VERBS = ("add", "set", "enable", "startup", "start", "restart", "reload",
         "save", "update", "bind", "load_minigraph", "load_mgmt_config")

#: SONiC vocabulary on top of the shared networking words in ``_common``.
OPTIONS = (
    "acl", "asic", "breakout", "brief", "buffer", "counterpoll", "counters",
    "dhcp_relay", "drop_counters", "ecn", "feature", "fec", "flow_counters",
    "kdump", "kube", "mirror_session", "mmu", "muxcable",
    "namespace", "nat", "pfc", "platform", "portchannel", "priority-group",
    "qos", "queue", "reboot-cause", "runningconfiguration", "services",
    "sflow", "snmp", "startupconfiguration", "status", "subinterface",
    "summary", "suppress-fib-pending", "synchronous_mode", "syslog",
    "tacacs", "techsupport", "transceiver", "uptime", "warm_restart",
    "watermark", "ztp",
)


class SONiCLexer(SwitchCLILexer):
    """Lexer for SONiC ``config``/``show`` CLI snippets.

    SONiC's CLI is a set of Linux commands rather than a configuration
    grammar, so lines are highlighted verb-first and command line flags such
    as ``-y`` are picked out as ``Name.Attribute``.
    """

    name = "SONiC"
    url = "https://github.com/sonic-net/sonic-utilities/blob/master/doc/Command-Reference.md"
    aliases = ["sonic", "sonic-cli"]
    filenames = ["*.sonic"]
    mimetypes = ["text/x-sonic"]

    tokens = {
        "root": [
            (r"[ \t]+", Whitespace),
            (r"\n", Whitespace),
            include("comments"),
            include("prompt"),
            (rf"{WORD_START}sudo{WORD_END}", Name.Builtin),
            keyword_rule(UTILITIES, Keyword.Namespace),
            default("line"),
        ],
        "line": [
            include("prelude"),
            (interface_re(INTERFACES), Name.Function),
            keyword_rule(DESTRUCTIVE_VERBS, Keyword.Reserved, state=None),
            keyword_rule(VERBS, Keyword, state=None),
            option_rule(OPTIONS),
            inherit,
        ],
    }

    def analyse_text(text):
        """``config``/``show`` invocations plus SONiC-only utility names."""
        score = 0.0
        if re.search(r"^\s*(?:sudo )?config (?:interface|vlan|portchannel|"
                     r"save|reload|bgp|feature)\b", text, re.M):
            score += 0.5
        for pattern, weight in (
            (r"\bsonic-(?:cfggen|installer|clear|db-cli)\b", 0.3),
            (r"^\s*show (?:interfaces status|runningconfiguration|techsupport)\b", 0.2),
            (r"\bEthernet\d+\b.*\bPortChannel\d+\b", 0.1),
        ):
            if re.search(pattern, text, re.M):
                score += weight
        return min(score, 1.0)
