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

- None blocking. (The Constellation MCP-server dependency below is tracked, not a
  question.)

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
