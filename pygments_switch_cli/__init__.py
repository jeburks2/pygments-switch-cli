"""Pygments lexers for network switch command line interfaces.

Installing this package registers lexers for Arista EOS, Cisco NX-OS, Dell
SmartFabric OS10, Cumulus Linux (both NCLU and NVUE), SONiC and FRRouting
through the ``pygments.lexers`` entry point group, which makes them available
to anything that renders code with Pygments -- MkDocs, Sphinx, ``pygmentize``
or a direct API call::

    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name

    highlight(config, get_lexer_by_name("eos"), HtmlFormatter())

See ``README.md`` for the alias table and the token scheme the lexers share.
"""

from __future__ import annotations

from .__about__ import __version__
from ._common import SwitchCLILexer
from .arista import AristaEOSLexer
from .cisco import CiscoNXOSLexer
from .cumulus import CumulusNCLULexer, NVUELexer
from .dell import DellOS10Lexer
from .frr import FRRLexer
from .sonic import SONiCLexer

#: Every lexer this distribution registers, in documentation order.  Tests
#: check this against the entry points declared in ``pyproject.toml``.
ALL_LEXERS = (
    AristaEOSLexer,
    CiscoNXOSLexer,
    DellOS10Lexer,
    CumulusNCLULexer,
    NVUELexer,
    SONiCLexer,
    FRRLexer,
)

__all__ = [
    "ALL_LEXERS",
    "AristaEOSLexer",
    "CiscoNXOSLexer",
    "CumulusNCLULexer",
    "DellOS10Lexer",
    "FRRLexer",
    "NVUELexer",
    "SONiCLexer",
    "SwitchCLILexer",
    "__version__",
]
