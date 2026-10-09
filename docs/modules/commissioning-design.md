# Commissioning Procedure Generation - Module Design

- **Title:** Engineering Knowledge Assistant (EKA) - `commissioning` Module Design (commissioning-procedure generation)
- **Version:** 0.1.0
- **Status:** Draft
- **Capability:** `commissioning` (second generator capability, built on the `itp` generator pattern)
- **Depends on:** [Solution Architecture](../architecture/solution-architecture.md),
  [Information Architecture](../information-arch/information-architecture.md),
  [Ingestion Flow Spec](../../flows/ingestion/ingestion-flow-spec.md),
  [ITP Module Design](itp-design.md) (generator pattern reused here),
  [Commissioning Procedure content type](../../schemas/content-types/generated-deliverable-commissioning-procedure.json),
  [Generation audit (Dataverse)](../../schemas/dataverse/generation-audit.json)
- **Implemented by:** [Commissioning procedure template](../../templates/commissioning/commissioning-procedure-template.md),
  [Commissioning generation flow spec](../../flows/commissioning/commissioning-generation-flow-spec.md)

> **Scope note.** Design artifact only. The sandbox cannot deploy to a Power Platform
> tenant. The flow and template referenced here are declarative, tenant-neutral designs
> for implementation in the target tenant by qualified makers, and every generated
> commissioning procedure is a draft requiring qualified-engineer review and sign-off. No
> clause number, acceptance criterion, or requirement from AS2885 / AS/NZS 4645 or any
> standard is ever fabricated; missing source text is left as a clearly-marked
> placeholder.

---

## 1. Purpose

Generate a **draft** commissioning procedure for a system or asset being brought into
service, from structured inputs plus grounding on cited source procedures. A commissioning
procedure sets out, in a controlled sequence, the pre-commissioning checks, the
commissioning steps, the acceptance / hold points at which work stops for verification, the
records produced, and the sign-off chain for putting the system safely into service.

The module serves the user capability **"generate commissioning procedures"**. It is the
second *generator* capability and deliberately **reuses the ITP generator pattern** from
[itp-design.md](itp-design.md): structured inputs -> templated draft -> stored in the
`GeneratedDeliverables` library -> routed for qualified-engineer review. What differs is the
deliverable structure (a sequenced procedure with hold points, not an inspection matrix) and
the stronger emphasis on commissioning-specific sequencing and safety controls (purge,
pressure / leak test sequencing, isolation, gas-in).

**It does not** ingest or classify documents (that is the
[ingestion flow](../../flows/ingestion/ingestion-flow-spec.md)); it **consumes** the
grounding metadata ingestion files and tags, and it writes its structured output to the
generation audit trail and a draft document in the `GeneratedDeliverables` library.

---

## 2. Generator pattern reused from `itp`

This module instantiates the same four-stage generator pattern established for ITPs. The
rules that matter for safety are identical in intent.

| Stage | ITP module | Commissioning module |
|---|---|---|
| Structured inputs | activity list + asset type + project metadata | commissioning scope + asset type + applicable procedure/standard references (labels) + project metadata |
| Templated draft | [ITP template](../../templates/itp/itp-template.md) | [commissioning procedure template](../../templates/commissioning/commissioning-procedure-template.md) |
| Stored deliverable | `GeneratedDeliverables`, content type ITP | `GeneratedDeliverables`, content type **Commissioning Procedure** ([schema](../../schemas/content-types/generated-deliverable-commissioning-procedure.json)) |
| Human-in-the-loop | qualified-engineer approval, DRAFT marker cleared on sign-off | identical review path |

Shared hard rules (from steering domain-accuracy), carried verbatim from the ITP module:

- Never invent or paraphrase a clause number, acceptance criterion, or requirement from
  AS2885 / AS/NZS 4645 or any standard; missing criteria become the marked placeholder.
- Keep transmission (`AS 2885` series) and distribution (`AS/NZS 4645` series) handling
  **distinct**; the standard family label carried differs by asset type and the two are
  never blended.
- Stamp the exact marker **"DRAFT — pending engineering review"** on every generated
  procedure.

