# Engineering Knowledge Assistant (EKA)

- **Title:** Engineering Knowledge Assistant (EKA) - Repository Index
- **Version:** 0.1.0
- **Status:** Draft

An **engineering knowledge assistant** for gas transmission and distribution (T&D) assets.
It helps engineers get grounded, standards-compliant answers and generate engineering
deliverables, built on the **Microsoft Power Platform** with **SharePoint as the document
repository / system of record** and an **Autodesk Inventor** export bridge.

> **Sandbox note.** This is a config / design-first project. The sandbox is a Linux / web
> environment and **cannot deploy to a Power Platform tenant**. Every artifact here is
> declarative / design-only: design docs, declarative schema / flow / agent definitions,
> deliverable templates, and a Python-stdlib logic prototype. Deployable Power Platform
> assets are kept as tenant-neutral declarative definitions to be imported into the target
> tenant by qualified makers and reviewed by qualified engineers.

---

## What it does

The system serves these user capabilities (from the request):

- Ask engineering questions
- Upload procedures
- Upload standards extracts
- Upload project documents
- Search historical lessons learned
- Generate technical queries
- Generate ITPs
- Generate commissioning procedures

It is a **program of composable modules** across nine capability areas (`as2885`, `as4645`,
`commissioning`, `welding`, `itp`, `design-review`, `construction`, `risk-assessment`,
`tech-query`). See the [program roadmap](docs/architecture/program-roadmap.md) for the full
sequencing, what is delivered, and what remains.

---

## Repository layout

```
/
├── docs/          Architecture & design documentation
├── schemas/       SharePoint content types, term sets, Dataverse tables (declarative)
├── flows/         Power Automate flow specs + tenant-neutral definitions
├── agents/        Copilot Studio agent & topic designs
├── templates/     Deliverable templates (ITP, commissioning, technical query)
├── prototypes/    Logic prototypes validating rules before low-code
└── .kiro/         Steering documents (product, tech, structure)
```

---

## Artifact index

### Docs (`docs/`)

| Document | Purpose |
|---|---|
| [docs/README.md](docs/README.md) | Design-documentation index. |
| [docs/architecture/solution-architecture.md](docs/architecture/solution-architecture.md) | Solution architecture: components, data flow, grounding model, capability mapping, open questions. |
| [docs/architecture/program-roadmap.md](docs/architecture/program-roadmap.md) | Program roadmap: all nine capability areas sequenced, delivered vs remaining, OQ-1 / OQ-2 preconditions. |
| [docs/architecture/README.md](docs/architecture/README.md) | Architecture index. |
| [docs/information-arch/information-architecture.md](docs/information-arch/information-architecture.md) | SharePoint libraries, taxonomy / term sets, content types, metadata columns. |
| [docs/information-arch/README.md](docs/information-arch/README.md) | Information-architecture index. |
| [docs/modules/tech-query-design.md](docs/modules/tech-query-design.md) | `tech-query` module design (grounded Q&A, lessons-learned search, technical-query generation). |
| [docs/modules/itp-design.md](docs/modules/itp-design.md) | `itp` module design (ITP generation). |
| [docs/modules/commissioning-design.md](docs/modules/commissioning-design.md) | `commissioning` module design (commissioning-procedure generation). |

### Schemas (`schemas/`)

| Artifact | Purpose |
|---|---|
| [schemas/content-types/README.md](schemas/content-types/README.md) | Content-types index. |
| [schemas/content-types/base-engineering-document.json](schemas/content-types/base-engineering-document.json) | Base engineering document content type. |
| [schemas/content-types/procedure.json](schemas/content-types/procedure.json) | Procedure content type (upload procedures). |
| [schemas/content-types/standard-extract.json](schemas/content-types/standard-extract.json) | Standards Extract content type (upload standards extracts; OQ-1 licence gate). |
| [schemas/content-types/project-document.json](schemas/content-types/project-document.json) | Project Document content type (upload project documents). |
| [schemas/content-types/lesson-learned.json](schemas/content-types/lesson-learned.json) | Lesson Learned content type (search lessons learned). |
| [schemas/content-types/generated-deliverable.json](schemas/content-types/generated-deliverable.json) | Base Generated Deliverable content type (carries the DRAFT marker). |
| [schemas/content-types/generated-deliverable-technical-query.json](schemas/content-types/generated-deliverable-technical-query.json) | Technical Query deliverable subtype. |
| [schemas/content-types/generated-deliverable-itp.json](schemas/content-types/generated-deliverable-itp.json) | ITP deliverable subtype. |
| [schemas/content-types/generated-deliverable-commissioning-procedure.json](schemas/content-types/generated-deliverable-commissioning-procedure.json) | Commissioning Procedure deliverable subtype. |
| [schemas/term-sets/term-sets.json](schemas/term-sets/term-sets.json) | Managed-metadata term sets (capability, asset type, status, etc.). |
| [schemas/dataverse/README.md](schemas/dataverse/README.md) | Dataverse tables index. |
| [schemas/dataverse/itp-register.json](schemas/dataverse/itp-register.json) | ITP register (header + line items). |
| [schemas/dataverse/technical-query-register.json](schemas/dataverse/technical-query-register.json) | Technical query register. |
| [schemas/dataverse/generation-audit.json](schemas/dataverse/generation-audit.json) | Generation / ingestion audit trail. |

