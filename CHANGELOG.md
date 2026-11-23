# Changelog

Notable changes to the Nova repository. Day-to-day build progress lives in
`docs/CURRENT.md`'s Changelog section (the Atlas sync contract); this file records
repository-level milestones.

## 2026-11-23 — Bootstrap + chat PoC shell (Phases 0–2)

- **Phase 0 — Bootstrap.** Turned the `atlas-seedling` copy into a real Atlas
  application repository. Rewrote `README.md` and `STANDARDS.md` for Nova's identity;
  added `CLAUDE.md`, `docs/PROJECT.md`, `docs/decisions.md`, `docs/CURRENT.md`, and
  `docs/ATLAS_REQUESTS.md`; refreshed `docs/platform-assumptions.md`'s Authentication
  section to reflect Authentik now being live. Stack decided (Python); PoC scoped
  (stateless, Constellation-only via a read-only MCP server, web chat behind Authentik).
- **Phases 1–2 — Scaffold + agent loop.** Promoted the scaffold to the repo root and
  removed the `template/` folder: `Dockerfile`, `compose.yaml` (external `atlas` network,
  no bundled DB), `requirements.txt`, `src/config.py`. Built a server-rendered Flask
  chat (`src/web/`) with `GET /health` and a streaming `/chat`, and the Claude agent
  loop (`src/agent/`) with the ADR-0009 data-class allowlist expressed as "only listed
  tools are mounted" — PoC tool `get_current_time` only, no data source. Runs via
  `docker compose up -d`; verified locally. Phase 3 (Constellation MCP) is blocked on
  that repo shipping its server — see `docs/CURRENT.md`.
