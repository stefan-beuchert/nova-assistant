# Nova — Project

What problem this repository solves, what's in and out of scope, and how it gets
built. The charter above this (why Nova is allowed to exist at all, and the data
boundary) is owned by `atlas/docs/adr/0009-nova-personal-assistant-data-boundary.md`
and `atlas/docs/services/NOVA-ASSISTANT.md` — read those first.

## 1. The problem

Atlas today is reached through per-application web UIs and SSH; the only conversational
channel is one-way ntfy push. There is no way to simply *ask* — "when did I last talk
to X", "whose birthday is coming up" — in natural language across your own data.

Nova is that channel: a chat interface that takes a request, plans steps, reads your
own data through read-only interfaces, and replies. It is an **enhancement layer**, not
a new system of record — every Atlas application must remain fully usable with Nova
switched off.

## 2. In scope (proof of concept)

- A small **web chat UI** at `nova.atlas`, server-rendered, behind Tailscale +
  Authentik — the same boundary every other internal UI uses.
- An **agent loop** driving Anthropic Claude via tool-use.
- **One** read-only data source: **Constellation**, consumed through its own read-only
  **MCP server**. Enough to prove the end-to-end shape: question → tool call → grounded
  answer about the user's own contacts.
- A **data-class allowlist** that decides, in code/config, which MCP servers/tools are
  mounted — the structural security control from ADR-0009.

Success criterion: a logged-in user can ask a natural-language question about their
Constellation contacts in the browser and get a correct, grounded answer, with the
model provably unable to reach any non-allowlisted data.

## 3. Out of scope / deferred

Each of these is a deliberate "not yet", gated on the PoC succeeding (and, where noted,
on a new decision):

- More data sources (each addition = an explicit decision, ideally an ADR-0009 amendment).
- **Vitae medical records and photos — never** (permanent hard-deny, not a phase order).
- Any write or outbound-messaging tool (would require human-in-the-loop confirmation in
  the UI, per ADR-0009).
- Persistence / conversation history (the PoC is stateless — `docs/decisions.md` D4).
- A self-hosted / local model, or a multi-provider abstraction.
- ntfy or any non-web input channel. (ntfy currently runs no-auth and is unsuitable for
  a channel that triggers tool calls on personal data — see the infra request.)

## 4. The data boundary (contract)

Restated from ADR-0009 because it is this project's defining constraint — neither this
file nor the ADR is the sole source of truth without the other:

- **Constellation** — allowed (read-only).
- **Vitae (medical) and photos** — permanently denied; no tool reaching them is ever
  mounted, so the boundary holds structurally.
- **Anything else** — opt-in only, per explicit decision.

Enforced in code/config, never in prompt text. The model is not the control.

## 5. Safety posture

- Read-only tools only for the PoC.
- Nova is non-authoritative: it suggests and retrieves, never acts unattended.
- Any future write/outbound tool requires explicit human-in-the-loop confirmation in
  the UI before execution.

## 6. Build plan

Phases are sequential; each ends with something demonstrable. Only Phase 0 is done.

- **Phase 0 — Repo bootstrap (done, 2026-11-23).** Seedling copy turned into a real
  Nova repository: identity docs, `CLAUDE.md`, the Atlas sync-contract files, local
  decisions, and this plan.
- **Phase 1 — Scaffold (done, 2026-11-23).** Scaffold promoted to the repo root and
  `template/` removed: `Dockerfile`, `compose.yaml` (external `atlas` network, no bundled
  DB), `src/config.py`, and a server-rendered chat UI exposing `GET /health`. Runs via
  `docker compose up -d`.
- **Phase 2 — Agent loop (done, 2026-11-23).** Anthropic client + streaming tool-use
  loop (`src/agent/loop.py`), responses streamed into the chat UI as NDJSON. One safe
  built-in tool (`get_current_time`, no data source, no side effects) exercises the loop;
  the allowlist (`src/agent/tools.py`) is the structural control. Verified end-to-end
  locally.
- **Phase 3 — Constellation via MCP (done, 2026-11-23).** Constellation shipped its
  read-only MCP server (streamable-HTTP, tools `list_contacts` / `get_contact`). Nova
  mounts it through the allowlist: `src/agent/mcp_client.py` is an MCP client over the
  `mcp` SDK; `src/agent/tools.py`'s registry discovers its tools (namespaced
  `constellation__*`) and routes calls back. Contract-verified locally against a real
  streamable-HTTP MCP server. First run against the *deployed* server is Phase 4.
- **Phase 4 — Deploy (in progress).** App-side tooling is built: a git-pull-and-rebuild
  systemd timer (`deploy/`) and a `GET /version` stamp, mirroring Constellation.
  Remaining is operator/infra: `atlas-infrastructure` adds the `nova.atlas` Caddy route
  (→ `nova:8080`) + Authentik `forward_auth` + Homepage entry (request pre-filed there),
  and the operator deploys to the Pi with a real `.env` (`ANTHROPIC_API_KEY` +
  `CONSTELLATION_MCP_URL`). First end-to-end run against real data happens here.

## 7. Future direction (not committed)

Only if the PoC proves useful: additional read-only sources via the allowlist,
conversation persistence (Nova's own Postgres database), human-in-the-loop write
tools, and — if hardware ever allows — revisiting the cloud-model deviation. None of
these is started; follow actual need, not speculation.
