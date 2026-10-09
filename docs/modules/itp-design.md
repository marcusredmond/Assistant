# ITP Generation - Module Design

- **Title:** Engineering Knowledge Assistant (EKA) - `itp` Module Design (Inspection & Test Plan generation)
- **Version:** 0.1.0
- **Status:** Draft
- **Capability:** `itp` (first generator capability taken end-to-end)
- **Depends on:** [Solution Architecture](../architecture/solution-architecture.md),
  [Information Architecture](../information-arch/information-architecture.md),
  [Ingestion Flow Spec](../../flows/ingestion/ingestion-flow-spec.md),
  [ITP register (Dataverse)](../../schemas/dataverse/itp-register.json),
  [ITP content type](../../schemas/content-types/generated-deliverable-itp.json)
- **Implemented by:** [ITP template](../../templates/itp/itp-template.md),
  [ITP generation flow spec](../../flows/itp/itp-generation-flow-spec.md),
  [ITP logic prototype](../../prototypes/itp/itp_generator.py)

> **Scope note.** Design artifact only. The sandbox cannot deploy to a Power Platform
> tenant. The flow, template, and register referenced here are declarative, tenant-neutral
> designs for implementation in the target tenant by qualified makers, and every generated
> ITP is a draft requiring qualified-engineer review and sign-off. The accompanying Python
> prototype exists to validate the generation rules **before** low-code implementation; it
> is not a deployed component.

---

## 1. Purpose

Generate a **draft** Inspection & Test Plan (ITP) from a structured scope-of-work /
activity list. An ITP lists the inspection and test activities for a scope of work, and
for each activity records the inspection/test to perform, the acceptance criteria (with a
reference to the governing document), the verifying document, the inspection point
classification (Hold / Witness / Review / Monitor), who is responsible, and the record or
form produced.

The module serves the user capability **"generate ITPs"**. It is the first *generator*
capability taken end-to-end: full module design, deliverable template, Power Automate
generation flow spec, and a Python-stdlib logic prototype with unit tests that validates
the generation rules before they are built in low-code.

**It does not** ingest or classify documents (that is the
[ingestion flow](../../flows/ingestion/ingestion-flow-spec.md)); it **consumes** the
grounding metadata ingestion files and tags, and it writes its structured output to the
[ITP register](../../schemas/dataverse/itp-register.json) and a draft document in the
`GeneratedDeliverables` library.

---

## 2. Inputs

| Input | Source | Required | Notes |
|---|---|---|---|
| Scope of work / **activity list** | Canvas app form, or a structured file | Yes | Ordered list of construction/commissioning activities to be inspected or tested. Drives the ITP line items. |
| **Asset type** (`Transmission` \| `Distribution` \| `Not asset-specific`) | User / project metadata | Yes | Selects the applicable standard family and keeps AS2885 (transmission) and AS/NZS 4645 (distribution) **distinct**. Never inferred silently. |
| Applicable **standard references** (labels only) | User / project metadata | No | Governing document labels (for example `AS 2885` series for transmission, `AS/NZS 4645` series for distribution, a welding standard under "Other"). Clause numbers and acceptance criteria are **not** supplied here and are **never** fabricated. |
| Project metadata | Canvas app / Dataverse | Yes | Project identifier, title, prepared-by, dates. |
| Per-activity attributes | Activity list | Partial | Inspection/test description, inspection point (H/W/R/M), responsibility, verifying document, record/form, and (optional) a reference to a licensed clause. |

Each activity in the activity list may carry: a name/operation, an inspection or test
description, an inspection-point classification, a responsible party, a verifying
document, a record/form, and an **optional** standard-clause reference. When a clause
reference is required but its text is not available from a licensed/approved source, the
acceptance criterion is left as a clearly-marked placeholder (section 4).

---

## 3. Asset-type / standard separation

Transmission and distribution assets are governed by different standard families and must
never be blended in one ITP.

| Asset type | Standard family label carried | Example disciplines |
|---|---|---|
| `Transmission` | `AS 2885` series (petroleum & gas pipeline systems) | pipeline welding, NDT, coating, pressure/strength testing, tie-ins |
| `Distribution` | `AS/NZS 4645` series (gas distribution networks) | mains laying, jointing, pressure testing, commissioning/purging |
| `Not asset-specific` | none assumed | generic QA activities with project-supplied references only |

