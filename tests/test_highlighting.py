"""Tests for the tokens the lexers actually assign.

The shared tests run against every lexer, so a new platform inherits them;
the per-platform tests pin down the syntax that platform does differently.
"""

from __future__ import annotations

import pytest
from pygments.token import (
    Comment,
    Generic,
    Keyword,
    Name,
    Number,
    String,
)

from conftest import significant, token_for
from pygments_switch_cli import (
    AristaEOSLexer,
    CiscoNXOSLexer,
    CumulusNCLULexer,
    DellOS10Lexer,
    FRRLexer,
    NVUELexer,
    SONiCLexer,
)

# --------------------------------------------------------------------------
# Behavior shared by every platform
# --------------------------------------------------------------------------


def test_description_tail_is_a_string(lexer):
    """Free text after ``description`` must not be lexed as keywords."""
    text = "description link to spine1 port 3\n"
    assert token_for(lexer, text, "description") is Name.Builtin
    assert token_for(lexer, text, "link to spine1 port 3") is String


def test_quoted_strings(lexer):
    """Quoted values keep their own token; a description tail is plain String.

    ``description`` deliberately swallows the rest of the line, so this uses a
    keyword that does not.
    """
    double = token_for(lexer, 'set community "65000:100"\n', '"65000:100"')
    single = token_for(lexer, "set community '65000:100'\n", "'65000:100'")
    assert double is String.Double
    assert single is String.Single


@pytest.mark.parametrize("address", ["10.0.0.1", "10.0.0.0/24", "2001:db8::1",
                                     "2001:db8::/32", "fe80::1"])
def test_addresses_are_numbers(lexer, address):
    assert token_for(lexer, f"ip address {address}\n", address) is Number


@pytest.mark.parametrize("mac", ["00:11:22:33:44:55", "0011.2233.4455"])
def test_mac_addresses_are_hex_numbers(lexer, mac):
    assert token_for(lexer, f"mac-address {mac}\n", mac) is Number.Hex


def test_vlan_ids_and_ranges_are_integers(lexer):
    text = "switchport trunk allowed vlan 100,200-300\n"
    assert token_for(lexer, text, "100,200-300") is Number.Integer


@pytest.mark.parametrize("comment", ["! a comment", "# a comment"])
def test_comments(lexer, comment):
    assert token_for(lexer, comment + "\n", comment) is Comment.Single


@pytest.mark.parametrize("prompt", ["leaf1#", "leaf1(config-if-Et1)#",
                                    "leaf1>", "admin@leaf1:~$"])
def test_prompts_in_pasted_sessions(lexer, prompt):
    assert token_for(lexer, f"{prompt} show version\n", prompt) is Generic.Prompt


@pytest.mark.parametrize("keyword", ["router-id", "route-map", "maximum-paths",
                                     "remote-as", "next-hop-self"])
def test_hyphenated_keywords_stay_whole(lexer, keyword):
    """``\\b`` matches inside a hyphenated word, which used to split these."""
    text = f"set {keyword} value\n"
    values = [value for _, value in significant(lexer, text)]
    assert keyword in values, f"{lexer.name} split {keyword}: {values}"


def test_hostname_takes_a_variable_name(lexer):
    assert token_for(lexer, "hostname leaf1\n", "leaf1") is Name.Variable


# --------------------------------------------------------------------------
# Arista EOS
# --------------------------------------------------------------------------


def test_eos_interface_context():
    lexer = AristaEOSLexer()
    text = "interface Ethernet3/1/1\n"
    assert token_for(lexer, text, "interface") is Keyword.Namespace
    assert token_for(lexer, text, "Ethernet3/1/1") is Name.Function


@pytest.mark.parametrize("name", ["Ethernet1", "Et3/1", "Po10", "Vlan4094",
                                  "Vxlan1", "Loopback0", "Management1/1",
                                  "Ethernet1.100", "Recirc-Channel501"])
def test_eos_interface_names(name):
    text = f"  no switchport\n  {name}\n"
    assert token_for(AristaEOSLexer(), text, name) is Name.Function


def test_eos_vlan_is_a_context_keyword_at_the_start_of_a_line():
    """The same word means different things in different positions."""
    lexer = AristaEOSLexer()
    assert token_for(lexer, "vlan 100\n", "vlan") is Keyword.Namespace
    assert token_for(lexer, "   switchport access vlan 100\n", "vlan") is Name.Builtin


def test_eos_negation():
    lexer = AristaEOSLexer()
    assert token_for(lexer, "   no shutdown\n", "no") is Keyword.Reserved
    assert token_for(lexer, "   default snmp-server\n", "default") is Keyword.Reserved


def test_eos_route_distinguisher():
    lexer = AristaEOSLexer()
    assert token_for(lexer, "      rd 10.0.0.1:10100\n", "10.0.0.1:10100") is Number


# --------------------------------------------------------------------------
# Cisco NX-OS
# --------------------------------------------------------------------------


def test_nxos_switchname_is_a_variable():
    assert token_for(CiscoNXOSLexer(), "switchname leaf1\n", "leaf1") is Name.Variable


