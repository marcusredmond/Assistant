---
inclusion: always
---

# Project Structure & Conventions

## Repository layout

The workspace root is `/projects/sandbox`. Organise work by capability module and
artifact type, since this is a config/design-first project rather than a single
app codebase.

```
/projects/sandbox
├── docs/                     # Architecture & design documentation
│   ├── architecture/         # Solution architecture, data flow, integration
│   ├── information-arch/     # SharePoint content types, metadata, taxonomy
│   └── modules/              # Per-capability design docs (as2885, itp, etc.)
├── schemas/                  # SharePoint content types, Dataverse tables (declarative)
├── flows/                    # Power Automate flow definitions / specs
├── agents/                   # Copilot Studio topic & agent designs
├── templates/                # Deliverable templates (ITP, risk assessment, procedures)
├── prototypes/               # Logic prototypes validating rules before low-code
└── .kiro/steering/           # These steering documents
```

Create directories as modules are started; don't scaffold empty folders ahead of need.

## Naming

- Use the capability shorthand consistently: `as2885`, `as4645`, `commissioning`,
  `welding`, `itp`, `design-review`, `construction`, `risk-assessment`, `tech-query`.
- Standards references use the official form: `AS 2885.1`, `AS/NZS 4645.1`, with
  clause numbers when citing (e.g. `AS 2885.1 Clause 5.3`).
- Files kebab-case; documents include a title, version, and status header.

## Documentation conventions

- Every design doc states its **status**: Draft / In Review / Approved.
- Compliance content **cites the source** (standard, clause/section, revision/year).
- Generated-deliverable templates carry a visible **"DRAFT — pending engineering
  review"** marker until signed off.
- Prefer tables for requirement/clause mappings and ITP line items.

## Domain accuracy rules

- Do **not** invent or paraphrase clause numbers, acceptance criteria, or
  requirements from AS2885/AS4645 or other standards. If the source text isn't
  available in the workspace, say so and leave a placeholder to be filled from the
  licensed document — never fabricate.
- Keep AS2885 (transmission pipelines) and AS4645 (distribution networks)
  distinct; their scope and requirements differ.
- Treat all generated engineering deliverables as drafts requiring qualified
  engineer review and sign-off.

## Working in this sandbox

- Produce declarative, importable artifacts for Power Platform assets.
- Git/GitHub are available; push branches and open PRs for review. The user
  reviews files on GitHub or via the read-only file explorer — they have no IDE.
