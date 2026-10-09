# Technical Query & Document-Grounded Q&A - Module Design

- **Title:** Engineering Knowledge Assistant (EKA) - `tech-query` Module Design (document-grounded Q&A, lessons-learned search, technical-query generation)
- **Version:** 0.1.0
- **Status:** Draft
- **Capability:** `tech-query` (recommended first end-to-end module)
- **Depends on:** [Solution Architecture](../architecture/solution-architecture.md),
  [Information Architecture](../information-arch/information-architecture.md),
  [Ingestion Flow Spec](../../flows/ingestion/ingestion-flow-spec.md),
  [Technical Query register](../../schemas/dataverse/technical-query-register.json),
  [Technical Query content type](../../schemas/content-types/generated-deliverable-technical-query.json),
  [Lesson Learned content type](../../schemas/content-types/lesson-learned.json)
- **Implemented by:** [Copilot agent design](../../agents/tech-query/agent-design.md),
  [topic designs](../../agents/tech-query/topics/),
  [technical-query template](../../templates/tech-query/technical-query-template.md)

> **Scope note.** Design artifact only. The sandbox cannot deploy to a Power Platform
> tenant. The Copilot Studio agent, topics, and template referenced here are declarative,
> tenant-neutral designs for implementation in the target tenant by qualified makers and
> reviewed by qualified engineers.

---

## 1. Why this is the first module

