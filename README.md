# Vitae

**Vitae** is Atlas's personal medical information service.

It provides a private, self-hosted place to collect, structure, preserve, and retrieve personal medical information over time. Vitae is intended to grow gradually with the information that becomes available, starting with vision/glasses data and eventually potentially covering vaccinations, laboratory results, medications, conditions, medical documents, and other personal health information.

Vitae is a **record-keeping and information-access system, not a medical decision system**.

---

## Status

**Early development / MVP**

The initial version of Vitae focuses on one domain:

* Glasses / vision prescriptions
* Historical prescriptions
* Structured prescription data
* Original prescription documents or photos as source evidence

The architecture is intentionally designed to support additional medical domains later without requiring the initial application to implement them now.

---

## Purpose

Medical information tends to accumulate gradually and is often scattered across paper documents, photographs, doctor's letters, prescriptions, and personal notes.

Vitae exists to provide one private place where this information can be:

1. **Collected** — information can be entered manually.
2. **Structured** — important values are stored as queryable data rather than only as images or PDFs.
3. **Preserved historically** — records remain available instead of being overwritten by newer information.
4. **Linked to evidence** — structured information can be associated with the original document or photograph from which it was obtained.
5. **Retrieved easily** — information can be viewed by medical category and date.
6. **Expanded gradually** — new medical domains can be added when they become useful.

The goal is not to predict what medical information will eventually be needed. The goal is to provide a sound foundation that can grow with the available information.

---

# Core Principles

## 1. Vitae is a personal record

Vitae is designed for one person: its owner.

It is not intended to become a multi-user medical records platform or a healthcare provider system.

This keeps the initial domain model and authorization model deliberately simple.

If multi-person support ever becomes necessary, that should be treated as an explicit architectural change rather than accidentally emerging from the implementation.

---

## 2. History matters

Medical information changes over time.

A new glasses prescription should not replace the previous prescription. A later vaccination should not overwrite an earlier vaccination. A future blood test should remain comparable with previous results.

Therefore, Vitae should generally model medical information as **historical records**.

For example:

```text
Vision
├── Glasses
│   ├── 2024-05-12
│   ├── 2026-07-15
│   └── ...
│
Vaccinations
├── ...
│
Laboratory
├── ...
```

The application should prefer creating a new historical record over mutating an existing record when a real-world medical event has changed.

Corrections to incorrectly entered data are different from real-world changes and should be handled accordingly.

---

## 3. Structured data and source evidence are complementary

Whenever practical, Vitae should store both:

* **structured information** that can be searched, displayed, compared, and analyzed
* **source material** such as photographs, scans, or PDFs

For example:

```text
Glasses prescription
├── Date: 2026-07-15
├── Right eye
│   ├── Sphere
│   ├── Cylinder
│   └── Axis
├── Left eye
│   ├── Sphere
│   ├── Cylinder
│   └── Axis
│
└── Source document
    └── prescription.jpg
```

The structured representation makes the information useful.

The source document provides provenance and allows the original information to be consulted later.

Vitae should not assume that the structured representation is an infallible transcription.

---

## 4. Provenance is first-class data

Important medical information should be traceable to its source where possible.

Records may therefore have associated source information such as:

* source document
* source type
* document date
* provider or institution
* notes
* original filename
* upload date

The exact provenance model may evolve as Vitae grows.

The architectural principle is:

> **Store what the information is and, where possible, where it came from.**

---

## 5. Categories provide the primary organization

Vitae should organize information primarily by medical domain.

Examples:

```text
Vision
Vaccinations
Laboratory
Medications
Conditions
Documents
...
```

Within each domain, records are displayed chronologically.

The user should therefore be able to think in terms of:

> "Show me my glasses history."

rather than:

> "Search through all medical records and find the relevant ones."

A global timeline may be useful later, but category-first navigation is the primary model.

---

## 6. Vitae does not diagnose

Vitae is intentionally not a medical decision system.

It may:

* store information
* organize information
* search information
* display historical information
* compare historical values
* show trends
* calculate simple derived values where appropriate
* associate information with source documents
* eventually import and export information

It must not attempt to:

* diagnose medical conditions
* recommend treatment
* prescribe medication
* make medical decisions
* determine whether a medical result is medically "normal"
* replace a healthcare professional