The generator stamps the asset-type-appropriate **standard family label** onto the ITP
header and onto any acceptance-criterion placeholder it emits. It will not place an
`AS 2885` label on a distribution ITP or an `AS/NZS 4645` label on a transmission ITP.
The label is a *pointer to the governing standard family*; it is not a clause number and
carries no acceptance-criteria text.

---

## 4. Generation rules - activities to ITP line items

Each activity in the input maps to exactly one ITP line item. The line-item columns match
the [ITP template](../../templates/itp/itp-template.md) and the
[`eka_itplineitem`](../../schemas/dataverse/itp-register.json) table.

| Line-item column | Rule |
|---|---|
| **Item No** | Sequence number assigned in input order (1-based). |
| **Activity/Operation** | Taken verbatim from the activity name. |
| **Inspection/Test** | Taken from the activity's inspection/test description; if absent, a neutral `"To be defined"` placeholder (never a fabricated test). |
| **Acceptance Criteria (Reference)** | If the activity supplies a *verbatim, source-backed* acceptance criterion, carry it unchanged with its source. **Otherwise emit the placeholder** `[PLACEHOLDER - acceptance criterion from licensed <standard> <clause> rev <year>]`, where `<standard>` is the asset-type standard **family label** (section 3) and `<clause>`/`<year>` stay as literal `<clause>` / `<year>` tokens until filled from the licensed source. **No clause number or criterion text is ever invented.** |
| **Verifying Document** | The document/record that evidences the activity (for example an inspection report, test certificate, weld map); label only. |
| **Inspection Point (H/W/R/M)** | Hold / Witness / Review / Monitor classification. Normalised from the activity's inspection-point value; defaults to `Review` only when unspecified, with a note that the point type needs engineering confirmation. |
| **Responsibility** | Who performs/verifies the activity. |
| **Record/Form** | The record or form produced. |
| **Status** | Always `Draft` on generation. |

**Hard rules (safety-critical, from steering domain-accuracy):**

- Never invent or paraphrase a clause number, acceptance criterion, or requirement from
  AS2885 / AS/NZS 4645 or any standard. Missing criteria become the marked placeholder.
- Keep transmission (AS 2885) and distribution (AS/NZS 4645) handling distinct; the
  standard family label carried differs by asset type and the two are never blended.
- Stamp the exact marker **"DRAFT — pending engineering review"** on every generated ITP.

---

## 5. Human-in-the-loop review step

The generator **drafts**; a qualified engineer **reviews and signs off**.

1. The flow generates the draft ITP document (from the template) and the structured
   register header + line items, all with status `Draft` and the DRAFT marker.
2. The draft is routed for qualified-engineer review (approval task). The reviewer:
   - replaces every acceptance-criterion **placeholder** with the actual criterion from
     the licensed/approved source (and records the clause/revision there, not before);
   - confirms every **Hold/Witness/Review/Monitor** classification, in particular that
     safety-critical activities (for example pressure/strength testing, welding and NDT)
     carry **Hold** or **Witness** points where required;
   - confirms the correct asset-type standard family and that no transmission/distribution
     blending occurred.
3. On sign-off the reviewer sets the register header `eka_status` to `Approved`, records
   themselves in `eka_reviewedby`, and the DRAFT marker is cleared from the deliverable.
4. Until sign-off the ITP is **not** authoritative and must not be issued for construction.

---

## 6. Output & storage

| Artifact | Where | Notes |
|---|---|---|
| ITP document (draft) | `GeneratedDeliverables` library, content type **ITP** ([schema](../../schemas/content-types/generated-deliverable-itp.json)) | Carries the DRAFT marker; `DeliverableType = itp`; links back to the register via `ItpRegisterId`. |
| ITP header (structured) | Dataverse `eka_itpregister` ([schema](../../schemas/dataverse/itp-register.json)) | One row per ITP: title, project, asset type, scope, status `Draft`, DRAFT marker, SharePoint URL, reviewed-by. |
| ITP line items (structured) | Dataverse `eka_itplineitem` (1:N from header) | One row per activity; acceptance criteria default to the marked placeholder. |
| Generation audit entry | Generation/ingestion audit trail | Request, asset type, counts, outcome. |

The structured register is the system of record for line items (a SharePoint document
library is unsuited to row-level structured data); the document in `GeneratedDeliverables`
is the human-readable, reviewable deliverable.

---

## 7. Open-question dependencies

