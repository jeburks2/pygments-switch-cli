"""Lexers for the two Cumulus Linux command line interfaces.

Cumulus Linux ships two generations of CLI: NCLU (``net add ...``), used
through Cumulus Linux 4.x, and NVUE (``nv set ...``), introduced in 4.4 and
the only CLI in Cumulus Linux 5.x.  Both are verb-first rather than
context-based, so their ``root`` states key off the leading command word
instead of a configuration mode.
"""

from __future__ import annotations

import re

from pygments.lexer import bygroups, default, include, inherit, words
from pygments.token import Keyword, Name, Whitespace

from ._common import (
    WORD_END,
    WORD_START,
    SwitchCLILexer,
    interface_re,
    option_rule,
)

__all__ = ["NCLU_OPTIONS", "NVUE_OPTIONS", "CumulusNCLULexer", "NVUELexer"]

#: Linux interface names as Cumulus presents them: front panel ports are
#: ``swp1``, breakout subports are ``swp1s0``, and ranges are accepted
#: wherever a single port is.
INTERFACES = ("swp", "bond", "eth", "vlan", "br", "vni", "vx", "vrf")

#: Interface names that carry no number, optionally with a VLAN subinterface.
BARE_INTERFACES = ("lo", "peerlink")

#: Objects and attributes shared by both CLIs.
SHARED_OPTIONS = (
    "acl", "address-virtual", "arp-nd-suppress", "backup-ip", "bond",
    "br_default", "bridge-learning", "clag", "clag-id", "dhcp-relay",
    "dhcp-server", "flooding", "head-end-replication", "l2protocol",
    "nameserver", "ntp", "ports", "ptp", "snmp-server", "stp", "sys-mac",
    "time", "timezone", "zone",
)

#: NCLU vocabulary.  ``net`` exposes a few objects NVUE renamed.
NCLU_OPTIONS = SHARED_OPTIONS + (
    "lnv", "mstpctl", "vlan-aware", "vrr",
)

#: NVUE object paths.
NVUE_OPTIONS = SHARED_OPTIONS + (
    "breakout", "ecmp", "fec", "l2vpn-evpn", "linklocal", "mlag",
    "multipaths", "nve", "path-selection", "peer-ip", "platform", "qos",
    "rule", "sid", "single-vxlan-device", "svi", "system", "untagged",
    "vlan-id",
)


class CumulusNCLULexer(SwitchCLILexer):
    """Lexer for the Cumulus Linux NCLU (``net``) CLI."""

    name = "Cumulus NCLU"
    url = "https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-43/System-Configuration/Network-Command-Line-Utility-NCLU/"
    aliases = ["nclu", "cumulus", "cumulus-nclu", "net-commands"]
    filenames = ["*.nclu"]
    mimetypes = ["text/x-cumulus-nclu"]

    #: ``net`` verbs that remove configuration or discard staged changes.
    DESTRUCTIVE_VERBS = ("del", "clear", "abort")

    #: Every other ``net`` verb.
    VERBS = (
        "add", "commit", "example", "help", "pending", "restart", "rollback",
        "show", "status",
    )

    tokens = {
        "root": [
            (r"[ \t]+", Whitespace),
            (r"\n", Whitespace),
            include("comments"),
            include("prompt"),
            (rf"{WORD_START}sudo{WORD_END}", Name.Builtin),
            (words(DESTRUCTIVE_VERBS, prefix=WORD_START + r"(net)([ \t]+)(",
                   suffix=r")" + WORD_END),
             bygroups(Keyword.Namespace, Whitespace, Keyword.Reserved), "line"),
            (words(VERBS, prefix=WORD_START + r"(net)([ \t]+)(",
                   suffix=r")" + WORD_END),
             bygroups(Keyword.Namespace, Whitespace, Keyword), "line"),
            (rf"{WORD_START}net{WORD_END}", Keyword.Namespace, "line"),
            default("line"),
        ],
        "line": [
            include("prelude"),
            (interface_re(INTERFACES, bare=BARE_INTERFACES), Name.Function),
            option_rule(NCLU_OPTIONS),
            inherit,
        ],
    }

    def analyse_text(text):
        """``net add``/``net commit`` lines are unambiguous NCLU."""
        score = 0.0
        if re.search(r"^\s*net (?:add|del) \S", text, re.M):
            score += 0.5
        if re.search(r"^\s*net (?:commit|pending|rollback)\b", text, re.M):
            score += 0.3
        return min(score, 1.0)


class NVUELexer(SwitchCLILexer):
    """Lexer for the NVIDIA NVUE (``nv``) CLI used by Cumulus Linux 5."""

    name = "NVUE"
    url = "https://docs.nvidia.com/networking-ethernet-software/cumulus-linux/System-Configuration/NVUE-CLI/"
    aliases = ["nvue", "nv", "cumulus-nvue"]
    filenames = ["*.nvue"]
    mimetypes = ["text/x-nvue"]

    #: ``nv config`` subcommands.
    CONFIG_VERBS = (
        "apply", "detach", "diff", "find", "history", "patch", "replace",
        "save", "show",
    )

    #: Top-level ``nv`` verbs other than the destructive ``unset``.
    VERBS = ("set", "show", "action", "docs", "help", "config")

    tokens = {
        "root": [
            (r"[ \t]+", Whitespace),
            (r"\n", Whitespace),
            include("comments"),
            include("prompt"),
            (rf"{WORD_START}sudo{WORD_END}", Name.Builtin),
            (words(CONFIG_VERBS, prefix=WORD_START + r"(nv)([ \t]+)(config)([ \t]+)(",
                   suffix=r")" + WORD_END),
             bygroups(Keyword.Namespace, Whitespace, Keyword, Whitespace,
                      Keyword), "line"),
            (rf"{WORD_START}(nv)([ \t]+)(unset){WORD_END}",
             bygroups(Keyword.Namespace, Whitespace, Keyword.Reserved), "line"),
            (words(VERBS, prefix=WORD_START + r"(nv)([ \t]+)(",
                   suffix=r")" + WORD_END),
             bygroups(Keyword.Namespace, Whitespace, Keyword), "line"),
            (rf"{WORD_START}nv{WORD_END}", Keyword.Namespace, "line"),
            default("line"),
        ],
        "line": [
            include("prelude"),
            (interface_re(INTERFACES, bare=BARE_INTERFACES), Name.Function),
            option_rule(NVUE_OPTIONS),
            inherit,
        ],
    }

    def analyse_text(text):
        """``nv set``/``nv config apply`` lines are unambiguous NVUE."""
        score = 0.0
        if re.search(r"^\s*nv (?:set|unset) \S", text, re.M):
            score += 0.5
        if re.search(r"^\s*nv config (?:apply|save|diff)\b", text, re.M):
            score += 0.3
        return min(score, 1.0)
