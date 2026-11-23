# CLAUDE.md — Nova

Instructions for Claude when working in this repository.

**Read first, don't restate here:**
- [README.md](README.md) — what Nova is, the data boundary, architecture, deployment.
- [docs/PROJECT.md](docs/PROJECT.md) — the problem, in/out of scope, and the phased build plan.
- [docs/CURRENT.md](docs/CURRENT.md) — current phase, open questions, blockers (the Atlas sync contract).
- [docs/decisions.md](docs/decisions.md) — this project's local architectural decisions.
- [STANDARDS.md](STANDARDS.md) + the root Atlas `docs/STANDARDS.md` — engineering conventions.
- The sibling [`atlas`](../atlas) repo's `docs/adr/0009-nova-personal-assistant-data-boundary.md`
  and `docs/services/NOVA-ASSISTANT.md` — Nova's charter, owned upstream.

This file only covers Claude-specific guardrails. If something here appears to
conflict with README.md / PROJECT.md, those win for *what* Nova is; this file governs
only *how Claude behaves* while building it.

This is a **personal, single-user project**. Optimise for a small, understandable
codebase — not for scale, multi-tenancy, or future flexibility not already described
in these docs.

---

## 1. The hard line (non-negotiable)

Nova's security boundary is a **data-class allowlist enforced in code/config, never in
prompt text** (ADR-0009). When writing any code that gives the model reach:

- **Vitae (medical records) and photos are permanently denied.** Never mount, wire,
  configure, or even stub a tool/MCP server that can reach that data — not "behind a
  flag", not "for testing", not "the model won't ask". The boundary must hold because
  the tool does not exist in the running process, not because the prompt says so.
- **Adding any new data source is out of scope** without explicit user confirmation
  and (ideally) an ADR-0009 amendment. The PoC source is **Constellation only**.
- **Read-only only.** Do not add a write tool, an outbound-messaging tool, or any tool
  with a side effect without first stopping and getting explicit confirmation — and
  even then, it requires human-in-the-loop confirmation *in the UI* before execution
  (ADR-0009). Nova is non-authoritative.
- The allowlist is **data about which tools are mounted**, expressed in config/code.
  Never let model instructions, system-prompt text, or user input decide what Nova can
  reach.

If a task seems to require crossing any of these, **stop and ask** — do not implement
the smallest version "to be safe".

---

## 2. Scope discipline (YAGNI)

The PoC is: a web chat → an agent loop over Claude → one read-only MCP source
(Constellation) → a grounded answer. Do **not** build, unless explicitly requested:

- a second data source, or a generic "source registry" / provider-abstraction layer
- any persistence / database / chat-history store (the PoC is stateless — see
  `docs/decisions.md`)
- a local/self-hosted model or a multi-provider LLM abstraction (cloud Claude is the
  deliberate, accepted choice for the PoC — same deviation class as Constellation)
- write or outbound tools (see §1)
- ntfy or any non-web input channel
- auth of Nova's own (gating is Authentik `forward_auth`, owned by infrastructure)
- a build step / SPA framework — follow the server-rendered, minimal-page-JS
  convention Constellation and Clio use

When a second real source is actually requested, extract shared code only where the
first implementation has proven it is genuinely shared.

---

## 3. Working style

- Work from `docs/CURRENT.md`'s current milestone / tasks, in order. Don't jump ahead.
- Keep functions small and single-purpose; keep the agent loop, the MCP client, and
  the web layer as separate, obvious modules.
- Prefer plain Python and a small number of well-known libraries (the Anthropic SDK,
  the official MCP SDK, a light web framework) over new frameworks.
- Keep `docs/CURRENT.md` current — it's the file the Atlas Architect reads (see §6).
  Move completed work into its Changelog; archive the Changelog when it grows large
  (the pattern Constellation and Clio use).

## 4. Secrets & config

- Never hardcode API keys or credentials. All config comes from `.env` (gitignored)
  via a single config module. `ANTHROPIC_API_KEY` is the one secret the PoC needs.
- Never commit `.env`. If a task needs a new secret, add it to the config module and
  `.env.example` with a placeholder — never a real value.
- Never log data returned from a data source (contact details, etc.) or full model
  prompts/responses containing personal data. Log that a tool was called and with what
  shape, not the contents.

## 5. Commits & git

- One logical change per commit. Format: `<area>: <short description>` (e.g.
  `docs: bootstrap nova repo from seedling`, `agent: add claude tool-use loop`).
- Commit or push only when asked. Branch first if on `master`.

## 6. Atlas sync responsibilities

Per `atlas/docs/adr/0003-cross-repo-current-md-sync.md`:
- Keep `docs/CURRENT.md` accurate — it's the only file here the Atlas Architect reads,
  and only on request.
- `docs/ATLAS_REQUESTS.md` entries are appended **only** by the Atlas Architect; you
  own resolving and clearing them. Never edit/remove an entry except to mark it
  resolved once it genuinely is.
- **You must not modify** `atlas`, `atlas-infrastructure`, or
  `constellation-relationship-manager` (or any other service repo). Cross-repo needs —
  e.g. Constellation building its read-only MCP server, or infrastructure adding the
  Caddy/Authentik/Homepage wiring — are recorded as open questions/dependencies in
  `docs/CURRENT.md` and flow out through the Architect; you never write into those
  repos yourself.

## 7. When something is ambiguous

If the docs don't clearly cover a decision (exact module names, prompt wording, a port
number), make a reasonable choice, implement it, and note the assumption in the commit
message or a code comment — unless the ambiguity touches §1 (the hard line) or §2
(scope), in which case stop and ask.
