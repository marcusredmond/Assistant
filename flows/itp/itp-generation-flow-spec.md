# EKA ITP Generation Flow - Specification

- **Title:** Engineering Knowledge Assistant (EKA) - ITP Generation Flow Specification
- **Version:** 0.1.0
- **Status:** Draft
- **Capability:** `itp` (generate ITPs)
- **Depends on:** [ITP Module Design](../../docs/modules/itp-design.md),
  [ITP template](../../templates/itp/itp-template.md),
  [ITP register (Dataverse)](../../schemas/dataverse/itp-register.json),
  [ITP content type](../../schemas/content-types/generated-deliverable-itp.json),
  [ITP logic prototype](../../prototypes/itp/itp_generator.py)

> **Scope note.** Design artifact only. The sandbox cannot deploy to a Power Platform
> tenant. The accompanying `itp-generation-flow.definition.json` is a tenant-neutral
> Power Automate export-style skeleton; connection references, site/library GUIDs, and
> Dataverse environment are placeholders to be bound on import. The generation rules this
> flow applies are the ones validated by the
> [ITP logic prototype](../../prototypes/itp/itp_generator.py).

---

## 1. Purpose

A Power Automate flow that collects ITP inputs (from the canvas app or a form), applies the
ITP generation rules, populates the [ITP template](../../templates/itp/itp-template.md) via
document generation, writes the draft to the `GeneratedDeliverables` library and an ITP
register record (header + line items), and routes the draft for qualified-engineer review.

It implements the same rules the prototype validates: carry acceptance-criteria
**placeholders** when a standard clause is required (never fabricate), stamp the exact
marker **"DRAFT — pending engineering review"**, and keep transmission (AS 2885) and
distribution (AS/NZS 4645) handling **distinct**.

## 2. Trigger & inputs

| Property | Value |
|---|---|
| Connector | Power Apps (V2) / manual button, or a form submission |
| Trigger | **PowerApps (V2)** - the canvas app passes the ITP inputs |

