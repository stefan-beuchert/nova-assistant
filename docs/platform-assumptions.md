# Atlas Platform Facts

The Atlas homelab platform has been live since 2026-08-02 (see the root [`atlas`](../../atlas) repo's `docs/ROADMAP.md`, Phase 1 — confirmed against both `atlas-infrastructure` and `constellation-relationship-manager`'s own `CURRENT.md` files as of 2026-08-09). This doc records the concrete, proven facts a new project needs to integrate with it. It replaces the earlier "not built yet" assumptions table — where something below is still genuinely undecided, it's marked as such.

When any of these change (a different topology, a new shared service), update this file and log why in [`CHANGELOG.md`](../CHANGELOG.md).

## Reverse Proxy — Caddy

- Every service is fronted by a single shared **Caddy** instance, run by `atlas-infrastructure`, reachable only over Tailscale (plain HTTP internally, no public exposure).
- Routing is by hostname, `<service>.atlas`, configured in a static `Caddyfile` — **not** compose labels, **not** a web UI.
- To register a new service: add a site block to that `Caddyfile` in `atlas-infrastructure`, then redeploy Caddy with
  ```bash
  docker compose -f compose/caddy/docker-compose.yml up -d --force-recreate
  ```
  Plain `docker compose up -d` or `caddy reload` will **not** pick up the change — the config is bind-mounted and needs the container recreated. This is a known gotcha, not a suggestion.
- Your app should not generate absolute URLs itself; assume it's reached at `https://<service>.atlas` via the proxy and take the public URL from `APP_URL`.

## PostgreSQL — shared instance, one database per app

- One shared Postgres instance. Each app gets its **own database and its own user** (not a shared schema), provisioned manually via `psql`:
  ```sql
  CREATE DATABASE <app>;
  CREATE USER <app> WITH PASSWORD '...';
  GRANT ALL PRIVILEGES ON DATABASE <app> TO <app>;
  ALTER DATABASE <app> OWNER TO <app>; -- required on PG15+, or CREATE TABLE fails
  ```
- Connect via `POSTGRES_HOST=postgres`, `POSTGRES_PORT=5432` — resolvable only from containers on the shared network (see below), not from outside Docker.
- Provisioning is currently a manual, one-off step requested from whoever runs `atlas-infrastructure` — there is no self-service or automated provisioning tool yet.
- "Migrations must be automated" (per the root `docs/STANDARDS.md`) is the target, not something proven in production yet — Constellation's own migration to shared Postgres was a manual, one-time job. Automate your own project's migrations regardless; don't assume tooling exists at the platform level.

## Docker Network

- One shared external Docker network, named **`atlas`**. Join it in `compose.yaml` with:
  ```yaml
  networks:
    atlas:
      external: true
  ```
- Services reach each other by Docker's embedded DNS using the compose service name (e.g. `postgres`, `constellation`) — no need to publish host ports unless you need direct access during local development.

## Monitoring

- Prometheus + Grafana + Node Exporter + cAdvisor + Alertmanager are live, with alerts routed to a shared `ntfy` instance.
- Implement `GET /health` (per root `docs/STANDARDS.md`) so the platform can eventually scrape or check it — there's no automatic per-app dashboard yet, but the endpoint is expected.

## Backups

- Postgres is backed up automatically at the platform level (daily, with a verified restore drill) — you don't need to build this yourself for database state.
- Anything your app stores outside Postgres (uploaded files, OAuth tokens, other local state) is **not** covered by the platform backup and needs its own documented backup/restore procedure.

## Authentication — still not built

- No shared auth provider exists yet (Authentik is planned, not deployed). Don't build against it; if your project needs auth today, it's on you to implement it locally and revisit once a platform auth service exists.

## Open questions

- Exact shape of self-service Postgres provisioning (still manual today).
- How auth will eventually be wired in (reverse-proxy-level vs. per-app) once Authentik lands.