---

## 3. Inputs

| Input | Source | Required | Notes |
|---|---|---|---|
| **System / asset being commissioned** | Canvas app form, or project metadata | Yes | The system / package being brought into service (for example a pipeline section, a station, a regulator set). Drives the procedure scope and title. |
| **Asset type** (`Transmission` \| `Distribution` \| `Not asset-specific`) | User / project metadata | Yes | Selects the applicable standard family and keeps AS2885 (transmission) and AS/NZS 4645 (distribution) **distinct**. Never inferred silently. |
| Applicable **procedure / standard references** (labels only) | User / project metadata | No | Governing document labels (for example an `Approved` company commissioning procedure, `AS 2885` series for transmission, `AS/NZS 4645` series for distribution, a welding standard under "Other"). Clause numbers and acceptance criteria are **not** supplied here and are **never** fabricated. |
| **Pre-commissioning check list** (structured) | Canvas app / grounded source procedure | Partial | Ordered checks to confirm the system is ready to commission (isolation confirmed, test equipment calibrated, instrumentation verified, etc.). |
| **Commissioning step list** (structured) | Canvas app / grounded source procedure | Partial | Ordered commissioning steps (for example purge, pressure test, leak test, nitrogen / gas-in, where applicable). Preserved in input sequence. |
| Project metadata | Canvas app / Dataverse | Yes | Project identifier, title, prepared-by, dates, revision. |

Each step or check in the structured lists may carry: a description, an acceptance /
hold-point classification, a responsible party, a verifying document, a record / form, and an
**optional** reference to a licensed clause. When a clause reference is required but its text
is not available from a licensed / approved source, the acceptance criterion is left as a
clearly-marked placeholder (section 6).

---

## 4. Asset-type / standard separation

Transmission and distribution assets are commissioned under different standard families and
must never be blended in one procedure.

| Asset type | Standard family label carried | Example commissioning scope |
|---|---|---|
| `Transmission` | `AS 2885` series (petroleum & gas pipeline systems) | pipeline purge, strength / pressure test, leak test, drying, nitrogen / gas-in, tie-ins |
| `Distribution` | `AS/NZS 4645` series (gas distribution networks) | mains purge, pressure test, commissioning / purging of distribution assets |
| `Not asset-specific` | none assumed | generic commissioning activities with project-supplied references only |

The generator stamps the asset-type-appropriate **standard family label** onto the procedure
header and onto any acceptance-criterion placeholder it emits. It will not place an `AS 2885`
label on a distribution procedure or an `AS/NZS 4645` label on a transmission procedure. The
label is a *pointer to the governing standard family*; it is not a clause number and carries
no acceptance-criteria text.

---

## 5. Procedure structure

The generated procedure follows a fixed structure, matching the
[commissioning procedure template](../../templates/commissioning/commissioning-procedure-template.md).

| Section | Content | Generation rule |
|---|---|---|
| **Purpose** | Why the procedure exists and the system it commissions. | From the system / asset input and scope. |
| **Scope** | Boundaries of what is and is not commissioned by this procedure. | From the scope input; asset-type stated. |
| **References** | Governing document labels (procedures, standards families). | Labels only; **no** clause numbers unless carried verbatim from a licensed source. |
| **Pre-commissioning checks** | Ordered readiness checks before commissioning starts. | One row per input check, in input order; acceptance defaults to the marked placeholder when a standard-derived criterion is required but not supplied. |
| **Commissioning steps** | Ordered commissioning sequence. | One row per input step, in input order; sequence preserved; hold / witness points carried, defaulting to `Review` only when unspecified and flagged for engineering confirmation. |
| **Acceptance / hold points** | Points at which work stops for witnessed verification. | Derived from the step classifications; a safety-critical step with an unspecified point is flagged, never silently downgraded. |
| **Records** | Records / forms produced by each step for traceability. | One row per record; carried from the input step's record / form. |
| **Sign-off** | Prepared / reviewed / approved chain. | Prepared by generator; reviewed and approved by qualified engineers on the human-in-the-loop path. |

