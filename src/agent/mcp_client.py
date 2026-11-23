"""MCP client bridge — lets Nova consume a source application's read-only MCP server.

Nova is the MCP *client*; each source app hosts its own server (ADR-0009, decisions
D2). The set of `McpSource` instances Nova mounts is the data-class allowlist
expressed in config — see `src/agent/tools.build_allowlisted_sources`. Vitae and
photos have no source here and must never get one.

The MCP SDK client is async and Nova's web layer is sync, so each call runs a short
`asyncio` loop and opens a fresh streamable-HTTP connection. That's fine for a
single-user assistant and keeps the rest of the code synchronous. Connections are
best-effort: an unreachable source mounts no tools and Nova keeps working, matching
the tolerant, non-authoritative cross-app posture (ADR-0006/0009).
"""

import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class McpSource:
    """One allowlisted read-only MCP server (e.g. Constellation)."""

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def list_tools(self) -> list[dict]:
        """Discover the source's tools as Anthropic tool definitions.

        Tool names are namespaced `<source>__<tool>` so multiple sources can't
        collide and the model can see where a tool comes from. Each dict also
        carries a private `_tool` (the un-namespaced name) for routing calls back.
        """
        return _run(self._list_tools())

    def call_tool(self, tool_name: str, args: dict | None) -> str:
        """Call one tool on the source and return its result as text for a tool_result."""
        return _run(self._call_tool(tool_name, args))

    async def _list_tools(self) -> list[dict]:
        from mcp import Client

        async with Client(self.url) as client:
            result = await client.list_tools()
            tools = getattr(result, "tools", result)
            return [
                {
                    "name": f"{self.name}__{tool.name}",
                    "description": tool.description or "",
                    "input_schema": tool.input_schema
                    or {"type": "object", "properties": {}},
                    "_tool": tool.name,
                }
                for tool in tools
            ]

    async def _call_tool(self, tool_name: str, args: dict | None) -> str:
        from mcp import Client

        async with Client(self.url) as client:
            result = await client.call_tool(tool_name, args or {})
            return _result_text(result)


def _run(coro):
    return asyncio.run(coro)


def _result_text(result) -> str:
    """Flatten an MCP CallToolResult into text for an Anthropic tool_result block.

    Prefers the tool's structured output (JSON); falls back to joined text content.
    An MCP tool error is surfaced as an `error:` string so the model can react,
    rather than raising.
    """
    structured = getattr(result, "structured_content", None)
    if structured is not None:
        text = json.dumps(structured, default=str)
    else:
        parts = [getattr(b, "text", "") for b in (getattr(result, "content", None) or [])]
        text = "\n".join(p for p in parts if p) or "(no content)"
    if getattr(result, "is_error", False):
        return f"error: {text}"
    return text
