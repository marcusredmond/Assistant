# Commissioning Procedure - Template

- **Title:** Engineering Knowledge Assistant (EKA) - Commissioning Procedure Deliverable Template
- **Version:** 0.1.0
- **Status:** Draft

> ## DRAFT — pending engineering review
>
> This commissioning procedure is machine-generated and is **not** authoritative. It must
> be reviewed and signed off by a qualified engineer before use. Acceptance criteria shown
> as `[PLACEHOLDER - acceptance criterion from licensed <standard> <clause> rev <year>]`
> (for example pressure-test hold times and leak-rate limits) must be completed from the
> licensed / approved source document; clause numbers, hold times, and criteria are never
> fabricated. The commissioning sequence and all hold / witness points must be confirmed by
> the reviewing engineer. Do **not** use to commission a live system while this marker is
> present.

---

## Header

| Field | Value |
|---|---|
| Procedure Title | `<procedure title>` |
| System / Asset Under Commissioning | `<system or asset being commissioned>` |
| Project | `<project identifier>` |
| Asset Type | `<Transmission | Distribution | Not asset-specific>` |
| Standard / Procedure References (labels only) | `<e.g. Approved company commissioning procedure | AS 2885 series | AS/NZS 4645 series | Other>` |
| Revision | `<revision>` |
| Status | Draft |
| Prepared By | `<prepared by / generated>` |
| Reviewed By | `<qualified engineer - on sign-off>` |
| Approved By | `<approver - on sign-off>` |
| Date | `<date>` |

> **Hold-point legend:** **H** = Hold Point (work stops until released) ·
> **W** = Witness Point · **R** = Review (document / record review) ·
> **M** = Monitor / Surveillance.

---

## 1. Purpose

`<State why this procedure exists and the system / asset it commissions.>`

## 2. Scope

`<State the boundaries of what is and is not commissioned by this procedure, including the
asset type. Keep transmission (AS 2885 series) and distribution (AS/NZS 4645 series) scope
distinct; do not blend the two.>`

## 3. References

| Reference (label only) | Type | Notes |
|---|---|---|
| `<e.g. Approved company commissioning procedure>` | Procedure | `<notes>` |
| `<e.g. AS 2885 series | AS/NZS 4645 series | Other>` | Standard family label | No clause numbers unless carried verbatim from a licensed source. |

> References are **labels / pointers** only. Clause numbers and acceptance criteria are
> never fabricated; they are completed from the licensed / approved source during review.

## 4. Pre-commissioning checks

| Check No | Check / Readiness Item | Acceptance Criteria (Reference) | Verifying Document | Hold Point (H/W/R/M) | Responsibility | Record/Form | Status |
|---|---|---|---|---|---|---|---|
| 1 | `<pre-commissioning check, e.g. positive isolation confirmed>` | `[PLACEHOLDER - acceptance criterion from licensed <standard> <clause> rev <year>]` | `<verifying document>` | `<H | W | R | M>` | `<responsibility>` | `<record/form>` | Draft |

> Add one row per pre-commissioning check, in sequence. Acceptance-criteria cells default to
> the placeholder above and are completed only from a licensed / approved source during
> engineering review. Isolation and test-equipment-calibration checks should be Hold points.

## 5. Commissioning steps

| Step No | Commissioning Step | Acceptance Criteria (Reference) | Verifying Document | Hold Point (H/W/R/M) | Responsibility | Record/Form | Status |
|---|---|---|---|---|---|---|---|
| 1 | `<commissioning step, e.g. purge / pressure test / leak test / nitrogen / gas-in>` | `[PLACEHOLDER - acceptance criterion from licensed <standard> <clause> rev <year>]` | `<verifying document>` | `<H | W | R | M>` | `<responsibility>` | `<record/form>` | Draft |

> Add one row per commissioning step, **in sequence**. The sequence is a safety control: do
> not reorder purge / pressure test / leak test / gas-in steps. Unspecified hold points
> default to **R** (Review) and must be confirmed by the reviewing engineer; safety-critical
> steps (pressure / leak test, gas-in, isolation) require **H** or **W**.

## 6. Acceptance / hold points

| Hold Point Ref | Associated Step | Point Type (H/W) | Release Criteria (Reference) | Witnessed / Released By |
|---|---|---|---|---|
| HP-1 | `<step reference>` | `<H | W>` | `[PLACEHOLDER - release criterion from licensed <standard> <clause> rev <year>]` | `<qualified engineer / witness - on release>` |

> Add one row per acceptance / hold point. These are the points at which work stops for
> witnessed verification before the next step may proceed. Release criteria are completed
> only from a licensed / approved source during engineering review.

## 7. Records

| Record No | Record / Form | Produced By Step | Retention / Location | Status |
|---|---|---|---|---|
| 1 | `<record or form, e.g. pressure-test record, purge record>` | `<step reference>` | `<retention / location>` | Draft |

> Add one row per record / form produced. These records form the as-commissioned integrity
> evidence; every commissioning and test step should produce a traceable record.

## 8. Sign-off

| Role | Name | Signature | Date |
|---|---|---|---|
| Prepared by | | | |
| Reviewed by (qualified engineer) | | | |
| Approved by | | | |

> The **"DRAFT — pending engineering review"** marker is cleared only when a qualified
> engineer has reviewed and signed off this commissioning procedure, confirmed the
> commissioning sequence and all hold / witness points, and completed every acceptance
> criterion from the licensed / approved source.