**Hold / witness / review / monitor classification** uses the same legend as the ITP module
(**H** = Hold, **W** = Witness, **R** = Review, **M** = Monitor). Unspecified points default
to `Review`, never silently to a non-stopping point, and are flagged for the reviewing
engineer to set per the applicable standard.

---

## 6. Acceptance-criteria placeholder rule

Identical in intent to the ITP module. When a step or check requires a standard-derived
acceptance criterion (for example a pressure-test hold time or a leak-rate limit) and that
text is not supplied from a licensed / approved source, the generator emits the exact marked
placeholder and never fabricates a value:

`[PLACEHOLDER - acceptance criterion from licensed <standard> <clause> rev <year>]`

where `<standard>` is the asset-type standard **family label** (section 4) and
`<clause>` / `<year>` stay as literal tokens until filled from the licensed source. A
source-backed criterion is carried verbatim **only** when both the criterion and its source
are supplied.

---

## 7. Human-in-the-loop review step

The generator **drafts**; a qualified engineer **reviews and signs off**.

1. The flow generates the draft commissioning procedure document (from the template) and the
   generation audit entry, with status `Draft` and the DRAFT marker.
2. The draft is routed for qualified-engineer review (approval task). The reviewer:
   - replaces every acceptance-criterion **placeholder** with the actual criterion from the
     licensed / approved source (and records the clause / revision there, not before);
   - confirms the **commissioning sequence** is correct and complete (in particular that
     purge, pressure test, leak test, and gas-in steps are in the correct order and
     interlocked);
   - confirms every **Hold / Witness / Review / Monitor** classification, in particular that
     safety-critical steps (pressure / strength test, leak test, nitrogen / gas-in,
     isolation) carry **Hold** or **Witness** points where required;
   - confirms the correct asset-type standard family and that no transmission / distribution
     blending occurred.
3. On sign-off the reviewer records themselves as reviewer / approver and the DRAFT marker is
   cleared from the deliverable.
4. Until sign-off the procedure is **not** authoritative and must not be used to commission a
   live system.

---

## 8. Output & storage

| Artifact | Where | Notes |
|---|---|---|
| Commissioning procedure document (draft) | `GeneratedDeliverables` library, content type **Commissioning Procedure** ([schema](../../schemas/content-types/generated-deliverable-commissioning-procedure.json)) | Carries the DRAFT marker; `DeliverableType = commissioning-procedure`; `SystemUnderCommissioning` set from the input. |
| Generation audit entry | Dataverse generation audit ([schema](../../schemas/dataverse/generation-audit.json)) | Request, asset type, counts, outcome. |

The human-readable, reviewable deliverable lives in `GeneratedDeliverables`; the audit trail
records the generation request for traceability and retry.

---

## 9. Open-question dependencies

| Ref | Dependency | Effect on this module |
|---|---|---|
| OQ-1 | Standards licensing | **Precondition** for populating acceptance-criteria text (for example pressure-test hold times, leak-rate limits) from AS2885 / AS/NZS 4645. Until confirmed, every standard-derived acceptance criterion stays a marked placeholder for the reviewing engineer to complete from the licensed source. The procedure *structure* (sections, step sequence, hold points) generates unaffected, and the generator can ground on `Approved` company commissioning procedures immediately. |
| OQ-2 | Inventor integration scope | May supply system / component data (BOM, line lists) that seeds the scope and step list; does not block commissioning-procedure generation. |

---

## 10. Engineering review notes (risk lens)

