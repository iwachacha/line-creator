"""Compatibility package for repo-root execution.

The installable package lives under scripts/line_factory. Extending __path__ keeps
`python -m line_factory.cli` and direct imports such as `line_factory.specs`
working from a source checkout.
"""

from pathlib import Path

_IMPL = Path(__file__).resolve().parents[1] / "scripts" / "line_factory"
if _IMPL.exists():
    __path__.append(str(_IMPL))

from scripts.line_factory import __version__

__all__ = ["__version__"]
