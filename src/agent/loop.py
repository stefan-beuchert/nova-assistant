"""The Claude agent loop: a streaming, tool-use conversation turn.

`run_turn` drives one user turn to completion — it streams assistant text as it
is generated, runs any allowlisted tool the model calls (see `tools.py`), feeds
the results back, and repeats until the model stops asking for tools. It yields
small event dicts the web layer serialises to the browser; it never touches the
network or the UI itself, so it is straightforward to exercise with a fake client.

Nova is read-only and non-authoritative (ADR-0009): the only tools it can call
are the structural allowlist in `tools.py`.
"""

from collections.abc import Iterator

from .tools import execute_tool, tool_definitions

SYSTEM_PROMPT = """You are Nova, the personal assistant for the Atlas homelab — \
a private, self-hosted platform of the user's own applications.

Your job is to answer the user's questions in natural language, grounding your \
answers in the user's own data through the tools you are given.

Rules you must follow:
- You are read-only and non-authoritative: you retrieve and suggest, you never \
act unattended. You have no tool that writes, sends, or changes anything.
- Only use the tools you are actually given. If answering would require data or \
an action you have no tool for, say so plainly instead of guessing or inventing \
an answer.
- Be concise and direct. Lead with the answer.
- You are an enhancement, not a system of record. Never imply the user depends \
on you."""


def build_client(api_key: str):
    """Construct the Anthropic client. Imported lazily so the web layer can boot
    (and `/health` can respond) even when the SDK isn't installed."""
    import anthropic

    return anthropic.Anthropic(api_key=api_key)


def run_turn(
    client,
    model: str,
    max_tokens: int,
    messages: list,
) -> Iterator[dict]:
    """Run the agent loop for one user turn.

    `messages` must already end with the new user message; it is mutated in place
    to append the assistant (and any tool-result) turns, so the caller's history
    stays correct for the next turn. Yields event dicts:
      {"type": "status", "value": "thinking" | "tool:<name>"}
      {"type": "token",  "text": "<delta>"}
      {"type": "done"}
    """
    tools = tool_definitions()

    while True:
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=tools,
            thinking={"type": "adaptive"},
        ) as stream:
            for event in stream:
                if event.type == "content_block_start" and (
                    getattr(event.content_block, "type", None) == "thinking"
                ):
                    yield {"type": "status", "value": "thinking"}
                elif event.type == "content_block_delta" and (
                    getattr(event.delta, "type", None) == "text_delta"
                ):
                    yield {"type": "token", "text": event.delta.text}
            final = stream.get_final_message()

        # Echo the full assistant turn back into history unchanged — thinking and
        # tool_use blocks included — so the next request is well-formed.
        messages.append({"role": "assistant", "content": final.content})

        if final.stop_reason != "tool_use":
            break

        tool_results = []
        for block in final.content:
            if getattr(block, "type", None) == "tool_use":
                yield {"type": "status", "value": f"tool:{block.name}"}
                output = execute_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    yield {"type": "done"}
