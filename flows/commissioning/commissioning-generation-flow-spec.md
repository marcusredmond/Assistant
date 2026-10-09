# EKA Commissioning Procedure Generation Flow - Specification

- **Title:** Engineering Knowledge Assistant (EKA) - Commissioning Procedure Generation Flow Specification
- **Version:** 0.1.0
- **Status:** Draft
- **Capability:** `commissioning` (generate commissioning procedures)
- **Depends on:** [Commissioning Module Design](../../docs/modules/commissioning-design.md),
  [Commissioning procedure template](../../templates/commissioning/commissioning-procedure-template.md),
  [Commissioning Procedure content type](../../schemas/content-types/generated-deliverable-commissioning-procedure.json),
  [Generation audit (Dataverse)](../../schemas/dataverse/generation-audit.json)

> **Scope note.** Design artifact only. The sandbox cannot deploy to a Power Platform
> tenant. The accompanying `commissioning-generation-flow.definition.json` is a
> tenant-neutral Power Automate export-style skeleton; connection references, site / library
> GUIDs, and the Dataverse environment are placeholders to be bound on import. The flow
> reuses the generator pattern established by the
> [ITP generation flow](../itp/itp-generation-flow-spec.md).

---

## 1. Purpose

A Power Automate flow that collects commissioning-procedure inputs (from the canvas app or a
form), populates the
[commissioning procedure template](../../templates/commissioning/commissioning-procedure-template.md)
via document generation, writes the draft to the `GeneratedDeliverables` library (content
type **Commissioning Procedure**), writes a generation audit entry, and routes the draft for
qualified-engineer review.

It implements the same safety-relevant rules the ITP generator applies: carry
acceptance-criteria **placeholders** when a standard clause is required (never fabricate),
preserve the commissioning step **sequence**, default an unspecified hold point to `Review`
(never silently to a non-stopping point), stamp the exact marker
**"DRAFT — pending engineering review"**, and keep transmission (`AS 2885`) and distribution
(`AS/NZS 4645`) handling **distinct**.

## 2. Trigger & inputs

| Property | Value |
|---|---|
| Connector | Power Apps (V2) / manual button, or a form submission |
| Trigger | **PowerApps (V2)** - the canvas app passes the commissioning inputs |

