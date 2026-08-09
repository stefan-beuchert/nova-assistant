# atlas-seedling

Template seed for future Atlas Homelab projects. This is **not** a runnable project itself — it's a starting point you copy from when a new Atlas service (like Constellation, Orbit, etc.) is ready to be built.

## Status

The Atlas homelab platform is live: Docker host, Caddy reverse proxy, shared PostgreSQL, and a Prometheus/Grafana/Alertmanager monitoring stack have all been running in production since 2026-08-02 (see the root [`atlas`](https://github.com/stefan-beuchert/atlas-homelab) repo's `docs/ROADMAP.md`, Phase 1). [`docs/platform-assumptions.md`](docs/platform-assumptions.md) reflects the actual, confirmed platform facts a new project needs (reverse proxy registration, Postgres provisioning, network name) — it is no longer a list of open questions. A few things (shared auth) are still genuinely not built yet; that file says which. Revisions get logged in [`CHANGELOG.md`](CHANGELOG.md).

## What's here

- **`STANDARDS.md`** — template-specific conventions for using this scaffold. General Atlas engineering standards live in the root [`atlas`](https://github.com/stefan-beuchert/atlas-homelab) repo's `docs/STANDARDS.md` — this file links to it rather than restating it.
- **`CHANGELOG.md`** — revision history for this template.
- **`docs/platform-assumptions.md`** — concrete, confirmed facts about the live Atlas platform (reverse proxy, Postgres, networking, monitoring, auth) that a new project needs to integrate with.
- **`template/`** — the actual scaffold to copy for a new project.

## Starting a new project from this template

1. Copy the `template/` folder into a new repository:
   ```bash
   cp -r atlas-seedling/template ../my-new-project
   cd ../my-new-project
   ```
2. Fill in `Dockerfile` for your project's language/framework — the one in the template is a commented placeholder, not a working build.
3. Update `README.md` (Purpose, Features, Architecture, etc.) and `.env.example` with your project's actual variables.
4. Implement `GET /health` per the root repo's `docs/STANDARDS.md`.
5. Follow `docs/platform-assumptions.md` to register with the shared Caddy reverse proxy and get a Postgres database/user provisioned before wiring up `compose.yaml` fully.

## Related Repositories

- [atlas](https://github.com/stefan-beuchert/atlas-homelab) — vision, architecture and engineering standards this template must follow
- [atlas-infrastructure](https://github.com/stefan-beuchert/atlas-infrastructure) — the live platform this template targets
- [constellation-relationship-manager](https://github.com/stefan-beuchert/constellation-relationship-manager) — the first Atlas service, as a worked example of a project built to these standards
