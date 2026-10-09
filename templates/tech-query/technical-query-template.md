# Technical Query (TQ) - Deliverable Template

- **Title:** Engineering Knowledge Assistant (EKA) - Technical Query Deliverable Template
- **Version:** 0.1.0
- **Status:** Draft
- **Capability:** `tech-query`
- **Produced by:** [`generate-technical-query`](../../agents/tech-query/topics/generate-technical-query.json) topic
- **Register record:** [`eka_technicalquery`](../../schemas/dataverse/technical-query-register.json)
- **Content type:** [Technical Query](../../schemas/content-types/generated-deliverable-technical-query.json)

> # DRAFT — pending engineering review
>
> This technical query is a machine-drafted deliverable. It is **not approved** and must
> be reviewed, verified, and signed off by a qualified engineer before use. The response
> is grounded on cited sources only; it does not invent clause numbers, acceptance
> criteria, or requirements, and defers to the authoritative document and the responsible
> engineer where a source is unavailable.

---

## 1. Query identification

| Field | Value |
|---|---|
| **Query reference (TQ number)** | `[TQ-REF]` |
| **Project** | `[PROJECT]` |
| **Discipline** | `[DISCIPLINE]` |
| **Asset type** | `[Transmission (AS 2885) / Distribution (AS/NZS 4645) / Not asset-specific]` |
| **Standard reference (label only)** | `[AS 2885.x / AS/NZS 4645.x / Other / None]` |
| **Status** | Draft |
| **Raised by** | `[RAISED-BY]` |
| **Date raised** | `[DATE]` |

> **Asset-type note.** Keep AS 2885 (transmission) and AS/NZS 4645 (distribution) distinct.
> Do not apply a transmission requirement to a distribution asset or vice versa.

---

## 2. Question

> `[QUESTION - the engineering query being raised]`

---

## 3. Supporting context

> `[SUPPORTING CONTEXT - background, drawings, prior correspondence, references. Optional.]`

---

## 4. Drafted response (grounded)

> `[DRAFTED RESPONSE - composed only from cited sources below. If no groundable source`
> `supports a response, leave this blank for the responsible engineer and state so.`
> `Never fabricate clause numbers, acceptance criteria, or requirements.]`

### 4.1 Citations

Every engineering claim in the response above must be traceable to a source here. Record
a clause/section and revision **only** when printed in the licensed source; otherwise use
the placeholder.

| # | Source document | Library | Standard reference (label) | Clause / section | Revision / year |
|---|---|---|---|---|---|
| 1 | `[DOCUMENT]` | `[LIBRARY]` | `[AS 2885.x / AS/NZS 4645.x / Other / n/a]` | `[CLAUSE/SECTION or [PLACEHOLDER - to be filled from licensed <standard> <clause> rev <year>]]` | `[REVISION or [PLACEHOLDER - to be filled from licensed <standard> <clause> rev <year>]]` |

> **Standards-licensing note (OQ-1).** Grounding on the text of AS2885 / AS/NZS 4645 or
> other copyrighted standards requires confirmed licensing. Until confirmed, standards
> clause content is unavailable and remains a placeholder; the response is grounded on
> procedures, project documents, and lessons learned only.

---

## 5. Review & close-out

| Field | Value |
|---|---|
| **Reviewed by (qualified engineer)** | `[REVIEWED-BY]` |
| **Review date** | `[DATE]` |
| **Outcome** | `[Approved / Revise / Rejected]` |
| **Close-out response** | `[ENGINEER CLOSE-OUT - the authoritative response on sign-off]` |
| **Status on close-out** | `[In Review -> Approved]` |

> This template remains marked **"DRAFT — pending engineering review"** and status `Draft`
> until a qualified engineer completes section 5 and signs off.
