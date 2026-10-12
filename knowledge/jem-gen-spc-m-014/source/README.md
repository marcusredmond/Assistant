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
| `jem-gen-spc-m-014.clauses.json` | Document metadata, ordered sections (1-11), and ordered clauses. Each clause has an ordered list of discrete, sentence/bullet-level `obligations` carrying verbatim `text` plus optional hint fields (`applies_to`, `references`, `cross_references`, `hold_witness_point`, `order_of_precedence`, `transcription_note`). |
| `appendix-f.rows.json` | Every row of the Appendix F "Specification Reference Guide" approval-class matrix `{clause, requirement_description, class}`, plus the Class A/B/C legend. |
| `README.md` | This provenance note. |

## Provenance

- **Source:** A verbatim extraction of the uploaded PDF of JEM-GEN-SPC-M-014 v4 (27 June
  2017), user-provided and captured in the task's `SOURCE-MATERIAL.md`.
- The transcription committed here is the **authoritative atomiser input**. Rule `text`
  and all quantitative limits are transcribed **verbatim**, with units kept exactly as
  written (not converted). Clause numbers, limits and acceptance criteria are never
  invented or paraphrased; where source wording is genuinely ambiguous a
  `transcription_note` is attached instead of inventing content.
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