Future functionality involving AI must respect this boundary.

---

# Initial Scope

## MVP: Glasses / Vision

The first Vitae domain is glasses and vision prescriptions.

The MVP should allow the user to:

* create a glasses prescription
* specify the relevant date
* enter structured prescription values
* distinguish right and left eye
* attach an original photograph or document
* view previous prescriptions
* view prescriptions chronologically
* edit incorrectly entered information
* delete records according to the application's data-retention rules
* access the attached source document

The exact prescription fields should be based on the information actually available from the user's documents.

The model should avoid assuming that every prescription contains every possible optical field.

Potential fields include:

* sphere
* cylinder
* axis
* addition
* prism
* pupillary distance
* prescription date
* optician / provider
* notes

Only fields that are relevant to the actual prescription should be implemented initially.

---

# Future Domains

Vitae is expected to grow as more personal medical information becomes available.

Possible future domains include:

### Vaccinations

Potential information:

* vaccine
* date
* dose
* provider
* batch/lot information where available
* source document
* notes

### Laboratory results

Potential information:

* test
* measurement
* value
* unit
* reference information supplied by the laboratory
* date
* provider/laboratory
* source document

The application should preserve the values provided by the source rather than attempting to independently determine medical meaning.

### Medications

Potential information:

* medication
* dosage
* start date
* end date
* prescription information
* provider
* source document

### Medical conditions

Potential information:

* condition
* diagnosis date
* status
* relevant notes
* source/provider
* supporting documents

### Medical documents

Vitae may eventually provide a general document layer for:

* laboratory reports
* prescriptions
* vaccination records
* doctor's letters
* examination results
* scans
* photographs

These are examples rather than commitments for the initial implementation.

---

# Architecture

Vitae is an independent Atlas service.

```text
Atlas
│
├── Infrastructure
│   ├── Docker
│   ├── Caddy
│   ├── PostgreSQL
│   ├── Prometheus
│   ├── Grafana
│   └── ...
│
├── Constellation
│   └── Social / relationship information
│
└── Vitae
    └── Personal medical information
```

Vitae owns its application logic and data model.

It does not share application tables with Constellation or other services.

---

## Technology

Vitae follows the established Constellation technology stack:

* **Python**
* **Flask**
* **PostgreSQL**
* **Docker**

The choice is intentional.

Using the same stack as Constellation provides:

* reduced operational complexity
* reusable development knowledge
* consistent Atlas services
* easier maintenance
* fewer technologies to operate
* established patterns for Flask, Docker, and PostgreSQL

A different technology should only be introduced when there is a concrete requirement that the established stack cannot satisfy.

---

# Data Storage

## PostgreSQL

Structured medical information is stored in Vitae's dedicated PostgreSQL database.

Vitae receives its own database on the shared Atlas PostgreSQL infrastructure.

The application must never rely on another service's database tables.

Conceptually:

```text
Atlas PostgreSQL
│
├── constellation
│
└── vitae
```

The exact provisioning mechanism is defined by the Atlas infrastructure documentation.

---

## Document storage

Original documents and photographs should not normally be stored directly inside PostgreSQL.

Instead:

```text
PostgreSQL
├── medical records
├── document metadata
└── references to stored files

Persistent file storage
├── photographs
├── PDFs
├── scans
└── other source documents
```

PostgreSQL remains the source of truth for the relationship between a medical record and its documents.

The filesystem/object storage contains the actual binary content.

The document storage abstraction should be designed so that the underlying storage mechanism can be changed later without changing the medical domain model.

---

# Domain Model

Vitae should be domain-oriented rather than based on one generic "medical data" table.

Conceptually:

```text
Vitae
│
├── Vision
│   └── GlassesPrescription
│
├── Vaccinations
│   └── Vaccination
│
├── Laboratory
│   └── BloodTest
│
├── Medications
│   └── Medication
│
├── Conditions
│   └── Condition
│
└── Documents
    └── SourceDocument
```

The actual database schema should be introduced incrementally.

The initial implementation should only create the structures necessary for the glasses domain and shared concepts such as documents/provenance where they are actually needed.

Do **not** create placeholder tables for every possible future medical domain.

---

# Historical Data

