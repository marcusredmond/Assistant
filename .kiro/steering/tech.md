---
inclusion: always
---

# Technology Stack

## Platform

Built on the **Microsoft Power Platform** with an Autodesk integration. This is a
low-code / configuration-first stack, not a traditional application codebase.
Artifacts are solutions, flows, agents, and schemas — not compiled binaries.

| Component | Role in this system |
|---|---|
| **SharePoint** | System of record for documents: standards, procedures, templates, ITPs, risk assessments. Provides the content library, metadata/content types, and the grounding source for AI. |
| **Power Apps** | User-facing applications. Canvas apps for task/form-driven and mobile/tablet use; model-driven apps for structured data-heavy workflows. |
| **Power Automate** | Workflow and orchestration — approvals, document generation, notifications, system-to-system integration. |
| **Microsoft Copilot / Copilot Studio** | Conversational, document-grounded assistant. Topics/agents grounded on SharePoint content with citations. |
| **Autodesk Inventor** | Desktop CAD source for engineering model data (BOM, parameters, drawing metadata). Integrated via export/connector, not natively part of Power Platform. |

## Architectural implications

- **Grounding over generation.** Copilot answers are grounded on SharePoint
  content with citations. Dataverse or SharePoint lists hold structured data.
- **Document generation.** ITPs, procedures, and risk assessments are generated
  from templates (Word/SharePoint templates populated via Power Automate or
  Office scripts), keeping output consistent and reviewable.
- **Inventor bridge.** Inventor is desktop software; expect an export step
  (e.g. Inventor iLogic/API → structured file → SharePoint/Dataverse) rather
  than a live Power Platform connection.

## This sandbox vs. the target tenant

This development sandbox is a **Linux/web environment with Git & GitHub**. It
**cannot deploy to a Power Platform tenant**. Useful artifacts to produce here:

- **Design & architecture documents** (solution design, information architecture).
- **Schema definitions** — SharePoint content types, metadata columns, Dataverse
  table designs.
- **Flow / agent specifications** — Power Automate flow definitions and Copilot
  Studio topic designs expressed as spec or exportable config.
- **Logic prototypes** — e.g. an ITP or risk-assessment generator prototyped in a
  scriptable language to validate the rules before implementing in low-code.
- **Templates** — Word/markdown templates for generated deliverables.

Keep deployable Power Platform assets as declarative definitions (JSON/YAML/XML
solution components) that can be imported into the tenant.
