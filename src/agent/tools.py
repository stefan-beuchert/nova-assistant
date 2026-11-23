"""Built-in tools Nova may call during the agent loop.

This module is where the ADR-0009 data-class allowlist is expressed in code:
**only the tools listed in `BUILTIN_TOOLS` are ever mounted.** No tool reaching
a denied data class (Vitae medical records, photos) exists in this process, so
the boundary holds structurally — not because the model declines to ask.

For the proof of concept the only tool is `get_current_time`: read-only, no data
source, no side effects. Its sole purpose is to exercise the tool-use loop end to
end (CLAUDE.md §2). Phase 3 adds Constellation's read-only MCP tools through this
same allowlist; until then the loop runs on safe built-ins only.

Adding any tool here that reaches a data source — or that writes or sends
anything — is a §1 decision in CLAUDE.md: stop and get explicit confirmation.
"""

from datetime import datetime, timezone


def _get_current_time(_args: dict) -> str:
    return datetime.now(timezone.utc).isoformat()


# Each entry is an Anthropic tool definition plus a private `_handler`.
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


def tool_definitions() -> list[dict]:
    """The tool list to send to the API (private `_handler` keys stripped)."""
    return [
        {k: v for k, v in tool.items() if not k.startswith("_")}
        for tool in BUILTIN_TOOLS
    ]


def execute_tool(name: str, args: dict | None) -> str:
    """Run an allowlisted tool by name. Unknown names are refused, not guessed."""
    for tool in BUILTIN_TOOLS:
        if tool["name"] == name:
            try:
                return tool["_handler"](args or {})
            except Exception as exc:  # surface as a tool error, don't crash the loop
                return f"error: {exc}"
    return f"error: unknown tool {name!r}"
