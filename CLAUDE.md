# CLAUDE.md — Vitae

Instructions for Claude when working in this repository.

**Read first, don't restate here:**
* [README.md](README.md) — what Vitae is, why, domain model, architecture, API/UI shape, phased roadmap.
* [STANDARDS.md](STANDARDS.md) + the root Atlas `docs/STANDARDS.md` — engineering conventions (containerization, config, DB, health checks, security, Definition of Done).
* [docs/decisions.md](docs/decisions.md) — this project's recorded architectural decisions.

This file only covers what those don't: Claude-specific guardrails, defaults, and when to stop and ask instead of guessing. If something here appears to conflict with README.md, README.md wins for *what* Vitae is; this file only governs *how Claude behaves* while building it.

---

## Core principle

Vitae stores medical information; it does not make medical decisions. Never add diagnosis, treatment recommendation, or "is this result normal" logic — even where an implementation could technically support it.

---

## Scope discipline (YAGNI)

The MVP is glasses/vision only. Do not implement vaccinations, laboratory, medications, conditions, FHIR/HL7, AI extraction, or notifications unless explicitly requested.

Don't build generic abstractions (`UniversalMedicalRecord`, `DynamicMedicalSchema`, a medical-domain factory, etc.) for hypothetical future domains. When a second real domain is actually requested, extract shared code only where the glasses domain proves it's genuinely shared.

---

## Ask before inventing medical semantics

Stop and clarify rather than guessing when:
* a medical unit or field's meaning is ambiguous
* it's unclear whether a change is a new historical record or a correction of bad data
* a date's meaning is ambiguous (event date vs. entry date vs. document date)
* the source/provenance of a value is unclear

Never silently coerce, infer, or default a medical value.

---

## Historical records

A new real-world event (e.g. a new prescription) → new record; never overwrite a previous one. A data-entry mistake → correct the existing record. Don't confuse the two.

Every domain entity distinguishes the real-world record/event date from `created_at`/`updated_at`.

---

## Structured data, not JSON blobs

Important medical values get explicit, typed fields — not a generic `data: JSON` column. JSON is fine for genuinely flexible metadata only. Store units explicitly; never a bare number.

---

## Documents

* Binary files live in file storage, not Postgres; Postgres holds metadata + a storage reference only.
* Never expose raw filesystem paths through the API.
* Treat uploads as untrusted input: validate type and size, never trust the original filename, generate internal storage IDs, prevent path traversal, serve only through an authorized application path, don't execute uploaded content.

---

## Logging

Log that something happened, not what it contains.

Good: `Created glasses prescription record id=<id>`
Bad: `Created prescription: right=-2.25/-0.50/90, left=-1.75/-0.25/80`

Never log prescription/lab/medication values, diagnoses, or document contents.

---

## Service boundaries

Vitae is independent from Constellation and other Atlas services: no shared tables, no direct cross-service DB access, no cross-service foreign keys. Vitae has its own Postgres database and user, per `docs/platform-assumptions.md`.

---

## Authentication

No shared Atlas auth provider exists yet (`docs/platform-assumptions.md`). Don't build a custom auth system speculatively — but don't assume unauthenticated exposure is acceptable either. Before building anything that depends on an auth boundary, check `docs/decisions.md` for the recorded MVP decision; if none exists yet, stop and ask rather than picking one.

---

## Testing minimum

For any domain feature, cover: valid creation, invalid/validation cases, optional fields, historical ordering, correction/update behavior, document association, and (where relevant) upload validation and retrieval authorization. Test behavior, not implementation details.

---

## Definition of Done

Beyond the happy-path UI working: migrations run and are reproducible, validation exists, historical behavior is correct, sensitive data isn't unnecessarily logged, documents are safely stored, tests pass, and docs (README.md / docs/decisions.md) are updated. Full checklist: README § MVP Definition of Done.

---

## When implementations conflict

Prefer, in order: preserving the user's original information → preserving historical records → preserving provenance → keeping medical data structured → minimizing complexity → following Atlas conventions → keeping Vitae independent of other services → avoiding speculative functionality.

---

## Git

Small, focused commits (`feat:`, `fix:`, `docs:`) — one concern per commit, not large mixed diffs.

---

## Documentation ownership

README.md owns the vision/architecture narrative. This file owns Claude's behavioral rules only. `docs/decisions.md` owns local architectural decisions (document storage specifics, provenance model, unusual validation, auth boundary, etc.). Record decisions there — don't grow this file back into a second copy of README.md.
