"""The tools Nova may call, and the allowlist that decides which are mounted.

The `ToolRegistry` is where the ADR-0009 data-class allowlist lives in code: the
agent loop can only ever call (a) the safe built-ins defined here, and (b) tools
from MCP sources that were *explicitly configured* in `build_allowlisted_sources`.
A source's tools exist in the running process only if it is on that list — so a
denied data class (Vitae medical records, photos) is unreachable by construction,
not because the model declines to ask.

Adding a built-in that reaches a data source, a write/outbound tool, or a new MCP
source is a CLAUDE.md §1/§2 decision: stop and get explicit confirmation.
"""

import logging
from datetime import datetime, timezone

from .mcp_client import McpSource

logger = logging.getLogger(__name__)


# --- Safe built-in tools (no data source, no side effects) -------------------

def _get_current_time(_args: dict) -> str:
    return datetime.now(timezone.utc).isoformat()


BUILTIN_TOOLS = [
    {
        "name": "get_current_time",
        "description": (
            "Return the current UTC date and time in ISO 8601 format. "
            "Use this when the user asks what the current time or date is."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "_handler": _get_current_time,
    },
]


# --- The allowlist -----------------------------------------------------------

def build_allowlisted_sources(config) -> list[McpSource]:
    """The ADR-0009 data-class allowlist: only explicitly configured sources are
    ever mounted. Constellation (contacts) and Nexus (calendar) are the allowed
    read-only sources. Vitae medical records and photos are intentionally absent
    and must never be added here.
    """
    sources: list[McpSource] = []
    if getattr(config, "CONSTELLATION_MCP_URL", ""):
        sources.append(McpSource("constellation", config.CONSTELLATION_MCP_URL))
    # Nexus calendar (2nd source, added 2026-11-25 with explicit user confirmation).
    # Tools are namespaced calendar__* (e.g. calendar__list_events).
    if getattr(config, "NEXUS_MCP_URL", ""):
        sources.append(McpSource("calendar", config.NEXUS_MCP_URL))
    return sources


def build_registry(config) -> "ToolRegistry":
    return ToolRegistry(build_allowlisted_sources(config))


# --- The registry ------------------------------------------------------------

class ToolRegistry:
    """The concrete set of tools mounted for the agent loop: built-ins plus the
    tools discovered from each allowlisted MCP source. Discovery is best-effort —
    an unreachable source is logged and simply contributes no tools."""

    def __init__(self, mcp_sources: list[McpSource] | None = None):
        self._builtin = {t["name"]: t for t in BUILTIN_TOOLS}
        self._mcp_routes: dict[str, tuple[McpSource, str]] = {}
        self._mcp_defs: list[dict] = []
        self._mounted_sources: list[str] = []

        for source in mcp_sources or []:
            try:
                defs = source.list_tools()
            except Exception as exc:
                logger.warning(
                    "MCP source %r (%s) unavailable; mounting no tools from it: %s",
                    source.name, source.url, exc,
                )
                continue
            self._mounted_sources.append(source.name)
            for d in defs:
                self._mcp_routes[d["name"]] = (source, d["_tool"])
                self._mcp_defs.append(
                    {
                        "name": d["name"],
                        "description": d["description"],
                        "input_schema": d["input_schema"],
                    }
                )
            logger.info("Mounted MCP source %r with %d tool(s)", source.name, len(defs))

    @property
    def mounted_sources(self) -> list[str]:
        return list(self._mounted_sources)

    def definitions(self) -> list[dict]:
        """Anthropic tool definitions for every mounted tool (built-ins + MCP)."""
        builtin_defs = [
            {k: v for k, v in t.items() if not k.startswith("_")}
            for t in BUILTIN_TOOLS
        ]
        return builtin_defs + self._mcp_defs

    def execute(self, name: str, args: dict | None) -> str:
        """Run a mounted tool by name; unknown names are refused, not guessed."""
        if name in self._builtin:
            try:
                return self._builtin[name]["_handler"](args or {})
            except Exception as exc:
                return f"error: {exc}"
        route = self._mcp_routes.get(name)
        if route is not None:
            source, tool = route
            try:
                return source.call_tool(tool, args or {})
            except Exception as exc:
                logger.warning("MCP tool %r failed: %s", name, exc)
                return f"error: {exc}"
        return f"error: unknown tool {name!r}"
