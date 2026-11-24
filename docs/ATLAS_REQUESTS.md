# Atlas Requests

Entries added by the Atlas Architect, on request only, per
`atlas/docs/adr/0003-cross-repo-current-md-sync.md`. The Architect only opens entries;
resolving and clearing them belongs to this repository's own agent. This repository's
agent never edits or removes an entry except to mark it resolved once it genuinely is.

## Open

### 2026-11-24 — add a second allowlisted MCP source: calendar (via Nexus MCP)

Category: suggestion

Atlas has approved Nova's first ADR-0010 scope expansion: a second, daily-use data source — the user's Google Calendar — so Nova's real-world usefulness (ADR-0010 criterion 5) can be evaluated. The calendar is served by a new read-only connector service, **Nexus MCP** (repo `nexus-mcp`), being built starting 2026-11-25; its first module is a read-only Google Calendar connector exposing MCP tools (e.g. `list_events` / events within a date range) over streamable HTTP on the `atlas` network, same pattern as `constellation-mcp`.

Nova's side, once Nexus MCP is reachable: add `calendar` to the data-class allowlist and mount the Nexus MCP calendar source as a second MCP source (alongside `constellation`), via the existing config/allowlist mechanism — no new integration in Nova itself (Nova stays a thin read-only consumer; the Google credentials live in Nexus MCP, not here). Note the ADR-0011 §4 data posture: full calendar event content, including any health-adjacent entries the user put in their own calendar, will reach the cloud model — a deliberate, operator-accepted narrowing, distinct from and not weakening the permanent Vitae/photos source deny (no medical source is mounted).

Not actionable until Nexus MCP exposes its MCP endpoint; filed now so the dependency is visible.

Reference: `atlas/docs/adr/0011-nova-external-source-connector-service.md`, `atlas/docs/adr/0009-nova-personal-assistant-data-boundary.md`, `atlas/docs/services/NEXUS-MCP.md`.

## Resolved

_None yet._