### Flows (`flows/`)

| Artifact | Purpose |
|---|---|
| [flows/ingestion/ingestion-flow-spec.md](flows/ingestion/ingestion-flow-spec.md) | Document ingestion & classification flow spec (upload backbone). |
| [flows/ingestion/ingestion-flow.definition.json](flows/ingestion/ingestion-flow.definition.json) | Ingestion flow tenant-neutral definition. |
| [flows/itp/itp-generation-flow-spec.md](flows/itp/itp-generation-flow-spec.md) | ITP generation flow spec. |
| [flows/itp/itp-generation-flow.definition.json](flows/itp/itp-generation-flow.definition.json) | ITP generation flow tenant-neutral definition. |
| [flows/commissioning/commissioning-generation-flow-spec.md](flows/commissioning/commissioning-generation-flow-spec.md) | Commissioning procedure generation flow spec. |
| [flows/commissioning/commissioning-generation-flow.definition.json](flows/commissioning/commissioning-generation-flow.definition.json) | Commissioning generation flow tenant-neutral definition. |

### Agents (`agents/`)

| Artifact | Purpose |
|---|---|
| [agents/tech-query/agent-design.md](agents/tech-query/agent-design.md) | `tech-query` Copilot Studio agent design (grounding + citation contract). |
| [agents/tech-query/topics/ask-engineering-question.json](agents/tech-query/topics/ask-engineering-question.json) | Topic: ask engineering question. |
| [agents/tech-query/topics/search-lessons-learned.json](agents/tech-query/topics/search-lessons-learned.json) | Topic: search historical lessons learned. |
| [agents/tech-query/topics/generate-technical-query.json](agents/tech-query/topics/generate-technical-query.json) | Topic: generate technical query. |

### Templates (`templates/`)

| Artifact | Purpose |
|---|---|
| [templates/tech-query/technical-query-template.md](templates/tech-query/technical-query-template.md) | Technical query deliverable template (carries the DRAFT marker). |
| [templates/itp/itp-template.md](templates/itp/itp-template.md) | ITP deliverable template (carries the DRAFT marker). |
| [templates/commissioning/commissioning-procedure-template.md](templates/commissioning/commissioning-procedure-template.md) | Commissioning procedure deliverable template (carries the DRAFT marker). |

### Prototypes (`prototypes/`)

| Artifact | Purpose |
|---|---|
| [prototypes/itp/itp_generator.py](prototypes/itp/itp_generator.py) | Python-stdlib ITP generation logic prototype (validates rules before low-code). |
| [prototypes/itp/test_itp_generator.py](prototypes/itp/test_itp_generator.py) | Unit tests for the ITP generator. |
| [prototypes/itp/sample-activities.json](prototypes/itp/sample-activities.json) | Sample activity list input. |
| [prototypes/itp/README.md](prototypes/itp/README.md) | Prototype usage notes. |

---

## Key conventions

These conventions apply across every artifact (from the project steering):

- **Grounded, not generative-from-memory.** Every compliance or standards answer must trace
  to a source document (clause, section, revision). The assistant cites its sources via the
  [citation contract](docs/modules/tech-query-design.md#5-citation-contract); it never
  invents clause numbers or requirements.
- **Domain accuracy (safety-critical).** Clause numbers, acceptance criteria, and
  requirements from AS2885 / AS/NZS 4645 (or any standard) are **never fabricated**. Where
  source text is unavailable, a clearly-marked placeholder is used:
  `[PLACEHOLDER - to be filled from licensed <standard> <clause> rev <year>]`.
- **AS2885 (transmission) and AS/NZS 4645 (distribution) are kept distinct** in scope,
  taxonomy, grounding, and generation. They are never blended.
- **Human-in-the-loop.** The assistant drafts and advises; a qualified engineer reviews and
  signs off. Every generated deliverable (technical query, ITP, commissioning procedure,
  and future risk assessments) carries the visible **"DRAFT — pending engineering review"**
  marker until sign-off.
- **Status headers.** Every design doc states its status: Draft / In Review / Approved.
- **Declarative / design-only.** Power Platform assets are tenant-neutral declarative
  definitions; the sandbox cannot deploy to a tenant.

## Open questions (resolve before the dependent module)

- **OQ-1 Standards licensing** - hard precondition for grounding on AS2885 / AS4645 / welding
  standard **text**. See the [program roadmap](docs/architecture/program-roadmap.md#2-hard-preconditions-open-questions).
- **OQ-2 Inventor integration scope** - precondition for any module needing model / BOM data.
- **OQ-3 First-module selection** - `tech-query` recommended first; team to confirm.
