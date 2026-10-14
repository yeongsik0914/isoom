"""MoonlightCare Backend Application Package.

Zero-LLM deterministic foundation and AI multi-agent orchestrator
for pediatric emergency and night clinic matching.
"""

from __future__ import annotations

import sys

# Windows CP949 console encoding fix
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

__version__ = "0.1.0"

