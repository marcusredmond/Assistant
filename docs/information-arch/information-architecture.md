# Engineering Knowledge Assistant - Information Architecture

- **Title:** Engineering Knowledge Assistant (EKA) - SharePoint Information Architecture
- **Version:** 0.1.0
- **Status:** Draft
- **Last updated:** 2025 (foundation feature FEAT-001)
- **Audience:** SharePoint information architects, Power Platform makers, engineering leads
- **Depends on / informs:** [Solution Architecture](../architecture/solution-architecture.md)

> **Scope note.** Design artifact only. The sandbox cannot deploy to a Power Platform
> tenant; the structures below are declarative designs for implementation in the target
> tenant. Metadata and content types defined here are the grounding and retrieval
> backbone referenced by the solution architecture's §4 Grounding model.

---

## 1. Design goals

1. **Groundable** - every document carries enough metadata (domain, discipline, asset
   type, standard reference, revision) for Copilot to retrieve and cite it accurately.
2. **Distinct standards** - AS2885 (**transmission** pipelines) and AS4645
   (**distribution** networks) remain separate across taxonomy, filing, and retrieval.
3. **Searchable lessons** - historical lessons learned are findable by capability, asset
   type, and project.
4. **Reviewable deliverables** - generated outputs are drafts with a tracked status.

---

## 2. Site & library structure

A single EKA SharePoint site (or hub) hosts one **document library per content domain**.
Separating libraries keeps content types, retention, and permissions clean and makes
Copilot grounding scopes explicit.

| Library (internal name) | Purpose | Primary content type | Grounds Q&A? | Notes |
|---|---|---|---|---|
| `StandardsExtracts` | Licensed standards extracts (AS2885, AS4645, welding, etc.) | Standards Extract | Yes (subject to **OQ-1 licensing**) | Access-restricted per licensing; see solution-architecture §8 OQ-1. |
| `Procedures` | Approved engineering procedures | Procedure | Yes | Upload target for "upload procedures". |
| `ProjectDocuments` | Project-specific documents, incl. Inventor exports | Project Document | Yes | Upload target for "upload project documents"; receives Inventor bridge output. |
| `LessonsLearned` | Historical lessons learned register | Lesson Learned | Yes | See §5. May be a list + attachment rather than a library (both patterns described). |
| `GeneratedDeliverables` | Draft/approved generated outputs (technical queries, ITPs, commissioning procedures) | Generated Deliverable (+ subtypes) | Optional | Human-in-the-loop review target; carries DRAFT marker until signed off. |

Structured records (ITP line items, technical-query register, generation audit trail)
live in **Dataverse or SharePoint lists**, not document libraries (see
solution-architecture §4).

---

## 3. Managed-metadata taxonomy (term sets)

Managed metadata (term store) drives consistent tagging, filtering, and grounding.
Term sets below are the governing taxonomy. Term labels use the capability shorthand
where applicable.

### 3.1 Term set: `Asset Type`

Keeps transmission and distribution **distinct**.

| Term | Meaning |
|---|---|
| `Transmission` | Transmission pipeline systems (AS2885 domain). |
| `Distribution` | Distribution gas networks (AS4645 domain). |
| `Not asset-specific` | Content not tied to a single asset type. |

### 3.2 Term set: `Discipline`

| Term | Meaning |
|---|---|
| `Pipeline` | Pipeline engineering. |
| `Mechanical` | Mechanical/rotating. |
| `Welding` | Welding & NDT. |
| `Civil` | Civil/structural. |
| `Instrumentation & Control` | I&C / SCADA. |
| `Integrity` | Integrity / risk. |
| `Commissioning` | Commissioning. |

> Extend as needed; keep labels stable because they are cited in grounding.

### 3.3 Term set: `Capability`

Maps to the nine capability-area shorthands used across the program.

| Term (shorthand) | Capability area |
|---|---|
| `as2885` | AS2885 compliance (transmission) |
| `as4645` | AS4645 compliance (distribution) |
| `commissioning` | Commissioning procedures |
| `welding` | Welding requirements |
| `itp` | ITP generation |
| `design-review` | Design reviews |
| `construction` | Construction support |
| `risk-assessment` | Risk assessments |
| `tech-query` | Technical queries |

### 3.4 Term set: `Document Status`

Drives the human-in-the-loop review lifecycle.

| Term | Meaning |
|---|---|
| `Draft` | Working draft / newly generated (DRAFT — pending engineering review). |
| `In Review` | Submitted for engineering review. |
| `Approved` | Reviewed and signed off by a qualified engineer. |
| `Superseded` | Replaced by a newer revision. |

### 3.5 Term set: `Standard Reference`

Identifies the governing standard **without encoding its text or clause content**.

| Term | Meaning |
|---|---|
| `AS 2885.1` | Transmission pipelines - part 1 (reference label only). |
| `AS 2885.2` | Transmission pipelines - part 2 (reference label only). |
| `AS 2885.3` | Transmission pipelines - part 3 (reference label only). |
| `AS/NZS 4645.1` | Distribution networks - part 1 (reference label only). |
| `AS/NZS 4645.2` | Distribution networks - part 2 (reference label only). |
| `AS/NZS 4645.3` | Distribution networks - part 3 (reference label only). |
| `Other` | Any other referenced standard (free term, label only). |

> **Domain-accuracy guard.** These are **reference labels only**. Clause numbers,
> acceptance criteria, and requirements are **never** stored as fabricated taxonomy
> values. Actual clause/section text and numbers come only from a licensed source
> document in `StandardsExtracts` (subject to OQ-1) and are entered as
> `[PLACEHOLDER - to be filled from licensed <standard> <clause> rev <year>]` until that
> source is available.

---

## 4. Content types & metadata columns

