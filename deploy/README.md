# Auto-deploy setup (Raspberry Pi)

A systemd timer that checks GitHub every 5 minutes and, if `origin/master` has moved,
pulls and runs `docker compose up -d --build`. No CI/CD pipeline, no image registry —
the Pi builds its own image locally, same pattern as Constellation.

Nova is not deployed yet; this is the tooling for Phase 4. The infrastructure side
(the `nova.atlas` Caddy route + Authentik `forward_auth` + Homepage entry) is owned by
`atlas-infrastructure` — see this repo's `docs/CURRENT.md` and `README.md` Deployment.

## One-time setup, on the Pi

1. Clone the repo and create `.env` (see `README.md`'s Deployment section). At minimum
   set `ANTHROPIC_API_KEY` and `CONSTELLATION_MCP_URL=http://constellation-mcp:8000/mcp`.
2. Edit `deploy/nova-deploy.service`: replace all `<PI_USER>` placeholders (including
   `User=`) with the account the repo is cloned under, and fix the path if it's not
   `~/nova-assistant`.
3. Install the units:
   ```bash
   sudo cp deploy/nova-deploy.service deploy/nova-deploy.timer /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now nova-deploy.timer
   ```
4. The account running this needs to run `docker compose` (typically: member of the
   `docker` group) and needs `git pull` to work non-interactively against `origin`
   (HTTPS with a cached credential, or an SSH remote with a deploy key — confirm a
   manual `git pull` works without prompting first).

## Checking it's working

```bash
systemctl status nova-deploy.timer            # timer active/enabled
journalctl -u nova-deploy.service -f           # follow the deploy log live
```

Each run logs one line: "up to date, nothing to do" or "new commits found… deploy complete".

## Test gate before rebuild

If a `tests/` directory exists, `deploy.sh` runs the suite (`.venv/bin/pytest` if a
local venv exists, else `pytest` on `PATH`) after `git pull` and before rebuilding; a
failure aborts without touching the running containers. The PoC has no test suite yet,
so the gate is skipped automatically — it activates once tests are added (and a dev
venv is set up: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`).

## What this deliberately doesn't do

No GitHub Actions, no container registry, no webhook — polling, not push-triggered;
a real push typically lands within 5 minutes. See `atlas/docs/STANDARDS.md` and
Constellation's `deploy/README.md` for the shared rationale.
