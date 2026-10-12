# JEM-GEN-SPC-M-014 Source Transcription

- **Title:** JEM-GEN-SPC-M-014 Source Transcription (atomiser input)
- **Version:** 1.0
- **Status:** Draft

## Purpose

This directory holds the authoritative, machine-readable source transcription of the Jemena
specification **JEM-GEN-SPC-M-014 "Piping and Mechanical Equipment – Shop Fabrication
Specification For Facilities"**, Version 4, dated 27 June 2017 (supersedes
P09JAM00-000SPC-M-006). It is the committed input that the atomiser prototype (FEAT-002)
parses to produce the clause-level atoms, per-clause Markdown mirror, and matrices. The
atomiser reads this committed in-repo content rather than a PDF, because no PDF and no PDF
libraries are available in the network-restricted sandbox.

## Files

| File | Contents |
|---|---|
| `jem-gen-spc-m-014.clauses.json` | Document metadata, ordered sections (1-11), and ordered clauses. Each clause has an ordered list of discrete, sentence/bullet-level `obligations` carrying `text` (a faithful rendering of the supplied extraction, limits/units verbatim) plus optional hint fields (`modality`, `applies_to`, `references`, `cross_references`, `hold_witness_point`, `order_of_precedence`, `transcription_note`, `modality_note`, `split_note`). An explicit `modality` hint, where present, is honoured by the atomiser ahead of wording-based derivation. |
| `appendix-f.rows.json` | Every row of the Appendix F "Specification Reference Guide" approval-class matrix `{clause, requirement_description, class}`, plus the Class A/B/C legend. |
| `README.md` | This provenance note. |

## Provenance

- **Source:** A user-provided extraction of the uploaded PDF of JEM-GEN-SPC-M-014 v4
  (27 June 2017), captured in the task's `SOURCE-MATERIAL.md`. That extraction is an
  already-condensed parenthetical outline of each clause, not the full PDF prose.
- The transcription committed here is the **authoritative atomiser input** and is a
  **faithful rendering of that supplied extraction**: rule `text` is expanded into
  readable sentences while all quantitative limits and units are preserved **verbatim**
  and kept exactly as written (not converted). Clause numbers, limits and acceptance
  criteria are never invented, dropped or altered; the wording is rendered, not quoted
  character-for-character against the original PDF. Where source wording is genuinely
  ambiguous a `transcription_note` is attached instead of inventing content.
- **Modality hints.** Some obligations carry an explicit `modality` hint. The supplied
  outline phrased a number of mandatory acceptance criteria descriptively (e.g. "is",
  "are"); an explicit `modality: shall` hint is set on those so the atomiser does not
  surface a hard limit (e.g. hydrostatic 1.5 x design pressure, interpass 300°C, drying
  dewpoint -40°C/-20°C, FAT 30 kPag, final NDE ≥24 hrs, archival film ≥7 years) as
  non-mandatory. A `modality_note` records why. Two compound obligations (5.2.6, 6.4)
  were split so a leading mandatory requirement and a trailing prohibition carry distinct
  modalities (`split_note` records this). No limit or wording was changed by these hints.
- **Ownership:** JEM-GEN-SPC-M-014 is **Jemena-owned content** (`jemena_owned`), so its
  text may be stored, atomised and grounded. Other `JEM-`, `GAS-` and `GTS-` documents are
  likewise Jemena-owned.
- **Copyright boundary:** Copyrighted **external** standards (AS / ASME / AWS / API / EN)
  are captured as **reference pointers / titles only** and their body text is **not**
  reproduced. Where the Jemena document's own §2.1 / §2.2 reference list does not supply a
  verbatim title, the `title` field is left `null` rather than invented.

## Known source anomalies preserved

- The printed clause numbering within Section 6.3 is preserved as published: **6.3.2**
  Inspection and NDE of Test Welds; **6.3.3** Approval of Welding Procedures; **6.3.4**
  Repair Procedures. The PWHT sentence is kept attached to clause 6.3.2 as in the source.
  This anomaly is noted here and in the module design doc rather than silently "fixed".
- The AS 2885.2 Clause 5.13 "Distance between welds" footnote is attached to clause 5.2.2.

## Status note

This is a **DRAFT** transcription pending qualified engineering review and sign-off.
