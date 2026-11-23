# Nova — Project-Specific Standards

General Atlas engineering standards — containerization, twelve-factor configuration,
database (per-app on the shared Postgres), health checks, logging, security/secrets,
documentation, and the Definition of Done — are owned by the root
[`atlas`](../atlas) repo's `docs/STANDARDS.md`. Nova follows that document; this file
does **not** restate it. It only covers what's specific to Nova.

For the concrete facts about the live platform Nova integrates with (reverse-proxy
registration, Authentik gating, shared network name, monitoring, auth status), see
[`docs/platform-assumptions.md`](docs/platform-assumptions.md). For Claude-specific
behavioural guardrails, see [`CLAUDE.md`](CLAUDE.md). For recorded design decisions,
see [`docs/decisions.md`](docs/decisions.md).

---

## Data access & the boundary

Nova's defining standard is the data-class allowlist: it mounts a tool/MCP server only
for an explicitly allowlisted source, in code/config, never on the strength of a prompt
instruction. Vitae (medical records) and photos are permanently denied — no tool
reaching them is ever mounted. See `CLAUDE.md` §1 and
`atlas/docs/adr/0009-nova-personal-assistant-data-boundary.md`.

## Data storage

Nova is stateless for the proof of concept (`docs/decisions.md` D4): no bundled
database, no shared tables, no shared database. It is the source of truth for no
data — every source application remains authoritative for its own. If conversation
persistence is ever added, it becomes Nova's own database on the shared Postgres
instance, never a shared schema.

## Design decisions log

`docs/decisions.md` records Nova's own non-obvious choices — separate from the root
repo's ADRs, which are for decisions affecting multiple Atlas repositories. The data
boundary itself is such a cross-repo decision and lives in ADR-0009, not here. Escalate
to a root-repo ADR only when a decision genuinely isn't local to Nova.

## Definition of Done

Nova is production-ready once it satisfies the root repo's `docs/STANDARDS.md`
"Definition of Done" checklist. Nothing here relaxes that list. The Nova-specific item
to watch, because the platform doesn't cover it for free: the data boundary is enforced
structurally (denied tools are not mounted) and personal data returned from tools is
never written to logs.