Per [solution-architecture section 8.1](../architecture/solution-architecture.md#81-recommended-first-module-recommendation-not-a-decision),
document-grounded Q&A (`tech-query`) is the recommended first end-to-end module. It:

- exercises the whole foundation (ingestion -> SharePoint information architecture ->
  Copilot grounding + citations) that every later module reuses;
- delivers value **without** depending on the standards-licensing open question
  (OQ-1): it can ground on uploaded procedures, project documents, and lessons learned
  immediately, and add standards grounding only once OQ-1 is confirmed;
- validates the human-in-the-loop review path through the technical-query generator.

> The first-module choice (OQ-3) remains a team decision; this module is designed so the
> team can commit to it with the dependencies made explicit.

---

## 2. Scope

**In scope**

| Capability (from the request) | How this module serves it |
|---|---|
| Ask engineering questions | Copilot Studio grounded Q&A with mandatory citations (topic `ask-engineering-question`). |
| Search historical lessons learned | Query the `LessonsLearned` list/library filtered by capability, asset type, project (topic `search-lessons-learned`). |
| Generate technical queries | Collect fields and produce a draft Technical Query record + deliverable (topic `generate-technical-query` + [template](../../templates/tech-query/technical-query-template.md)). |

**Out of scope (other modules)**

- Generating ITPs (`itp`) and commissioning procedures (`commissioning`).
- Uploading/classifying documents - handled by the [ingestion flow](../../flows/ingestion/ingestion-flow-spec.md); this module **consumes** what ingestion files and tags.
- Resolving OQ-1 (standards licensing) and OQ-2 (Inventor scope). This module flags them and degrades gracefully.

---

## 3. Grounding sources

The agent grounds **only** on SharePoint content prepared by the ingestion flow and
marked grounding-eligible. Sources map to the libraries and content types in the
information architecture.

| Grounding source (library) | Content type | Used by | Notes |
|---|---|---|---|
| `Procedures` | Procedure | ask-engineering-question | Approved procedures preferred; reliance on `In Review` is flagged. |
| `ProjectDocuments` | Project Document | ask-engineering-question | Project-scoped; may include Inventor exports (OQ-2). |
| `LessonsLearned` | Lesson Learned | ask-engineering-question, search-lessons-learned | List-based; searchable by capability/asset type/project. |
| `StandardsExtracts` | Standards Extract | ask-engineering-question | **Gated by OQ-1.** Only `LicenceConfirmed = Yes` extracts are groundable; otherwise excluded and the agent says so. |
| `GeneratedDeliverables` | Generated Deliverable (+ subtypes) | ask-engineering-question (optional) | Approved deliverables only; drafts are not authoritative. |

**Retrieval rules carried into the agent (see [agent-design.md](../../agents/tech-query/agent-design.md)):**

- Prefer `Approved` sources; exclude `Superseded`; flag any reliance on `In Review`.
- Keep AS2885 (**transmission**) and AS/NZS 4645 (**distribution**) distinct by filtering
  on `AssetType` / `StandardReference`; never blend the two in one answer.
- Standards extracts are groundable only when `LicenceConfirmed = Yes` (OQ-1).

---

## 4. User journeys

### 4.1 Ask a question, get a grounded answer with citations

1. Engineer asks a question in the canvas app / Teams.
2. Agent retrieves relevant grounding passages (section 3) honouring the retrieval rules.
3. Agent answers **only** from retrieved content and returns a citation for each claim
   (section 5).
4. If retrieval is empty, weak, or spans conflicting asset types, the agent states
   uncertainty and defers (section 6) rather than guessing.

### 4.2 Search historical lessons learned

1. Engineer supplies any of: capability, asset type, project, free-text keywords.
2. Agent queries the `LessonsLearned` list filtered on the managed-metadata/lookup
   columns.
3. Agent returns tagged results (title, summary, capability, asset type, project, date,
   related-document links). `AssetType` on every result preserves the
   transmission/distribution distinction.

### 4.3 Raise / generate a formal technical query record

1. Engineer provides question, project, discipline, asset type, optional standard
   reference and supporting context.
2. Agent attempts a grounded draft response with citations (reusing 4.1).
3. Agent writes a **draft** Technical Query record to the register
   ([`eka_technicalquery`](../../schemas/dataverse/technical-query-register.json),
   status `Draft`) and produces a deliverable from the
   [template](../../templates/tech-query/technical-query-template.md) carrying the
   **"DRAFT — pending engineering review"** marker.
4. The draft is routed for qualified-engineer review and close-out; the engineer, not the
   assistant, decides.

---

## 5. Citation contract

Every answer that makes an engineering claim **must** cite its source. This is a hard
requirement, enforced in the agent instructions.

- A citation identifies the **source document** and, **where the source provides it**,
  the **standard + clause/section + revision/year**.
- Two valid citation shapes:
  1. **Standards-backed:** `<Standard Reference> <Clause/Section> (rev <year>)` plus the
     source extract document, e.g. `AS 2885.1 Clause X.Y (rev <year>) - StandardsExtracts/<doc>`.
     The clause/section and revision are reproduced **only** when printed in the licensed
     source; otherwise the agent does not state a clause number.
  2. **Document-backed:** `<source document title> - <section/heading>` for procedures,
     project documents, or lessons learned that are not standards.
- **Grounded, not generative.** The agent **never invents or paraphrases** clause
  numbers, acceptance criteria, or requirements. If the governing clause text is not in a
  groundable source, the agent says the source is unavailable (and, for standards,
  references OQ-1) and leaves `[PLACEHOLDER - to be filled from licensed <standard> <clause> rev <year>]`.
- Citations populate `eka_sourcecitations` on the TQ register and `SourceDocuments` on the
  deliverable for traceability.

| Answer contains | Citation requirement |
|---|---|
| A standards requirement | Standards-backed citation; clause/revision only if present in a licensed, `LicenceConfirmed = Yes` source. |
| Guidance from a procedure / project doc | Document-backed citation (title + section). |
| A lesson learned | Lesson title + project + capability tag. |
| No groundable source found | **No answer invented** - state uncertainty and defer (section 6). |

---

## 6. Uncertainty behaviour

Gas T&D is safety-critical. When the agent cannot ground an answer confidently it must
**state uncertainty and defer to the authoritative document and the responsible
engineer** rather than guessing. Specifically, the agent:

- says plainly when retrieval found nothing relevant, or only `In Review` / `Superseded`
  / conflicting sources;
- never fills the gap with memory-based or paraphrased standard content;
- names the authoritative document to consult and recommends the responsible engineer
  make the call;
- for standards gaps caused by licensing, references OQ-1 and the placeholder convention;
- flags when a question appears to mix transmission and distribution so the engineer can
  disambiguate asset type.

---

## 7. Data & artifact mapping

| Journey | Reads | Writes | Artifact |
|---|---|---|---|
| Ask a question | grounding libraries (section 3) | nothing | [`ask-engineering-question.json`](../../agents/tech-query/topics/ask-engineering-question.json) |
| Search lessons | `LessonsLearned` list | nothing | [`search-lessons-learned.json`](../../agents/tech-query/topics/search-lessons-learned.json) |
| Generate TQ | grounding libraries + user inputs | `eka_technicalquery` (Draft) + `GeneratedDeliverables` deliverable | [`generate-technical-query.json`](../../agents/tech-query/topics/generate-technical-query.json), [template](../../templates/tech-query/technical-query-template.md) |

---

## 8. Open-question dependencies

| Ref | Dependency | Effect on this module |
|---|---|---|
| OQ-1 | Standards licensing | **Precondition** for grounding on AS2885/AS4645 (and other standard) **text**. Until confirmed, standards extracts are excluded from grounding; document-grounded Q&A on procedures, project documents, and lessons learned proceeds unaffected. |
| OQ-2 | Inventor integration scope | Affects CAD-derived grounding in `ProjectDocuments`; does not block document-grounded Q&A. |
| OQ-3 | First-module selection | This module is the recommended choice; team confirmation recorded before build. |

---

## 9. Engineering review notes (risk lens)

Written from a senior pipeline engineer's perspective. These are design cautions to
challenge during review, not resolved decisions. They are kept consistent with the same
section in the [ingestion flow spec](../../flows/ingestion/ingestion-flow-spec.md#6-engineering-review-notes-risk-lens).

- **Assumption to challenge: "a grounded answer is a correct answer."** Grounding
  guarantees traceability to a source, not that the source is current, approved, or
  applicable to this asset. The agent must prefer `Approved` sources, exclude
  `Superseded`, and visibly flag any reliance on `In Review` content so the engineer
  weighs it. Retrieval confidence is not engineering judgement.
- **Safety / grounding integrity.** Grounding on `Superseded` or `In Review` sources in a
  safety-critical gas T&D domain can surface a withdrawn procedure or an unverified draft
  as if authoritative. Treat the status filter as a safety control: fail safe to "no
  confident answer" rather than serving stale content. Do not add a bypass that answers
  from model memory when retrieval is empty.
- **Mis-attributed AS2885-vs-AS4645 risk.** Transmission (AS 2885) and distribution
  (AS/NZS 4645) requirements differ; a single answer that blends them, or that applies a
  transmission clause to a distribution asset (or vice versa), is a direct hazard. The
  agent must separate on `AssetType` / `StandardReference` and refuse to answer when the
  asset type is ambiguous.
- **Over-trust in draft answers in the field.** Field engineers on a tablet/Teams under
  time pressure may act on a drafted technical-query response before sign-off. Every
  generated TQ carries the **"DRAFT — pending engineering review"** marker and status
  `Draft`; the UI should make the unreviewed state unmissable and never present a draft as
  a decision.
- **Constructability risk.** Answers that quote acceptance criteria the source does not
  actually contain would drive wrong hold/witness points downstream in ITPs and
  inspections. The no-fabrication + placeholder rule is the control; weak enforcement here
  propagates into generated deliverables.
- **Commissioning risk.** A commissioning question answered from an `In Review` (not yet
  `Approved`) procedure could carry unverified steps (purge, pressure test, leak test
  sequencing). Prefer `Approved` sources and flag reliance on `In Review` content, as in
  the ingestion risk lens.
- **Emergency-response implication.** Emergency/field queries must trace to the correct
  asset type and the **current** revision. `Superseded` documents must be excluded from
  grounding so responders are never served withdrawn procedures; when only superseded or
  draft content exists, the agent states that and defers.
- **Standards to review (labels only, no fabricated clauses).** For transmission queries:
  AS 2885 series; for distribution queries: AS/NZS 4645 series; welding queries: the
  applicable welding standard recorded under `Standard Reference = Other`. These are
  review pointers only - actual clause numbers and acceptance criteria come solely from
  the licensed source once OQ-1 is confirmed.
- **Practical field solution.** Until OQ-1 is resolved, operate the assistant in
  "procedures + project docs + lessons learned" mode: it still answers a large share of
  field questions from company-controlled, groundable content, and clearly says when a
  question needs the licensed standard and the responsible engineer.