def test_nxos_feature_lines():
    lexer = CiscoNXOSLexer()
    text = "feature vn-segment-vlan-based\n"
    assert token_for(lexer, text, "feature") is Keyword
    assert token_for(lexer, text, "vn-segment-vlan-based") is Name.Builtin


@pytest.mark.parametrize("name", ["Ethernet1/1", "Eth1/1", "mgmt0", "nve1",
                                  "port-channel10", "Vlan100", "loopback0"])
def test_nxos_interface_names(name):
    assert token_for(CiscoNXOSLexer(), f"interface {name}\n", name) is Name.Function


# --------------------------------------------------------------------------
# Dell OS10
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["ethernet1/1/1", "ethernet 1/1/1",
                                  "port-channel10", "vlan100", "mgmt1/1/1",
                                  "virtual-network100"])
def test_os10_accepts_both_interface_spellings(name):
    """OS10 writes ``ethernet1/1/1`` but accepts ``ethernet 1/1/1``."""
    assert token_for(DellOS10Lexer(), f"interface {name}\n", name) is Name.Function


def test_os10_vlt_domain_is_a_context():
    lexer = DellOS10Lexer()
    assert token_for(lexer, "vlt-domain 1\n", "vlt-domain") is Keyword.Namespace


def test_os10_interface_range():
    lexer = DellOS10Lexer()
    text = " discovery-interface ethernet1/1/29-1/1/30\n"
    assert token_for(lexer, text, "ethernet1/1/29-1/1/30") is Name.Function


# --------------------------------------------------------------------------
# Cumulus Linux
# --------------------------------------------------------------------------


def test_nclu_verbs():
    lexer = CumulusNCLULexer()
    assert token_for(lexer, "net add interface swp1\n", "net") is Keyword.Namespace
    assert token_for(lexer, "net add interface swp1\n", "add") is Keyword
    assert token_for(lexer, "net del bgp neighbor swp1\n", "del") is Keyword.Reserved
    assert token_for(lexer, "net commit\n", "commit") is Keyword


@pytest.mark.parametrize("name", ["swp1", "swp1s0", "swp1-48", "bond0",
                                  "vlan100", "lo", "peerlink.4094"])
def test_cumulus_interface_names(name):
    text = f"net add interface {name}\n"
    assert token_for(CumulusNCLULexer(), text, name) is Name.Function


def test_nvue_verbs():
    lexer = NVUELexer()
    assert token_for(lexer, "nv set interface swp1\n", "nv") is Keyword.Namespace
    assert token_for(lexer, "nv set interface swp1\n", "set") is Keyword
    unset = token_for(lexer, "nv unset interface swp1 ip address\n", "unset")
    assert unset is Keyword.Reserved


def test_nvue_config_subcommands():
    lexer = NVUELexer()
    text = "nv config apply\n"
    assert token_for(lexer, text, "config") is Keyword
    assert token_for(lexer, text, "apply") is Keyword


def test_nvue_on_off_values_are_constants():
    lexer = NVUELexer()
    assert token_for(lexer, "nv set evpn enable on\n", "on") is Keyword.Constant


# --------------------------------------------------------------------------
# SONiC
# --------------------------------------------------------------------------


def test_sonic_utility_and_verbs():
    lexer = SONiCLexer()
    text = "sudo config vlan add 100\n"
    assert token_for(lexer, text, "sudo") is Name.Builtin
    assert token_for(lexer, text, "config") is Keyword.Namespace
    assert token_for(lexer, text, "add") is Keyword
    assert token_for(lexer, "sudo config vlan del 100\n", "del") is Keyword.Reserved


@pytest.mark.parametrize("flag", ["-y", "--min-links", "-u"])
def test_sonic_command_line_flags(flag):
    text = f"sudo config portchannel add PortChannel001 {flag} 2\n"
    assert token_for(SONiCLexer(), text, flag) is Name.Attribute


@pytest.mark.parametrize("name", ["Ethernet0", "PortChannel001", "Vlan100",
                                  "Ethernet-BP0", "Loopback0"])
def test_sonic_port_names(name):
    text = f"sudo config interface startup {name}\n"
    assert token_for(SONiCLexer(), text, name) is Name.Function


# --------------------------------------------------------------------------
# FRRouting
# --------------------------------------------------------------------------


def test_frr_version_header():
    lexer = FRRLexer()
    assert token_for(lexer, "frr version 8.4.2\n", "frr") is Keyword
    assert token_for(lexer, "frr version 8.4.2\n", "8.4.2") is Number


def test_frr_router_id_is_one_token():
    lexer = FRRLexer()
    text = " bgp router-id 10.0.0.1\n"
    assert token_for(lexer, text, "router-id") is Name.Builtin
    assert token_for(lexer, text, "10.0.0.1") is Number


def test_frr_exit_commands():
    lexer = FRRLexer()
    assert token_for(lexer, " exit-address-family\n", "exit-address-family") is Keyword


def test_frr_bare_loopback():
    assert token_for(FRRLexer(), "interface lo\n", "lo") is Name.Function
