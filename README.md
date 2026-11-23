# Nova

Nova is Atlas's personal assistant: a natural-language chat interface that plans
steps, reads **your own** data through read-only interfaces, and answers — an AI
enhancement layer over the rest of the Atlas homelab, never a dependency of it.

This repository is one application within the Atlas homelab platform. For
platform-level context — why Nova exists relative to the rest of Atlas, the data
boundary it must honour, deployment/infrastructure ownership, and shared
engineering standards — read the sibling [`atlas`](../atlas) repository:
`docs/services/NOVA-ASSISTANT.md`, `docs/adr/0009-nova-personal-assistant-data-boundary.md`,
`docs/VISION.md`, `docs/ARCHITECTURE.md`, and `docs/STANDARDS.md`. This file does not
duplicate them; it references them.

## Purpose

See [`docs/PROJECT.md`](docs/PROJECT.md) for the problem Nova solves, its scope, and
the phased build plan. In short: the only conversational channel into Atlas today is
one-way ntfy push and per-app web UIs. Nova adds a two-way, natural-language way to
ask questions over your own data — bounded, read-only, and non-authoritative.

## The data boundary (read this first)

Nova reasons via a **cloud** model (Anthropic Claude), so what it can read is
constrained by an explicit **data-class allowlist enforced in code/config, not in
prompt text**. The model is not the control; the allowlist is.

- **Constellation** — allowed (the proof-of-concept source; read-only).
- **Vitae (medical records) and photos** — **permanently denied** to any
  cloud-backed assistant. No tool reaching that data is ever mounted, so the
  boundary holds structurally rather than depending on the model declining to ask.
- **Any other source** — opt-in only, each addition an explicit decision (ideally an
  amendment to ADR-0009).

This hard line is owned by `atlas/docs/adr/0009` and restated identically in
`atlas/docs/services/NOVA-ASSISTANT.md`; it is repeated here because it is the single
most important constraint on this repository.

## Features (proof of concept)

- A small server-rendered **web chat** at `nova.atlas`, behind Tailscale + Authentik.
- An **agent loop** driving Anthropic Claude via tool-use.
- A single read-only data source for the PoC: **Constellation**, consumed through its
  own read-only **MCP server** (owned by that repository — see Architecture).
- **Read-only, non-authoritative.** Nova suggests and retrieves; it never acts
  unattended. Any future write or outbound-messaging tool requires explicit
  human-in-the-loop confirmation.

## Architecture

```
browser ──HTTP──> Caddy ──forward_auth──> Authentik
                   │ (nova.atlas, Tailscale-only)
                   ▼
              Nova (this repo)
         ┌──────────────────────┐
         │  web chat (Flask)    │
         │  agent loop (Claude) │
         │  MCP client          │
         │  data-class allowlist│  ← mounts only allowlisted MCP servers
         └──────────┬───────────┘
                    │ MCP (read-only)
                    ▼
     Constellation's read-only MCP server (owned by constellation-relationship-manager)
```

Nova owns only the conversation / orchestration domain. It owns no other
application's data and holds no shared database. It is a tolerant, read-only
consumer — every Atlas application stays fully usable with Nova switched off. See
[`docs/decisions.md`](docs/decisions.md) for the local implementation choices (Python,
MCP-client-only, stateless PoC, server-rendered UI).

## Status

**Bootstrapped from `atlas-seedling` on 2026-11-23; Phases 0–2 built** (see
`docs/PROJECT.md` §6). The web chat, the Claude agent loop, and a safe built-in tool
are working and verified locally. The next step — reading real data via Constellation's
MCP server (Phase 3) — is **blocked on Constellation shipping that server**; see
[`docs/CURRENT.md`](docs/CURRENT.md). The architectural decision and data boundary are
settled upstream (ADR-0009).

## Local development

```bash
cp .env.example .env
# fill in .env (at minimum ANTHROPIC_API_KEY)
docker compose up -d        # serves http://localhost:8080
```

Without Docker, for iterating locally:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m src.web.app       # http://localhost:8080 (ANTHROPIC_API_KEY required for /chat)
```

`GET /health` works without a key; the chat needs `ANTHROPIC_API_KEY` set.

## Deployment

Nova is reached at `https://nova.atlas`, fronted by the shared Caddy instance and
gated by Authentik `forward_auth`, on the shared `atlas` Docker network — the same
boundary every other internal UI uses. The Caddy route, Authentik gating, and the
Homepage entry are owned by `atlas-infrastructure` (a request for this wiring is
already pre-filed in that repo's `docs/ATLAS_REQUESTS.md`, 2026-11-23). See
[`docs/platform-assumptions.md`](docs/platform-assumptions.md) for the concrete
platform facts and [`atlas/docs/STANDARDS.md`](../atlas/docs/STANDARDS.md) for the
app-owned half of the deployment contract.

## Environment variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | API key for the cloud reasoning model (Claude). |
| `APP_URL` | Public URL this service is reached at (`https://nova.atlas`). |
| `PORT` | Port the app listens on inside the container. |
| `LOG_LEVEL` | Logging verbosity. |
| `CONSTELLATION_MCP_URL` | URL of Constellation's read-only MCP server on the `atlas` network (contract to be finalised with that repo). Unset = source disabled. |

No `POSTGRES_*` variables: the PoC is **stateless** and provisions no database (see
`docs/decisions.md`). This table grows as the scaffold lands.

## Backup strategy

Nothing to back up for the PoC — Nova is stateless and is the source of truth for no
data. If conversation persistence is ever added, this section and a restore procedure
become required (per `atlas/docs/STANDARDS.md`).

## Related repositories

- [atlas](../atlas) — vision, architecture, standards, and ADR-0009 (Nova's charter).
- [atlas-infrastructure](../atlas-infrastructure) — the live platform Nova deploys onto.
- [constellation-relationship-manager](../constellation-relationship-manager) — the
  PoC data source; owns the read-only MCP server Nova consumes.
