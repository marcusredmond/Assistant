# EKA Document Ingestion Flow - Specification

- **Title:** Engineering Knowledge Assistant (EKA) - Document Ingestion Flow Specification
- **Version:** 0.1.0
- **Status:** Draft
- **Capability:** upload backbone (procedures, standards extracts, project documents) + lessons-learned intake
- **Depends on:** [Information Architecture](../../docs/information-arch/information-architecture.md),
  [content types](../../schemas/content-types/), [term sets](../../schemas/term-sets/term-sets.json)

> **Scope note.** Design artifact only. The sandbox cannot deploy to a Power Platform
> tenant. The accompanying `ingestion-flow.definition.json` is a tenant-neutral
> Power Automate export-style skeleton; connection references and site/library GUIDs are
> placeholders to be bound on import.

---

## 1. Purpose

An automated Power Automate flow that fires when a document is uploaded to an EKA
SharePoint library. It classifies the document, validates and sets its grounding
metadata, routes standards extracts through a licensing gate, and marks the document for
Copilot grounding/indexing. This is the ingestion backbone for the user capabilities
**upload procedures**, **upload standards extracts**, **upload project documents**, and
intake of **lessons learned** (so they are searchable).

## 2. Trigger

| Property | Value |
|---|---|
| Connector | SharePoint |
| Trigger | **When a file is created or modified** (`OnNewFile`) |
| Scope | EKA site; one trigger per ingested library (`StandardsExtracts`, `Procedures`, `ProjectDocuments`, `LessonsLearned`). The `GeneratedDeliverables` library is written by the generators, not ingested here. |
| Concurrency | Serial per item recommended to avoid metadata race conditions. |

## 3. Steps (trigger / action sequence)

1. **Trigger - OnNewFile.** A new/updated file (or list item for `LessonsLearned`)
   arrives in a monitored library.
2. **Get file + current metadata.** Read file properties and the library name.
3. **Detect content type.**
   - Prefer the content type already set on upload.
   - If unset or generic, infer from the source library:
     `StandardsExtracts -> Standards Extract`, `Procedures -> Procedure`,
     `ProjectDocuments -> Project Document`, `LessonsLearned -> Lesson Learned`.
   - Set the content type on the item.
4. **Validate required metadata** (per content type - see
   `schemas/content-types/`):
   - All documents: `Title`, `AssetType`, `DocumentStatus`.
   - `Standards Extract`: additionally `StandardReference`, `LicenceConfirmed`.
   - `Project Document`: additionally `Project`.
   - `Lesson Learned`: `Summary`, `Capability`, `AssetType`, `Project`.
   - If a required field is missing, **do not** silently guess. Set
     `DocumentStatus = Draft`, start an **approval/assignment task** to the uploader to
     supply the missing metadata, and halt grounding until resolved.
5. **Set / normalise `DocumentStatus`.**
   - Newly uploaded source documents (procedures, project documents, standards extracts)
     default to `In Review` unless the uploader marked them `Approved` and holds rights.
   - Lessons learned default to `Approved` for search once required fields are present
     (they are records, not drafts).
6. **Standards-extract licensing gate (OQ-1).**
   - **Branch when content type = `Standards Extract`.**
   - If `LicenceConfirmed = No` (default): set `DocumentStatus = Draft`, write a note that
     the extract is **not groundable pending licensing confirmation (OQ-1)**, skip the
     indexing step, and notify the licensing/records owner. See solution-architecture
     section 8 OQ-1.
   - If `LicenceConfirmed = Yes`: continue to grounding.
   - **Clause/section values are never fabricated.** If `ClauseSectionRef` is empty it is
     left as `[PLACEHOLDER - to be filled from licensed <standard> <clause> rev <year>]`.
7. **Index for Copilot grounding.**
   - For documents that passed validation and (for standards extracts) the licence gate,
     mark the item as grounding-eligible (for example set a `GroundingEligible` flag /
     move to an indexed view, and trigger the Copilot Studio knowledge-source refresh for
     that library).
   - Preserve AS2885 (transmission) vs AS4645 (distribution) separation via `AssetType`
     and `StandardReference` so retrieval stays domain-correct.
8. **Audit + notify.** Write an entry to the generation/ingestion audit trail (reuse the
   `eka_generationrequest`-style audit pattern or a dedicated ingestion log) and notify
   the uploader of the outcome (grounded / pending metadata / pending licence).

## 4. Branch summary

| Content type | Extra validation | Licence gate | Default status | Grounded? |
|---|---|---|---|---|
| Procedure | - | n/a | In Review | Yes (after validation) |
| Project Document | `Project` required | n/a | In Review | Yes (after validation) |
| Standards Extract | `StandardReference`, `LicenceConfirmed` | **Yes (OQ-1)** | Draft until licence confirmed | Only if `LicenceConfirmed = Yes` |
| Lesson Learned | `Summary`, `Capability`, `AssetType`, `Project` | n/a | Approved | Yes (searchable) |

## 5. Error handling

- Missing-metadata and licence-pending paths **stop grounding** and raise a human task;
  they never auto-populate engineering metadata.
- Flow failures write to the audit log with the item reference for retry.

## 6. Engineering review notes (risk lens)

Surfaced for the responsible engineer; these are design cautions, not resolved decisions.

- **Safety / grounding integrity.** The licence gate is the control that stops
  unlicensed or unverified standard text from grounding answers in a safety-critical gas
  T&D domain. Treat `LicenceConfirmed = No` as fail-safe (not groundable). Do not add a
  bypass.
- **Assumption to challenge.** Inferring content type from the source library assumes
  uploads land in the correct library. Mis-filed uploads (for example an AS4645
  distribution extract placed under a transmission project) would mis-tag `AssetType`.
  Keep uploader confirmation of `AssetType` mandatory rather than inferred.
- **Constructability / data-quality risk.** ITP and commissioning generators depend on
  this metadata downstream; weak validation here propagates into generated deliverables.
  Required-field enforcement is deliberately strict for that reason.
- **Commissioning risk.** Commissioning procedures grounded on an `In Review` (not yet
  `Approved`) source could carry unverified steps; retrieval should prefer `Approved`
  sources and flag reliance on `In Review` content.
- **Emergency-response implication.** Field/emergency queries must trace to the correct
  asset type and the current revision; `Superseded` documents must be excluded from
  grounding so responders are not served withdrawn procedures.
- **Standards to review (labels only, no fabricated clauses).** For transmission intake:
  AS 2885 series; for distribution intake: AS/NZS 4645 series; welding content: the
  applicable welding standard recorded under `Standard Reference = Other`. Actual clauses
  come only from the licensed source.