Written from a senior pipeline engineer's perspective. These are design cautions to challenge
during review, not resolved decisions. They are kept consistent with the same section in the
[ITP module design](itp-design.md#8-engineering-review-notes-risk-lens), the
[ITP generation flow spec](../../flows/itp/itp-generation-flow-spec.md#6-engineering-review-notes-risk-lens),
and the [ingestion flow spec](../../flows/ingestion/ingestion-flow-spec.md#6-engineering-review-notes-risk-lens).

- **Assumption to challenge: "a generated commissioning procedure is a usable commissioning
  procedure."** The generator produces the *structure and sequence skeleton* from the input
  lists; it does not and must not supply the engineering judgement that sets purge volumes,
  pressure-test hold times, leak-rate acceptance, or the interlocks between steps. A
  plausible-looking but unreviewed procedure used to commission a live gas system is a
  high-consequence hazard. Every output is `Draft` with the DRAFT marker, and the UI must make
  the unreviewed state unmissable and never present a draft as issued-for-commissioning.
- **Safety / purge and gas-in sequencing.** The single highest-consequence commissioning
  failure is introducing gas into a system that has not been correctly purged, pressure
  tested, and leak tested in the right order, or with an incorrect inert-gas (nitrogen) purge
  such that a flammable air / gas mixture is formed. The generator must preserve the input
  step sequence exactly, must never reorder purge / test / gas-in steps, and must flag any
  gas-in or purge step that lacks a Hold / Witness point. Treat the sequence and the hold-point
  classification as safety controls, not formatting fields.
- **Safety / pressure and leak test sequencing.** Strength / pressure test and leak test are
  classic Hold / Witness activities with mandatory witnessed verification and defined hold
  times and acceptance limits. If the input omits them, mis-orders them, or classifies them as
  Monitor, the risk is energising a system without proven integrity. The generator defaults an
  unspecified point to `Review`, not Hold, so a missing classification cannot silently
  downgrade a test; the reviewer sets pressure / leak testing to Hold / Witness per the
  applicable standard. Hold times and leak-rate limits stay as placeholders until filled from
  a licensed source.
- **Safety / isolation and energy control.** Commissioning touches live or soon-to-be-live
  systems; positive isolation (and its verification) before and during work is critical. The
  pre-commissioning checks must include confirmation of isolation and that test equipment is
  calibrated and rated; the reviewer confirms isolation points are Hold points. The generator
  must not drop an isolation-confirmation check that the source procedure carries.
- **Constructability risk: wrong acceptance criteria propagating from an unlicensed source.**
  A confident-looking pressure-test hold time or leak-rate limit that was never in a licensed /
  approved source would drive a wrong accept / reject decision in the field. The no-fabrication
  rule plus the explicit placeholder is the control: criteria are blank-by-design until an
  engineer fills them from the licensed document. Do not add any "helpful" auto-fill of clause
  text or test parameters.
- **Mis-attributed AS2885-vs-AS/NZS 4645 risk.** Applying a transmission commissioning regime
  to a distribution asset (or vice versa) is a direct hazard - the test regimes and acceptance
  differ. The generator carries the asset-type standard **family label** and never blends the
  two; the reviewer must confirm the asset type and refuse a procedure whose steps mix
  transmission and distribution scope.
- **Emergency-response implication.** A commissioning procedure governs how a system is proven
  safe before it is put into service, and the records it produces are the as-commissioned
  integrity evidence that operators and emergency responders later rely on. Defective
  sequencing, missing hold points on test / gas-in steps, or missing records undermine that
  evidence and the ability to respond safely to an incident. Prefer sourcing steps from
  `Approved` commissioning procedures over `In Review` drafts, and ensure every step produces a
  traceable record / form.
- **Standards to review (labels only, no fabricated clauses).** For transmission commissioning:
  `AS 2885` series (pipeline systems; testing and commissioning parts as applicable). For
  distribution commissioning: `AS/NZS 4645` series (gas distribution networks). Welding scope:
  the applicable welding standard recorded under `Standard Reference = Other`. These are review
  pointers only; actual clause numbers, hold times, and acceptance criteria come solely from
  the licensed source once OQ-1 is confirmed.
- **Practical field solution.** Until OQ-1 is resolved, use the generator to produce the
  commissioning procedure *skeleton* - correct sections, pre-commissioning checks, ordered
  commissioning steps, provisional hold points, responsibilities, verifying documents, and
  record / form columns - with every standard-derived acceptance criterion (hold times,
  leak-rate limits) left as a placeholder. The responsible engineer then completes the criteria
  and confirms the sequence and hold points from the licensed standard and the `Approved`
  company procedure before the procedure is issued for commissioning. This gets most of the
  clerical work done safely without ever guessing a requirement.
