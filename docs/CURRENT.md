# Current Work

Sync-contract file for the Atlas Architect, per
`atlas/docs/adr/0003-cross-repo-current-md-sync.md` and `atlas/docs/STANDARDS.md`. The
Architect reads only this file in this repository, and only on request. Keep it a short
bullet list — a sync contract, not a status report.

## Current Phase

Bootstrapped from `atlas-seedling` and built through **Phase 4** (2026-11-23/24).
`docs/PROJECT.md` §6 Phases 0–4 are done: identity/sync docs; the app scaffold
(`Dockerfile`, `compose.yaml` on the external `atlas` network, no bundled DB,
`GET /health`); the streaming web chat + Claude agent loop; the **Constellation
MCP integration** — Nova mounts Constellation's read-only MCP server through the
data-class allowlist (`src/agent/mcp_client.py` + `src/agent/tools.py`) and can call
`list_contacts` / `get_contact`; and **deployment** — infra added the `nova.atlas`
Caddy route + Authentik gating + Homepage entry, and Nova now runs on the Pi against
the live Constellation MCP server (`GET /version` reports the live commit;
`nova-deploy.timer` keeps it current). The PoC success criterion is met: a logged-in
user can ask a natural-language question about their Constellation contacts and get a
grounded answer.

## Next Milestone

**PoC complete — no committed next phase.** The build plan (`docs/PROJECT.md` §6) is
delivered end to end. Further work is the uncommitted future direction in
`docs/PROJECT.md` §7 (additional read-only sources via the allowlist, conversation
persistence, human-in-the-loop write tools), pursued only if the PoC proves useful and
each via its own explicit decision. Near-term, iterating on the chat UI.

## Deviations from Atlas Vision, Architecture, or Standards

- **Cloud LLM.** `atlas/docs/ROADMAP.md` (Phase 3) makes self-hosted Ollama the default
  and cloud providers opt-in. Nova reasons via cloud Anthropic Claude. Deliberate,
  accepted deviation — the same class as Constellation's LLM connector; a local model
  is not viable on the current Pi (ADR-0009). Revisit if hardware changes.

## Open Questions for the Architect

- **ADR-0009 needs amending for Nova's 2nd data source.** On 2026-11-25, with explicit
  user confirmation, Nova mounted **Nexus's read-only calendar MCP server** (`nexus-mcp`
  on the `atlas` network, tools `calendar__list_events` / `calendar__list_calendars`)
  through the allowlist alongside Constellation. ADR-0009 (owned upstream in `atlas`)
  still describes Constellation as the sole PoC source — please amend it to record
  calendar as an allowed read-only class. Note the boundary rationale is unchanged:
  Vitae (medical) and photos remain permanently denied. Nova cannot edit `atlas`/`nexus`
  repos (CLAUDE.md §6), so this flows through you.

## Blockers / Dependencies

- **None.** Both cross-repo dependencies are resolved. **Phase 3 (Constellation MCP):**
  Constellation shipped its read-only MCP server (`constellation-mcp` on the `atlas`
  network, streamable-HTTP on :8000, tools `list_contacts` / `get_contact`) and Nova
  consumes it via the allowlist (`CONSTELLATION_MCP_URL`). **Phase 4 (deploy):**
  `atlas-infrastructure` added the `nova.atlas` Caddy route, Authentik `forward_auth`,
  and the Homepage entry; Nova is live on the Pi and the full Nova → live Constellation
  path now runs against real data.

## Notes

Temporary, in-progress implementation notes belong here. Once a decision becomes
permanent it belongs in `README.md`, `docs/PROJECT.md`, or `docs/decisions.md` — not here.

Bootstrap leftovers are cleared: the `template/` scaffold folder and the Windows
`*:Zone.Identifier` artifacts are removed.

## Changelog