A medical record normally represents something that happened in the real world.

For example:

```text
2024-05-12
Glasses prescription

2026-07-15
Glasses prescription
```

Both records should remain.

The application should never treat the newest record as a replacement for historical records unless the real-world domain explicitly requires such behavior.

This enables future functionality such as:

* comparing prescriptions
* viewing historical values
* identifying changes
* displaying trends

Trend functionality should be introduced only when there is enough structured data for it to be useful.

---

# Dates

Medical records can have more than one meaningful date.

For example:

* date the medical event occurred
* date the document was created
* date the information was entered into Vitae
* date a record became effective
* date a record ended

The domain model should distinguish these where the distinction is meaningful.

Do not reduce every medical event to a single generic `created_at` field.

At minimum, Vitae should distinguish between:

* **event/record date**
* **application creation timestamp**

Additional dates should be introduced when the domain requires them.

---

# Data Integrity

Medical information is sensitive and potentially difficult to reconstruct.

The application should favor:

* explicit schemas
* validation
* typed values
* clear units
* explicit dates
* explicit provenance
* historical preservation
* database constraints where appropriate

Avoid storing important structured information solely inside arbitrary JSON fields.

JSON may be useful for genuinely flexible metadata, but it should not replace proper relational modeling of important medical information.

---

# Security and Privacy

Vitae contains highly sensitive personal information.

It must therefore follow the Atlas security standards and should be treated as a more sensitive application than ordinary homelab services.

The application should:

* never log medical information unnecessarily
* never log uploaded document contents
* never expose sensitive information through health endpoints
* keep secrets outside source control
* use secure configuration
* restrict access through the Atlas infrastructure
* protect uploaded files from unintended public access
* validate uploaded files
* avoid trusting user-supplied filenames or paths

Additional authentication or access-control mechanisms may be introduced later if the Atlas platform develops such capabilities.

The architecture should not make such future strengthening difficult.

---

# Medical Data and AI

AI-assisted functionality may become useful in the future, particularly for document transcription or extraction.

For example:

```text
Prescription photo
       │
       ▼
AI-assisted extraction
       │
       ▼
Proposed structured values
       │
       ▼
User confirmation
       │
       ▼
Vitae record
```

AI-generated medical data should **never silently become authoritative data**.

Any future extraction system should clearly distinguish:

* source information
* machine-extracted information
* user-confirmed information

AI functionality is explicitly out of scope for the initial MVP.

---

# FHIR / HL7

Healthcare interoperability standards such as FHIR and HL7 are not part of the initial implementation.

They may become useful in the future if Vitae needs to exchange information with external systems.

The current architecture should therefore avoid deliberately making interoperability impossible, but it should **not introduce FHIR complexity without a concrete use case**.

FHIR support is a future consideration, not an MVP requirement.

---

# API

Vitae should expose a clean application API where appropriate.

The API should follow the same general conventions established by Atlas and Constellation.

The initial API should focus on the actual MVP use cases:

* health check
* glasses prescription creation
* glasses prescription retrieval
* glasses prescription update
* glasses prescription deletion
* historical prescription listing
* source document upload
* source document retrieval

The API should not expose speculative endpoints for future domains.

---

# UI

The user interface should prioritize retrieval and clarity over complexity.

A reasonable initial structure is:

```text
Vitae
│
├── Dashboard
│
├── Vision
│   └── Glasses
│       ├── History
│       ├── Prescription detail
│       └── Add prescription
│
└── Documents
```

As domains are added:

```text
Vitae
│
├── Dashboard
├── Vision
├── Vaccinations
├── Laboratory
├── Medications
├── Conditions
└── Documents
```

The UI should make historical information easy to understand.

---

# Backups

Because Vitae contains irreplaceable personal information, backups are an infrastructure requirement rather than an optional application feature.

Vitae should rely on the Atlas backup strategy for:

* PostgreSQL data
* uploaded documents

The application should not implement its own backup system unless a specific requirement arises.

A backup that contains only the PostgreSQL database but not the associated source documents is incomplete.

---

# Observability

Vitae should integrate with the Atlas monitoring infrastructure.

It should provide:

* `GET /health`
* useful application logs
* appropriate metrics where supported by Atlas conventions

Health and monitoring endpoints must not expose medical information.

