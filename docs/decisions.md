# Design Decisions

Non-obvious, **Nova-local** design decisions — what was decided, why, and what
alternatives were considered. One section per decision.

The data boundary and safety posture themselves are **not** recorded here: they affect
multiple repositories and are owned by `atlas/docs/adr/0009-nova-personal-assistant-data-boundary.md`.
This file records only choices local to building Nova. Escalate anything cross-repo to
an ADR in the root `atlas` repo (see that repo's `CLAUDE.md`, Decision Rules).

These were agreed during initial scoping (2026-11-23), before implementation.

---

## D1 — Python

**Decision.** Nova is written in Python.

**Why.** Consistency with the rest of Atlas (Constellation, Clio, Vitae are all
Python), so one operator and the per-repo agents stay fluent across the ecosystem and
reuse the same deploy/test idioms. Nova is only an MCP *client* plus a Claude agent
loop plus a small web chat — all first-class in Python (Anthropic SDK, official MCP
SDK), so nothing is lost versus Node.

**Alternatives considered.** TypeScript/Node — the MCP SDK's original reference
ecosystem and a slightly more natural streaming-chat story. Rejected because the
maturity gap is small for a client, runtime is container-isolated anyway, and
cross-Atlas consistency won on a near-coin-flip.

---

## D2 — Nova is an MCP client only; each source owns its MCP server

**Decision.** Source applications expose their own read-only MCP servers; Nova
*consumes* them. For the PoC the single source is **Constellation**, which owns and
builds a read-only MCP server wrapping the data it already publishes
(`GET /api/contacts` + its per-contact read surface). Nova never wraps another app's
data shape itself.

**Why.** This is the ADR-0009-literal path and keeps Nova thin and swappable — the
durable value stays in each app's data and own UI, and Nova stays a tolerant,
non-authoritative consumer (the ADR-0006 cross-app pattern, as MCP). Nova owning a
Constellation wrapper would pull another app's data model into this repo.

**Consequence / dependency.** Phase 3 depended on Constellation shipping that server
(contract: transport, URL, tool surface) — **resolved 2026-11-23**: Constellation now
runs a `constellation-mcp` service on the `atlas` network, streamable-HTTP on :8000,
with `list_contacts` / `get_contact`. Nova consumes it as an MCP client (see D6).

**Alternatives considered.** (a) Nova hosts a thin MCP layer over Constellation's REST
— faster, no Constellation change, but deviates from "source app exposes MCP" and
couples Nova to Constellation's shape. (b) Nova calls Constellation's REST directly
with no MCP — simplest, but drops the interface ADR-0009 deliberately chose. Both
rejected in favour of the literal pattern.

---

## D3 — The allowlist is mounted-tool configuration, not prompt text

**Decision.** Which MCP servers/tools Nova mounts is decided in code/config at startup.
Denied data classes (Vitae, photos) are simply never configured, so no tool reaching
them exists in the running process. No system-prompt instruction, model output, or user
input can change what Nova can reach.

**Why.** ADR-0009 requires the boundary to be structural, not a promise the model keeps.
"Permanently denied" means the tool is absent, not refused.

**Alternatives considered.** Instructing the model not to touch certain data via the
system prompt — rejected outright; that is exactly the control ADR-0009 forbids.

---

## D4 — Stateless proof of concept (no persistence)

**Decision.** The PoC persists nothing. Conversation state lives in-process per session;
there is no database and no infra provisioning request.

**Why.** Keeps the PoC lean and swappable, avoids a provisioning dependency, and matches
"build the smallest thing that proves the concept". Nova is the source of truth for no
data regardless.

**Alternatives considered.** Nova's own Postgres database for chat history (it owns the
conversation domain) — deferred to `docs/PROJECT.md` §7, to be added only if history
proves useful. SQLite-in-a-volume as a middle ground — also deferred; unnecessary for
the PoC.

---

## D5 — Server-rendered web chat, no build step

**Decision.** The chat UI is server-rendered (a light Python web framework + templates)
with minimal page-local JavaScript for streaming, no SPA framework and no build step.
It is gated by Authentik `forward_auth` at Caddy and reachable only on the tailnet;
Nova implements no auth of its own.

**Why.** Matches the no-build-step convention Constellation and Clio established, keeps
the footprint small on the Pi, and lets the existing platform boundary do the auth.

**Alternatives considered.** A JS SPA / separate frontend build — rejected as
disproportionate for a single-user PoC and inconsistent with the other apps.

---

## D6 — MCP consumed as a client via a thin sync bridge (added 2026-11-23)

**Decision.** Nova reaches Constellation's MCP server (D2) with the official `mcp` 2.x
high-level `Client` over streamable HTTP, wrapped in a small **synchronous** bridge
(`src/agent/mcp_client.py`): each `list_tools` / `call_tool` runs a short `asyncio`
loop and opens a **fresh connection per call**. Discovered tools are namespaced
`<source>__<tool>` and registered in the `ToolRegistry` alongside the built-ins;
mounting is **best-effort** — an unreachable source logs a warning and contributes no
tools, and Nova keeps working.

**Why.** Nova's web layer is synchronous (D5); a per-call loop keeps the whole codebase
sync without a persistent async session to manage, and per-call connects are negligible
for a single user. Namespacing avoids tool-name collisions across future sources and
shows provenance. Best-effort mounting matches the tolerant, non-authoritative cross-app
posture (ADR-0006/0009) — a source being down must never take Nova down.

**Why not the API-native MCP connector.** Anthropic's `mcp_servers` request parameter
makes the *model API* connect to the MCP server directly. Constellation's server is on
the private `atlas` tailnet with no public exposure, so Anthropic's cloud can't reach
it. Nova must be the client and relay the tools itself — which also keeps the allowlist
(D3) in Nova's own code, not delegated to the API.

**Alternatives considered.** A persistent async MCP session shared across requests —
rejected for the PoC: more moving parts (lifecycle, reconnect) for no meaningful gain at
single-user volume; revisit if latency matters.
