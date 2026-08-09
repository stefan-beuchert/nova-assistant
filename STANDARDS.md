# atlas-seedling — Template-Specific Standards

> Version: 2.0 — see [CHANGELOG.md](CHANGELOG.md) for revision history.

General Atlas engineering standards — containerization, twelve-factor mindset, configuration, database, health checks, logging, security/secrets, documentation, Definition of Done — are owned by the root [`atlas`](../atlas) repo's `docs/STANDARDS.md`. Every project built from this template follows that document. This file does not restate it; it only covers what's specific to using this scaffold.

For the current, concrete facts about the live platform (reverse proxy registration, Postgres provisioning, shared network name, monitoring, auth status), see [`docs/platform-assumptions.md`](docs/platform-assumptions.md) — that file, not this one, is what changes as the homelab evolves.

---

# Using This Scaffold

`template/` is a starting point, not a finished project. Two things it covers that the root standards don't, because they're specific to bootstrapping a new repo from scratch:

## Data Storage

Containers are disposable — the copied scaffold has no local state by default. Persistent data belongs in the platform's shared PostgreSQL (per `docs/platform-assumptions.md`) or a Docker volume for uploaded files. Application code should never be the source of truth for user data.

## Design Decisions Log

`template/docs/decisions.md` is where a new project should record its own non-obvious choices (what was decided, why, what alternatives were considered) as it's built — separate from the root repo's ADRs, which are for decisions that affect multiple Atlas repositories. Most projects will only need this file; escalate to an ADR in the root `atlas` repo only if a decision genuinely isn't local to this project (see that repo's `CLAUDE.md`, Decision Rules).

---

# Definition of Done

A project built from this template is production-ready once it satisfies the root repo's `docs/STANDARDS.md` "Definition of Done" checklist. Nothing in this template relaxes or replaces that list.