Each content type inherits from Document (or Item for list-based) and adds columns used
for grounding and retrieval. Columns typed `Managed metadata` bind to the term sets in §3.

### 4.1 Base columns (shared by all document content types)

| Column | Type | Required | Source term set | Purpose |
|---|---|---|---|---|
| `Title` | Text | Yes | n/a | Human-readable title. |
| `AssetType` | Managed metadata | Yes | `Asset Type` (§3.1) | Transmission vs distribution separation. |
| `Discipline` | Managed metadata | No | `Discipline` (§3.2) | Discipline filtering. |
| `Capability` | Managed metadata | No | `Capability` (§3.3) | Routes/retrieves by capability. |
| `DocumentStatus` | Managed metadata | Yes | `Document Status` (§3.4) | Review lifecycle. |
| `StandardReference` | Managed metadata (multi) | No | `Standard Reference` (§3.5) | Which standard(s) govern this doc (label only). |
| `Revision` | Text | No | n/a | Document revision/year as stated by the source. |
| `Project` | Text / lookup | No | n/a | Project identifier for project-scoped filtering. |
| `SourceCitation` | Text | No | n/a | Canonical citation string the assistant surfaces (clause/section/revision **only when present in the source**). |

### 4.2 `Standards Extract` content type

| Column | Type | Required | Purpose |
|---|---|---|---|
| *(base columns)* | n/a | n/a | See §4.1. `StandardReference` required here. |
| `StandardReference` | Managed metadata (multi) | **Yes** | The standard this extract belongs to. |
| `ClauseSectionRef` | Text | No | Clause/section identifier **as printed in the licensed source only**; otherwise `[PLACEHOLDER - to be filled from licensed <standard> <clause> rev <year>]`. |
| `LicenceConfirmed` | Yes/No | Yes | Gate tied to OQ-1; `No` means not groundable. |

### 4.3 `Procedure` content type

| Column | Type | Required | Purpose |
|---|---|---|---|
| *(base columns)* | n/a | n/a | See §4.1. |
| `ProcedureType` | Choice | No | e.g. Commissioning, Construction, Welding, General. |
| `Owner` | Person | No | Document owner. |
| `EffectiveDate` | Date | No | When the procedure takes effect. |

### 4.4 `Project Document` content type

| Column | Type | Required | Purpose |
|---|---|---|---|
| *(base columns)* | n/a | n/a | See §4.1. `Project` required here. |
| `Project` | Text / lookup | **Yes** | Project scoping. |
| `DocumentKind` | Choice | No | Drawing, BOM, calc, correspondence, Inventor export, etc. |
| `InventorExport` | Yes/No | No | Flags CAD-derived content from the Inventor bridge (OQ-2). |

### 4.5 `Generated Deliverable` content type (and subtypes)

Parent content type for generated outputs; subtypes `Technical Query`, `ITP`,
`Commissioning Procedure` inherit it.

| Column | Type | Required | Purpose |
|---|---|---|---|
| *(base columns)* | n/a | n/a | See §4.1. `DocumentStatus` defaults to `Draft`. |
| `DeliverableType` | Choice | Yes | technical-query / itp / commissioning-procedure. |
| `DraftMarker` | Text (calculated/default) | Yes | Must read **"DRAFT — pending engineering review"** until approved. |
| `GeneratedBy` | Text | No | Generator/module that produced it (`tech-query`, `itp`, `commissioning`). |
| `SourceDocuments` | Hyperlink/lookup (multi) | No | Links to the grounding sources used (traceability). |
| `ReviewedBy` | Person | No | Qualified engineer who signed off. |

---

## 5. Lessons learned

Satisfies the user capability **"search historical lessons learned."**

**Storage pattern.** A dedicated `LessonsLearned` **SharePoint list** (preferred for
structured, searchable records) with an optional attached document, backed by a
`Lesson Learned` content type. A document library is an acceptable alternative when
lessons are long-form documents; the content type and columns are the same either way.

### 5.1 `Lesson Learned` content type columns

| Column | Type | Required | Source term set | Purpose |
|---|---|---|---|---|
| `Title` | Text | Yes | n/a | Short lesson title. |
| `Summary` | Multi-line text | Yes | n/a | What happened / what was learned. |
| `Capability` | Managed metadata (multi) | Yes | `Capability` (§3.3) | Search by capability area. |
| `AssetType` | Managed metadata | Yes | `Asset Type` (§3.1) | Search transmission vs distribution. |
| `Project` | Text / lookup | Yes | n/a | Search by originating project. |
| `Discipline` | Managed metadata | No | `Discipline` (§3.2) | Discipline filtering. |
| `DateCaptured` | Date | No | n/a | When the lesson was recorded. |
| `RelatedDocuments` | Hyperlink/lookup (multi) | No | n/a | Links to supporting evidence. |

### 5.2 Searchability

- Lessons are **retrievable by capability, asset type, and project** via the required
  managed-metadata and lookup columns above.
- The canvas app's "search historical lessons learned" screen filters on these columns;
  Copilot can also ground on lessons for "ask engineering questions."
- Keeping `AssetType` on every lesson preserves the AS2885 (transmission) /
  AS4645 (distribution) distinction in search results.

---

## 6. Open questions affecting the IA

| Ref | Open question | IA impact |
|---|---|---|
| OQ-1 | Standards licensing | `StandardsExtracts` grounding is gated by `LicenceConfirmed`; clause/section values stay as placeholders until a licensed source exists. |
| OQ-2 | Inventor integration scope | `InventorExport` flag and `ProjectDocuments` columns anticipate CAD-derived content; exact fields depend on the resolved extraction scope. |

See [Solution Architecture §8](../architecture/solution-architecture.md#8-assumptions-risks--open-questions)
for full detail. These are not resolved here.