| Ref | Dependency | Effect on this module |
|---|---|---|
| OQ-1 | Standards licensing | **Precondition** for populating acceptance-criteria text from AS2885 / AS/NZS 4645. Until confirmed, every standard-derived acceptance criterion stays a marked placeholder for the reviewing engineer to complete from the licensed source. The ITP *structure* (line items, inspection points) generates unaffected. |
| OQ-2 | Inventor integration scope | May supply BOM / weld / component data that seeds activities; does not block ITP generation. |

---

## 8. Engineering review notes (risk lens)

Written from a senior pipeline engineer's perspective. These are design cautions to
challenge during review, not resolved decisions. They are kept consistent with the same
section in the [ingestion flow spec](../../flows/ingestion/ingestion-flow-spec.md#6-engineering-review-notes-risk-lens)
and the [tech-query module design](tech-query-design.md#9-engineering-review-notes-risk-lens).

- **Assumption to challenge: "a generated ITP is a usable ITP."** The generator produces
  the *structure* of an ITP from the activity list; it does not and must not supply the
  engineering judgement that decides acceptance criteria and hold points. A plausible-
  looking but unreviewed ITP is more dangerous than an obviously incomplete one, because it
  invites use. Every output is `Draft` with the DRAFT marker, and the UI should make the
  unreviewed state unmissable and never present a draft as issued-for-construction.
- **Safety / missing hold points on pressure testing.** The single highest-consequence ITP
  failure is a pressure/strength/leak test that is *not* a Hold Point - the activity could
  proceed (or the system be energised) without the mandatory witnessed verification. The
  generator defaults an unspecified inspection point to `Review`, **not** Hold, precisely so
  that a missing classification cannot silently downgrade a test to a non-stopping point;
  the reviewer must set pressure testing to Hold/Witness as the applicable standard
  requires. Treat the inspection-point classification as a safety control, not a formatting
  field.
- **Welding / NDT inspection points.** Weld procedure qualification, welder qualification,
  visual inspection and NDT (for example radiography) are classic Hold/Witness activities;
  if the input omits them or classifies them as Monitor, the risk is unverified welds
  entering a live pipeline. The reviewer must confirm welding and NDT points against the
  WPS/PQR regime and the applicable standard; the generator will not invent these.
- **Constructability risk: wrong acceptance criteria propagating from an unlicensed
  source.** The most insidious failure mode is a *confident-looking* acceptance criterion
  that was never in a licensed/approved source - it would drive wrong accept/reject
  decisions in the field. The no-fabrication rule plus the explicit placeholder is the
  control: criteria are blank-by-design until an engineer fills them from the licensed
  document. Do not add any "helpful" auto-fill of clause text.
- **Commissioning risk.** Commissioning activities (purge, pressure test, leak test,
  tie-in, pigging where applicable) have strict sequencing and witnessing requirements; an
  ITP that reorders them or drops a witness/hold point creates a commissioning hazard.
  Preserve input sequence, flag any commissioning activity lacking a Hold/Witness point for
  reviewer attention, and prefer sourcing these activities from `Approved` commissioning
  procedures rather than `In Review` drafts.
- **Mis-attributed AS2885-vs-AS/NZS 4645 risk.** Applying a transmission acceptance regime
  to a distribution asset (or vice versa) is a direct hazard. The generator carries the
  asset-type standard **family label** and never blends the two; the reviewer must confirm
  the asset type and refuse an ITP whose activities mix transmission and distribution scope.
- **Emergency-response implication.** An ITP governs how a system is proven safe before it
  is put into service; a defective or unreviewed ITP undermines the integrity evidence that
  emergency responders and operators later rely on. Hold points on test and tie-in
  activities, and traceable records/forms per line item, are what make the as-built
  integrity case defensible.
- **Standards to review (labels only, no fabricated clauses).** For transmission ITPs:
  `AS 2885` series (pipeline systems; welding, testing and commissioning parts as
  applicable). For distribution ITPs: `AS/NZS 4645` series (gas distribution networks).
  Welding scope: the applicable welding standard recorded under `Standard Reference =
  Other`. These are review pointers only; actual clause numbers and acceptance criteria
  come solely from the licensed source once OQ-1 is confirmed.
- **Practical field solution.** Until OQ-1 is resolved, use the generator to produce the
  ITP *skeleton* - correct activities, sequence, responsibilities, verifying documents,
  record/form columns and provisional inspection points - with every standard-derived
  acceptance criterion left as a placeholder. The responsible engineer then completes the
  criteria and confirms hold points from the licensed standard before the ITP is issued.
  This gets most of the clerical work done safely without ever guessing a requirement.