Operational telemetry should describe the state of the service, not the contents of the user's medical records.

---

# Project Structure

The exact implementation structure should follow the conventions established by Constellation and the Atlas engineering standards.

A conceptual structure is:

```text
vitae/
├── app/
│   ├── ...
│   ├── domains/
│   │   └── vision/
│   ├── documents/
│   └── ...
│
├── migrations/
├── tests/
├── docs/
│   └── decisions.md
│
├── Dockerfile
├── compose.yaml
├── .env.example
├── README.md
├── CLAUDE.md
└── STANDARDS.md
```

The exact structure should be adapted to the established Constellation patterns rather than imposed unnecessarily.

---

# Development Philosophy

Vitae should follow a **small-first, extensible-later** philosophy.

This means:

### Do

* implement the current use case well
* model real data explicitly
* preserve history
* preserve source documents
* keep domain boundaries clear
* reuse Atlas patterns
* document non-obvious decisions
* leave deliberate extension points

### Do not

* build every possible medical domain up front
* add FHIR without a use case
* add AI without a concrete benefit
* build a generalized medical ontology
* create speculative abstractions
* store all future data in arbitrary JSON
* build diagnostic functionality
* turn Vitae into a medical recommendation system

---

# MVP Definition of Done

The initial Vitae MVP is complete when:

* [ ] Vitae runs as an independent Docker service.
* [ ] Vitae uses its own PostgreSQL database.
* [ ] Vitae follows Atlas infrastructure conventions.
* [ ] `GET /health` is implemented.
* [ ] A glasses prescription can be created.
* [ ] Right and left eye values can be stored.
* [ ] The prescription has a meaningful real-world date.
* [ ] Multiple prescriptions can coexist historically.
* [ ] A prescription can be viewed individually.
* [ ] Historical prescriptions can be listed chronologically.
* [ ] A source photograph/document can be uploaded.
* [ ] A source document is associated with the corresponding record.
* [ ] Uploaded files are stored persistently.
* [ ] Uploaded files cannot be accessed without appropriate application authorization.
* [ ] Medical information is not unnecessarily written to logs.
* [ ] Database migrations are reproducible.
* [ ] Tests cover the important domain behavior.
* [ ] The service follows the Atlas Definition of Done.
* [ ] Backup requirements for both database and documents are understood and satisfied by the Atlas platform.

---

# Future Direction

Vitae should evolve through concrete needs rather than speculative development.

A likely evolution is:

```text
Phase 1
Glasses
│
├── Structured prescription
├── History
└── Source documents

Phase 2
Additional known personal data
│
├── Vaccinations
├── Laboratory results
└── Other concrete needs

Phase 3
Broader medical record
│
├── Medications
├── Conditions
├── Medical encounters
└── Additional documents

Phase 4+
Advanced capabilities
│
├── Search
├── Trends
├── Import/export
├── Document extraction
└── Interoperability
```

These phases are directional rather than commitments.

The architecture should grow because there is a real need to grow it.

---

# Relationship to Atlas

Vitae is one component of the broader Atlas homelab.

The root Atlas repository defines the overarching:

* architecture
* engineering standards
* security expectations
* operational conventions
* deployment model

The Atlas infrastructure repository provides the shared platform on which Vitae runs.

Vitae owns:

* medical domain logic
* medical data schema
* document associations
* Vitae-specific UI/API
* Vitae-specific tests
* Vitae-specific decisions

Constellation and Vitae should remain independent services.

They may eventually communicate through explicit APIs or shared Atlas mechanisms, but they must not directly depend on each other's database schemas.

---

# Related Repositories

* `atlas` — Atlas vision, architecture, and engineering standards
* `atlas-infrastructure` — shared Atlas infrastructure
* `atlas-seedling` — project scaffold/template
* `constellation-relationship-manager` — established Flask/PostgreSQL Atlas service and architectural reference

---

# Final Architectural Principle

The most important rule for Vitae is:

> **Do not optimize for the medical data Vitae has today. Build a small, trustworthy foundation for the medical information Vitae may have tomorrow.**

The first record may only be a glasses prescription.

That is enough.

Vitae becomes valuable by preserving each piece of information, its history, and its source as the personal medical record gradually grows.
