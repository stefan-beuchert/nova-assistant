# Changelog

Notable changes to the Nova repository. Day-to-day build progress lives in
`docs/CURRENT.md`'s Changelog section (the Atlas sync contract); this file records
repository-level milestones.

## 2026-11-23 — Deploy tooling (Phase 4, app-side)

- Added the git-pull-and-rebuild deploy mechanism (`deploy/deploy.sh` + systemd
  `nova-deploy.service`/`.timer` + `deploy/README.md`), mirroring Constellation, and a
  running-version stamp surfaced at `GET /version` (`APP_VERSION`/`APP_BUILD_TIME` set
  by the deploy script via compose). README Deployment split into app-owned vs
  platform-owned halves. Remaining Phase-4 work is operator/infra: the `nova.atlas`
  Caddy route + Authentik gating in `atlas-infrastructure`, and the Pi deploy with a
  real `ANTHROPIC_API_KEY`. See `docs/CURRENT.md`.

## 2026-11-23 — Constellation MCP integration (Phase 3)

- Nova now reads the user's contacts through **Constellation's read-only MCP server**.
  Added an MCP client bridge (`src/agent/mcp_client.py`, `mcp` 2.x `Client` over
  streamable HTTP) and reworked `src/agent/tools.py` into a `ToolRegistry` +
  `build_allowlisted_sources` — the ADR-0009 data-class allowlist in code: only
  explicitly configured MCP sources are mounted (Constellation; Vitae/photos never),
  their tools namespaced `constellation__*`. `/health` reports mounted sources. Added
  `mcp>=2,<3`; `CONSTELLATION_MCP_URL` defaults to `http://constellation-mcp:8000/mcp`.
  Verified against a real streamable-HTTP MCP server. Phase 4 (deploy) is next; the
  first run against the live Constellation server happens there. See `docs/decisions.md`
  D6 and `docs/CURRENT.md`.

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
