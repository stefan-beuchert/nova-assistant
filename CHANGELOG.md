# Changelog

All notable changes to Atlas engineering standards and the seedling template are logged here.

## 2.0 — 2026-08-09

- The Atlas homelab platform went live 2026-08-02 (confirmed via `atlas-infrastructure` and `constellation-relationship-manager`'s own `CURRENT.md` files during a full platform audit on this date), which made this template's core premise — "the homelab isn't built yet" — false. Rewrote `README.md`, `docs/platform-assumptions.md`, `template/compose.yaml`, `template/.env.example`, and `template/README.md` to reflect the actual, confirmed platform: Caddy as the reverse proxy (static Caddyfile registration, with a redeploy gotcha), one Postgres database + user per app (manual `psql` provisioning), the shared Docker network's real name (`atlas`), live monitoring, automatic Postgres backups, and auth still genuinely not built.
- Rewrote `STANDARDS.md`: it previously duplicated the root `atlas` repo's `docs/STANDARDS.md` "Application Repository Standards" section almost verbatim, as an independently-maintained copy — a violation of Atlas's own single-ownership documentation rule, and a source of drift (this file had grown its own extra sections not present upstream). It now links to the root doc instead of restating it, and only covers what's genuinely specific to this scaffold (data storage guidance, the decisions log, how the Definition of Done maps here). See the root repo's `docs/adr/0005-template-repository.md` for the rule this codifies going forward.

## 1.0 — 2026-07-21

- Initial version of `STANDARDS.md`, covering philosophy, infrastructure assumptions, twelve-factor mindset, containerization, configuration, data storage, database, networking, health checks, logging, error handling, security, documentation, API design, observability, backups, repository structure, development workflow, design principles, Atlas ecosystem integration, and Definition of Done.
- File was truncated on disk mid-Observability-section; restored to full text.
- Added `template/` scaffold, `docs/platform-assumptions.md`, and root `README.md` to make this repo usable as a starting point for new Atlas projects ahead of the homelab itself being built.

---

Future entries should record *what* changed in `STANDARDS.md` and *why* — especially decisions made once the real homelab platform (reverse proxy choice, Postgres topology, auth) is actually built and assumptions get confirmed or revised.