Inputs (see [commissioning-design.md section 3](../../docs/modules/commissioning-design.md#3-inputs)):

- `title`, `project`, `systemUnderCommissioning`,
  `assetType` (`Transmission` | `Distribution` | `Not asset-specific`), `scope`, `revision`,
  `preparedBy`;
- `preCommissioningChecksJson` - ordered pre-commissioning checks;
- `commissioningStepsJson` - ordered commissioning steps (purge, pressure test, leak test,
  gas-in, etc.).

Each check / step object may carry: `description`, `inspection_point` (H/W/R/M),
`responsibility`, `verifying_document`, `record_form`, `acceptance_criteria`,
`acceptance_source`.

## 3. Steps (trigger / action sequence)

1. **Trigger - PowerApps (V2).** The canvas app submits the inputs and the ordered check /
   step lists.
2. **Validate asset type.** `assetType` must be one of the three allowed values. If not,
   terminate with an error (keeps AS2885 / AS4645 distinct; never guesses).
3. **Resolve standard family label.** Transmission -> `AS 2885 series`;
   Distribution -> `AS/NZS 4645 series`; Not asset-specific -> `project-supplied reference`.
   The label is a pointer only, carrying **no** clause number or criteria text.
4. **Compose acceptance placeholder.** Build the exact placeholder
   `[PLACEHOLDER - acceptance criterion from licensed <standard> <clause> rev <year>]` used
   wherever a standard-derived criterion is required but not supplied from a licensed source.
5. **Parse checks and steps.** Parse `preCommissioningChecksJson` and
   `commissioningStepsJson` into ordered arrays, **preserving input order** (sequence is a
   safety control).
6. **Normalise the ordered lists.** `Normalise_pre_commissioning_checks` and
   `Normalise_commissioning_steps` are `Select` actions that run before the document write.
   For each row they:
   - normalise the hold point to an H/W/R/M code using the same Hold/Witness/Review/Monitor/
     Surveillance synonym mapping as the ITP prototype's `normalise_inspection_point`
     (default `R` / `Review`, never silently `Hold`), emitting `inspection_point_code`;
   - set `point_defaulted` when the raw value was empty or an unrecognised synonym, so a
     defaulted point can be rendered `(confirm)` (mirroring the prototype's `point_defaulted`);
   - resolve `acceptance_criteria` to a source-backed verbatim criterion **only** when both
     the criterion and its source are supplied, otherwise the exact placeholder;
   - carry responsibility, verifying document, and record / form.
   `Select` preserves input order.
7. **Generate the deliverable document.** Populate the commissioning procedure template
   (Word / SharePoint template or an Office Script over the markdown template) with the
   header and the normalised pre-commissioning check and commissioning step tables, hold
   points, and records, including the visible DRAFT marker. A defaulted (Review) point is
   rendered `(confirm)`.
8. **Store the draft.** Upload the document to `GeneratedDeliverables` with content type
   **Commissioning Procedure** (`DeliverableType = commissioning-procedure`,
   `SystemUnderCommissioning` set), carrying the DRAFT marker.
9. **Write a generation audit entry.** Record the request in the Dataverse
   `eka_generationrequest` table using only the columns that table defines
   (`eka_name`, `eka_deliverabletype = commissioning-procedure`, `eka_requestedon`,
   `eka_requestinput` carrying asset type / project / system / check and step counts,
   `eka_templateused`, `eka_outputdocurl`, `eka_status`). The audit table has no dedicated
   asset-type/project columns, so those are recorded inside `eka_requestinput`; the
   asset-type separation itself is enforced upstream by step 2.
10. **Route for engineering review.** Start an approval / assignment task to a qualified
    engineer. On sign-off, the reviewer confirms the sequence and hold points, completes the
    acceptance criteria from the licensed source, and the DRAFT marker is cleared. Until then
    the procedure is not authoritative and must not be used to commission a live system.
11. **Respond.** Return the document URL and status to the canvas app.

## 4. Rule parity with the ITP generator

| Rule | ITP generator | Commissioning flow step |
|---|---|---|
| Asset-type validity + standard label | validate + resolve label | 2, 3 |
| Preserve input order | line items in input order | 5, 6 (`Select` preserves order) |
| Acceptance-criteria placeholder vs source-backed | placeholder unless source supplied | 4, 6 |
| Hold-point normalisation (H/W/R/M synonyms), default Review | `normalise_inspection_point` | 6 (`Normalise_*` Select) |
| Defaulted-point flag (`(confirm)`) | `point_defaulted` | 6 (`point_defaulted` field) |
| DRAFT marker on output | DRAFT marker stamped | 7, 8 |
| Transmission / distribution distinct | never blended | 2, 3 |

## 5. Error handling

- Invalid / absent `assetType` terminates the run (no silent default); the two standard
  families are never blended.
- A missing acceptance criterion is **not** an error - it is left as the marked placeholder
  for the reviewing engineer.
- The commissioning step sequence is never reordered by the flow.
- Flow failures write to the audit log with the request reference for retry.

## 6. Engineering review notes (risk lens)

Kept consistent with the risk-lens sections in
[commissioning-design.md](../../docs/modules/commissioning-design.md#10-engineering-review-notes-risk-lens),
the [ITP generation flow spec](../itp/itp-generation-flow-spec.md#6-engineering-review-notes-risk-lens),
and the [ingestion flow spec](../ingestion/ingestion-flow-spec.md#6-engineering-review-notes-risk-lens).

- **Safety / sequencing and hold points.** The flow must preserve the commissioning step
  order exactly (purge, pressure test, leak test, nitrogen / gas-in) and must never silently
  set a safety-critical step to a non-stopping point. Unspecified points default to Review and
  are flagged; the reviewing engineer sets Hold / Witness per the applicable standard.
- **Safety / isolation and gas-in.** Isolation-confirmation and gas-in steps are the highest
  consequence; the flow flags any such step lacking a Hold / Witness point and never drops an
  isolation check the source procedure carries.
- **Constructability.** Acceptance criteria (hold times, leak-rate limits) are
  placeholder-by-design until filled from a licensed source; the flow must not auto-fill
  clause text or test parameters.
- **Commissioning.** Prefer sourcing steps from `Approved` commissioning procedures over
  `In Review` drafts; flag any commissioning step without a Hold / Witness point.
- **Asset-type separation.** Carry only the asset-type standard family label; refuse mixed
  transmission / distribution scope at review.
- **Emergency-response.** Traceable records / forms per step and correct hold points underpin
  the as-commissioned integrity case operators and responders later rely on.
- **Standards to review (labels only).** Transmission: `AS 2885` series; distribution:
  `AS/NZS 4645` series; welding under `Other`. Actual clauses, hold times, and acceptance
  come only from the licensed source once OQ-1 is confirmed.
