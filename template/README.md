# <project-name>

TODO: one-line description of what this service does.

## Purpose

TODO: why this service exists, what problem it solves.

## Features

TODO: bullet list of key features.

## Architecture

TODO: how it's put together — key components, how it talks to Postgres/other services, any diagrams if useful. Complex decisions belong in `docs/decisions.md`, not here.

## Local development

```bash
cp .env.example .env
# fill in .env
docker compose up -d
```

TODO: anything else needed to run locally (seed data, migrations, etc.)

## Deployment

1. Get a Postgres database + user provisioned on the shared instance (ask whoever runs `atlas-infrastructure` — it's a manual `psql` step today, see [`docs/platform-assumptions.md`](../docs/platform-assumptions.md)).
2. Add a site block for this service to the shared Caddyfile in `atlas-infrastructure`, then have Caddy redeployed with `docker compose -f compose/caddy/docker-compose.yml up -d --force-recreate` (a plain `up -d` or `caddy reload` won't pick up the change).
3. Clone this repo onto the host and run `docker compose up -d --build`. There's no CI/CD or image registry expected yet — a simple git-pull-and-rebuild step (see Constellation's `constellation-deploy.timer` for a working example) is an acceptable pattern.

See [`docs/platform-assumptions.md`](../docs/platform-assumptions.md) for the full current platform picture.

## Environment variables

| Variable | Description |
|---|---|
| `POSTGRES_HOST` | Postgres service name on the shared network (`postgres`) |
| `POSTGRES_PORT` | Postgres port (`5432`) |
| `POSTGRES_DB` | This app's database name, provisioned per `docs/platform-assumptions.md` |
| `POSTGRES_USER` | This app's database user |
| `POSTGRES_PASSWORD` | This app's database password |
| `JWT_SECRET` | TODO |
| `LOG_LEVEL` | Logging verbosity |
| `APP_URL` | Public URL this service is reachable at (`https://<service>.atlas`) |
| `PORT` | Port the app listens on inside the container |

## Backup strategy

TODO: what must be backed up (database, uploaded files, config) and how often.

## Restore procedure

TODO: exact steps to restore from backup on a fresh host — should require nothing beyond installing Docker, cloning this repo, restoring backups, and `docker compose up -d`.