- 2026-11-25 (post-PoC — 2nd data source) — Mounted **Nexus's read-only calendar MCP
  server** through the ADR-0009 allowlist, with explicit user confirmation (CLAUDE.md
  §2). `src/config.py` adds `NEXUS_MCP_URL` (blank = disabled, same posture as
  Constellation); `src/agent/tools.py`'s `build_allowlisted_sources` appends
  `McpSource("calendar", …)`, so Nova discovers `calendar__list_events` /
  `calendar__list_calendars` and `/health` reports `calendar` once the source is
  reachable. No new write/outbound path — Nova only relays the server's read-only tools;
  Vitae/photos stay permanently absent. `.env.example` documents the URL
  (`http://nexus-mcp:8000/mcp`). The ADR-0009 amendment for a 2nd source is owned
  upstream — flagged under Open Questions. First real discovery happens on the Pi after
  deploy (the `atlas`-network server isn't reachable from a dev box). Not committed yet.
- 2026-11-25 (post-PoC — chat UI) — Two backlog items from `docs/PROJECT.md` §7,
  both within the accepted cloud-Claude decision and the ADR-0009 boundary (no new
  data reach, no write/outbound tool). **Text-to-speech:** Nova's replies can be read
  aloud via the browser's on-device `speechSynthesis` — no audio or text leaves the
  machine, so no new egress. A per-reply speaker button plays/stops any reply, and a
  persisted header toggle auto-speaks new replies; speech stops on a new turn or reset
  (`src/web/templates/index.html`, client-only). **Model switcher:** the active Claude
  is selectable per turn from a config-defined allowlist (`Config.MODELS` / env
  `ANTHROPIC_MODELS`, default Opus 4.8 / Sonnet 5 / Haiku 4.5). The set is *data in
  config* — the same posture as the tool allowlist (D3) — and `/chat` re-validates the
  requested id server-side, falling back to the default; a model choice never widens
  what data Nova can reach. Header `<select>` (persisted, server-rendered from the
  allowlist) in `index.html`; `src/config.py` + `src/web/app.py`. **Voice input
  (speech-to-text):** a mic button dictates into the message box via the browser's
  `SpeechRecognition` (`index.html`, client-only; hidden where unsupported). Unlike the
  on-device TTS, this streams audio to Google's cloud in Chrome/Edge — a deliberate,
  recorded trade (the query text already goes to Anthropic; never touches hard-denied
  data), to be revisited with a self-hosted Whisper once the homelab can host one — see
  `docs/PROJECT.md` §7. Not committed yet.
- 2026-11-24 (post-PoC — chat UI) — Functional polish to the web chat
  (`src/web/templates/index.html`, client-side only, no backend/protocol change):
  Nova's replies now render markdown via a small self-contained renderer
  (HTML-escaped first, safe http/mailto links only); the transient "using <tool>"
  status became a persistent "source · tool" grounding chip parsed from the
  `<source>__<tool>` namespace; and the layout is centered in a max-width column
  with a mobile breakpoint and stick-to-bottom auto-scroll. On branch
  `chat-ui-improvements`.
- 2026-11-24 (Phase 4 — deployed) — Infra/operator completed deployment:
  `atlas-infrastructure` added the `nova.atlas` Caddy route (→ `nova:8080`), Authentik
  `forward_auth`, and the Homepage entry, and Nova was deployed to the Pi (real `.env`,
  `docker compose up -d --build`, `nova-deploy.timer` enabled). Nova now runs on the
  `atlas` network against the **live** Constellation MCP server — the first end-to-end
  run against real data. Phase 4 and the PoC build plan are complete.
- 2026-11-23 (Phase 4 — app-side) — Added deploy tooling: `deploy/deploy.sh`
  (git-pull-and-rebuild poller with a conditional test gate), `deploy/nova-deploy.{service,timer}`,
  and `deploy/README.md`, mirroring Constellation. Added a running-version stamp
  (`APP_VERSION`/`APP_BUILD_TIME` via compose → `GET /version`). README Deployment
  rewritten into app-owned vs platform-owned halves. The remaining Phase-4 work is
  operator/infra (Caddy/Authentik wiring + the Pi deploy with a real `ANTHROPIC_API_KEY`).
- 2026-11-23 (Phase 3) — Integrated Constellation's read-only MCP server. New MCP
  client bridge `src/agent/mcp_client.py` (sync wrapper over the `mcp` 2.x high-level
  `Client`, streamable-HTTP, fresh connection per call, best-effort). `src/agent/tools.py`
  now holds a `ToolRegistry` + `build_allowlisted_sources` — the ADR-0009 allowlist in
  code: only explicitly configured MCP sources (Constellation; Vitae/photos never) are
  mounted, their tools namespaced `<source>__<tool>`. `run_turn` and the web app take
  the registry; `/health` reports mounted `sources`. Added `mcp>=2,<3`; set
  `CONSTELLATION_MCP_URL` default to `http://constellation-mcp:8000/mcp`. Verified end to
  end against a real streamable-HTTP MCP stub (contract-identical): tool discovery,
  `list_contacts`/`get_contact`/not-found, allowlist gating, registry routing, and the
  full loop stream → tool_use → live MCP call → tool_result → done. Not committed yet.
- 2026-11-23 (Phases 1–2) — Scaffolded the app and built the chat PoC's shell.
  `Dockerfile` (python:3.12-slim), `compose.yaml` (external `atlas` network, no DB),
  `requirements.txt` (anthropic, flask, python-dotenv), `src/config.py`, and a
  server-rendered Flask chat (`src/web/app.py` + `templates/index.html`, no build step)
  with `GET /health`, `/chat` (NDJSON streaming), `/reset`. The agent loop
  (`src/agent/loop.py`) streams Claude with adaptive thinking and runs the allowlisted
  built-in tools in `src/agent/tools.py` — PoC tool `get_current_time` only; the
  data-class allowlist (ADR-0009) is enforced as "only listed tools are mounted".
  Conversation state is in-memory per session (no persistence, D4). Removed `template/`
  and `*:Zone.Identifier` leftovers. Verified locally: app boots without the SDK,
  `/health` + `/` respond, and a fake-client test drives the full stream → tool_use →
  execute → loop → done path. Not committed to git yet.
- 2026-11-23 (Phase 0) — Repository bootstrapped from `atlas-seedling`. Rewrote
  `README.md` and `STANDARDS.md` for Nova's identity, added `CLAUDE.md`,
  `docs/PROJECT.md`, `docs/decisions.md` (D1–D5), this `docs/CURRENT.md`, and
  `docs/ATLAS_REQUESTS.md`, and refreshed `docs/platform-assumptions.md`'s auth section
  (Authentik is now live). Stack decided (Python), PoC scoped (stateless,
  Constellation-only via MCP).