Inputs (see [itp-design.md section 2](../../docs/modules/itp-design.md#2-inputs)):

- `title`, `project`, `assetType` (`Transmission` | `Distribution` | `Not asset-specific`),
  `scopeOfWork`, `revision`, `preparedBy`;
- `activitiesJson` - the structured activity list (same shape as
  [`sample-activities.json`](../../prototypes/itp/sample-activities.json)).

## 3. Steps (trigger / action sequence)

1. **Trigger - PowerApps (V2).** The canvas app submits the ITP inputs and activity list.
2. **Validate asset type.** `assetType` must be one of the three allowed values. If not,
   terminate with an error (keeps AS2885/AS4645 distinct; never guesses).
3. **Resolve standard family label.** Transmission -> `AS 2885 series`;
   Distribution -> `AS/NZS 4645 series`; Not asset-specific -> `project-supplied reference`.
   The label is a pointer only, carrying **no** clause number or criteria text.
4. **Parse activities.** Parse `activitiesJson` into an array of activity objects.
5. **Create ITP register header.** Create an `eka_itpregister` row (status `Draft`,
   `eka_draftmarker = "DRAFT — pending engineering review"`, asset type, project, scope).
6. **Generate line items.** For each activity, create an `eka_itplineitem` row linked to the
   header:
   - `eka_sequence` set from the 1-based loop index so stored line items preserve input
     order (`Generate_line_items` runs sequentially, concurrency `1`);
   - `eka_acceptancecriteria` = a source-backed verbatim criterion **only** when the
     activity supplies both the criterion and its source; otherwise the marked placeholder
     `[PLACEHOLDER - acceptance criterion from licensed <standard> <clause> rev <year>]`;
   - normalise the inspection point to an H/W/R/M code (the `Normalise_inspection_point_code`
     Compose maps Hold/Witness/Review/Monitor/Surveillance synonyms exactly as the
     prototype's `normalise_inspection_point`; default `R` / `Review`, flagged for
     confirmation via `Compose_point_defaulted`, never silently `Hold`), then map the code to
     the register's `eka_inspectiontype` choice (`H` -> `Hold Point`, `W` -> `Witness Point`,
     `R` -> `Review`, `M` -> `Monitor`) in `Map_inspection_point_choice` and write it to
     `eka_inspectiontype`;
   - a defaulted (Review) point is surfaced as `(confirm)` in the generated document (step 7),
     matching the prototype's `point_defaulted` annotation;
   - carry responsibility, verifying document, record/form.
7. **Generate the deliverable document.** Populate the ITP template (Word/SharePoint
   template or an Office Script over the markdown template) with the header and line-item
   table, including the visible DRAFT marker.
8. **Store the draft.** Upload the document to `GeneratedDeliverables` with content type
   **ITP** (`DeliverableType = itp`), link it to the register header via `ItpRegisterId`,
   and write the SharePoint URL back onto the header (`eka_sharepointdocurl`).
9. **Route for engineering review.** Start an approval/assignment task to a qualified
   engineer. On sign-off, set `eka_status = Approved`, record `eka_reviewedby`, and clear
   the DRAFT marker. Until then the ITP is not authoritative.
10. **Audit + respond.** Write a generation audit entry to the Dataverse
    `eka_generationrequest` table using only the columns that table defines
    (`eka_name`, `eka_deliverabletype = itp`, `eka_requestedon`, `eka_requestinput`
    carrying asset type / project / activity count, `eka_templateused`,
    `eka_outputdocurl`, `eka_status`), then return the register id and document URL to the
    canvas app. The audit table has no dedicated asset-type/project columns, so those are
    recorded inside `eka_requestinput`; the asset-type separation itself is enforced upstream
    by step 2.

## 4. Rule parity with the prototype

| Rule | Prototype function | Flow step |
|---|---|---|
| Asset-type validity + standard label | `generate_itp` / `STANDARD_LABELS` | 2, 3 |
| One line item per activity, input order | `build_line_item` | 6 |
| Acceptance-criteria placeholder vs source-backed | `_resolve_acceptance` / `acceptance_placeholder` | 6 |
| Inspection point normalisation (H/W/R/M synonyms), default Review | `normalise_inspection_point` | 6 (`Normalise_inspection_point_code` -> `Map_inspection_point_choice`) |
| Defaulted-point flag (`(confirm)`) | `point_defaulted` | 6 (`Compose_point_defaulted`) |
| Preserve line-item order (`eka_sequence`) | `build_line_item` item_no | 6 (`iterationIndexes` + 1) |
| DRAFT marker on output | `DRAFT_MARKER` | 5, 7 |

## 5. Error handling

- Invalid/absent `assetType` terminates the run (no silent default); the two standard
  families are never blended.
- A missing acceptance criterion is **not** an error - it is left as the marked
  placeholder for the reviewing engineer.
- Flow failures write to the audit log with the register reference for retry.

## 6. Engineering review notes (risk lens)

Kept consistent with the risk-lens sections in
[itp-design.md](../../docs/modules/itp-design.md#8-engineering-review-notes-risk-lens) and the
[ingestion flow spec](../ingestion/ingestion-flow-spec.md#6-engineering-review-notes-risk-lens).

- **Safety / hold points.** The flow must never silently set a safety-critical test (for
  example hydrostatic/pressure test, NDT) to a non-stopping point. Unspecified points
  default to Review and are flagged; the reviewing engineer sets Hold/Witness per the
  applicable standard.
- **Constructability.** Acceptance criteria are placeholder-by-design until filled from a
  licensed source; the flow must not auto-fill clause text. Weak enforcement would
  propagate wrong accept/reject criteria into the field.
- **Commissioning.** Preserve activity sequence; flag any commissioning activity without a
  Hold/Witness point; prefer `Approved` source procedures over `In Review` drafts.
- **Asset-type separation.** Carry only the asset-type standard family label; refuse mixed
  transmission/distribution scope at review.
- **Emergency-response.** Traceable records/forms per line item and correct hold points
  underpin the as-built integrity case responders later rely on.
- **Standards to review (labels only).** Transmission: `AS 2885` series; distribution:
  `AS/NZS 4645` series; welding under `Other`. Actual clauses come only from the licensed
  source once OQ-1 is confirmed.
