# Current Work

Sync-contract file for the Atlas Architect, per
`atlas/docs/adr/0003-cross-repo-current-md-sync.md` and `atlas/docs/STANDARDS.md`. The
Architect reads only this file in this repository, and only on request. Keep it a short
bullet list — a sync contract, not a status report.

## Current Phase

Bootstrapped from `atlas-seedling` and built through **Phase 2** (2026-11-23).
`docs/PROJECT.md` §6 Phases 0–2 are done: identity/sync docs, then the app scaffold
(`Dockerfile`, `compose.yaml` on the external `atlas` network, no bundled DB,
`GET /health`), then the streaming web chat and the Claude agent loop with one
safe built-in tool (`get_current_time`) to exercise tool-use. Runs via
`docker compose up -d`. Verified locally (app boots without the SDK; `/health` + `/`
respond; the loop streams, runs the tool, loops, and finishes). No data source is
wired yet.

## Next Milestone

**Phase 3 — Constellation via MCP** (`docs/PROJECT.md` §6) — **blocked** (see
Dependencies). Mount Constellation's read-only MCP server through the allowlist and
answer grounded questions about contacts. Deliberately not started until that server
exists. Phase 4 (platform deploy) follows.

## Deviations from Atlas Vision, Architecture, or Standards

- **Cloud LLM.** `atlas/docs/ROADMAP.md` (Phase 3) makes self-hosted Ollama the default
  and cloud providers opt-in. Nova reasons via cloud Anthropic Claude. Deliberate,
  accepted deviation — the same class as Constellation's LLM connector; a local model
  is not viable on the current Pi (ADR-0009). Revisit if hardware changes.

## Open Questions for the Architect

- None blocking. (The Constellation MCP-server dependency below is tracked, not a
  question.)

## Blockers / Dependencies

- **Phase 3 depends on Constellation shipping a read-only MCP server** wrapping its
  existing contact read surface (`docs/decisions.md` D2). Nova cannot write into the
  Constellation repo, so this needs to flow through the Architect into Constellation's
  `docs/ATLAS_REQUESTS.md`. This is now the active blocker: Phases 1–2 are complete, so
  the next step (Phase 3) cannot start until that server exists and its transport/URL/
  tool contract is agreed. `CONSTELLATION_MCP_URL` is reserved in config/`.env.example`
  for it.
- **Phase 4 (deploy) depends on `atlas-infrastructure`** adding the `nova.atlas` Caddy
  route, Authentik `forward_auth`, and a Homepage entry. A request for this is already
  pre-filed in that repo's `docs/ATLAS_REQUESTS.md` (2026-11-23); not actionable until
  Nova is being deployed.

## Notes

Temporary, in-progress implementation notes belong here. Once a decision becomes
permanent it belongs in `README.md`, `docs/PROJECT.md`, or `docs/decisions.md` — not here.

Bootstrap leftovers are cleared: the `template/` scaffold folder and the Windows
`*:Zone.Identifier` artifacts are removed.

## Changelog

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
