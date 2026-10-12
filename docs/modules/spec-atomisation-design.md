# Spec Atomisation Module Design

- **Title:** Spec Atomisation (JEM-GEN-SPC-M-014) Module Design
- **Version:** 0.1
- **Status:** Draft

Atomise a Jemena-owned specification into AI-readable, clause-traceable rule atoms
so a document-grounded assistant can read, cite and reason over the requirements
without re-interpreting the source PDF each time.

> This design doc is part of the Engineering Knowledge Assistant (EKA) program.
> The atomisation artifacts it describes live on the `atomise-jem-gen-spc-m-014`
> branch. Some EKA artifacts referenced by role below (the tech-query Copilot
> agent, the ITP generator, the information-architecture doc) are delivered on the
> separate `eka-foundation` branch and are named rather than linked here.

## Dependencies

| Artifact | Location | Relationship |
|---|---|---|
| Repository README artifact index | [`../../README.md`](../../README.md) | Lists this module doc, the atomiser prototype and the corpus. |
| Atomiser prototype | [`../../prototypes/atomiser/`](../../prototypes/atomiser/) | Produces the atomised corpus from the committed source. |
| Source transcription | [`../../knowledge/jem-gen-spc-m-014/source/`](../../knowledge/jem-gen-spc-m-014/source/) | Verbatim atomiser input (committed, not a live PDF). |
| JSONL atoms | [`../../knowledge/jem-gen-spc-m-014/atoms/`](../../knowledge/jem-gen-spc-m-014/atoms/) | One rule object per line, the primary grounding corpus. |
| Per-clause Markdown mirror | [`../../knowledge/jem-gen-spc-m-014/clauses/`](../../knowledge/jem-gen-spc-m-014/clauses/) | Human-readable mirror with YAML front-matter. |
| Matrices | [`../../knowledge/jem-gen-spc-m-014/matrices/`](../../knowledge/jem-gen-spc-m-014/matrices/) | Appendix F RTM + legend, reference register. |
| Template schemas | [`../../knowledge/jem-gen-spc-m-014/schemas/`](../../knowledge/jem-gen-spc-m-014/schemas/) | Field structure of the five spec forms. |
| Manifest | [`../../knowledge/jem-gen-spc-m-014/manifest.json`](../../knowledge/jem-gen-spc-m-014/manifest.json) | Document identity, counts, join rule, provenance. |
| tech-query Copilot agent | EKA program (`eka-foundation` branch) | Consumes atoms as a grounding source; cites `rule_id` / clause. |
| ITP generator | EKA program (`eka-foundation` branch) | Consumes hold/witness points and approval classes. |
| Information architecture | EKA program (`eka-foundation` branch) | Content types / metadata the corpus maps to. |

## 1. Purpose

JEM-GEN-SPC-M-014 *Piping and Mechanical Equipment – Shop Fabrication Specification
For Facilities* (Version 4, 27 June 2017, supersedes P09JAM00-000SPC-M-006) is a
Jemena-owned specification. This module atomises it into discrete, clause-traceable
**rule atoms**: one obligation per atom, each carrying verbatim rule text plus the
structured metadata an AI assistant needs to find, cite and reason over the rule.

Goals:

- **Full traceability by clause.** Every atom links back to its section, clause,
  clause title and source page, and carries a stable `rule_id`.
- **AI-readable granularity.** Bullet / sentence-level atoms so retrieval returns a
  single rule, not a whole clause blob.
- **No fabrication.** Rule text, clause numbers, limits and acceptance criteria are
  verbatim from the committed source; nothing is invented or paraphrased.
- **Dual output.** Machine-first JSONL atoms plus a human-readable per-clause
  Markdown mirror, both generated from the same source.

## 2. Provenance

The corpus is produced by a deterministic, reproducible pipeline:

1. **User-provided PDF extraction.** The uploaded PDF of JEM-GEN-SPC-M-014 v4 was
   captured verbatim in the task's `SOURCE-MATERIAL.md`.
2. **Committed source transcription.** That extraction was transcribed into
   machine-readable JSON under
   [`knowledge/jem-gen-spc-m-014/source/`](../../knowledge/jem-gen-spc-m-014/source/)
   (`jem-gen-spc-m-014.clauses.json` and `appendix-f.rows.json`). The atomiser reads
   this committed in-repo content rather than a PDF, because no PDF and no PDF
   libraries are available in the network-restricted sandbox.
3. **Generated outputs.** The atomiser prototype parses the transcription and emits
   the atoms, clause mirror, manifest, matrices and template schemas under
   `knowledge/jem-gen-spc-m-014/`. These generated files are checked in; they are the
   deliverable corpus. Regenerate with `python3 prototypes/atomiser/atomiser.py`.

Rule text and all quantitative limits are transcribed verbatim, with units kept
exactly as written (not converted). Where source wording was genuinely ambiguous, a
`transcription_note` was attached in the source rather than inventing content.

## 3. Atom schema

One obligation yields one atom. Order-of-Precedence (see Section 9) adds four extra
ranked atoms. Current totals: **11 sections, 78 clauses, 186 obligations yielding 190
atoms** (186 obligation atoms + 4 ranked §2.4 atoms).

| Field | Type | Notes |
|---|---|---|
| `rule_id` | string | Stable `JEM-GEN-SPC-M-014:<clause>:R<nn>`, `<nn>` zero-padded per clause. Unique across the corpus. |
| `doc_id` | string | `JEM-GEN-SPC-M-014`. |
| `doc_version` | string | `4`. |
| `doc_title` | string | Full document title. |
| `supersedes` | string | `P09JAM00-000SPC-M-006`. |
| `section` | string | Parent section number (1-11). |
| `clause` | string | Parent clause number (e.g. `5.2.2`). |
| `clause_title` | string | Parent clause title. |
| `rule_text` | string | **Verbatim** obligation text. Never paraphrased or altered. |
| `plain_summary` | string / null | Optional plain-language aid. **Null unless supplied; never replaces `rule_text`.** |
| `modality` | enum | See allowed set below. Derived deterministically from the verbatim wording. |
| `parameter` | string / null | Null for narrative obligations (see Section 3.2 caveat). |
| `value` | string / null | Null for narrative obligations. |
| `operator` | string / null | Null for narrative obligations. |
| `unit` | string / null | Null for narrative obligations; units are never converted. |
| `applies_to` | list | Scope tags (e.g. `shop-fabrication`, `welding`). |
| `references` | list | External reference **pointer strings** (titles / clause pointers only). |
| `cross_references` | list | In-document clause links. |
| `hold_witness_point` | bool | `true` for Clause 3.1 HOLD / WITNESS point obligations. |
| `approval_required` | bool | `true` where the clause appears in Appendix F. |
| `approval_class` | enum / null | `A`, `B`, `C` or null. Joined from Appendix F (see Section 3.1). |
| `source_page` | int | Source page for traceability. |
| `order_of_precedence_rank` | int / null | Set only on the ranked §2.4 atoms (1-4). |

### Allowed modality set

`shall`, `should`, `may`, `not_permitted`, `prohibited`, `informational`.

Modality is derived deterministically from the verbatim wording; the `rule_text` is
never changed to fit a modality. Explicit negative directive forms
(`shall not` / `is not permitted` / `are not to` / `is not to` / `not to be`) map to
`not_permitted`; `shall` maps to `shall`; `should` to `should`; `may` to `may`; the
transcription's directive style (`are to be` / `is to be` / `is required` /
`to be submitted`) maps to `shall`; everything else is `informational`. Current
distribution: `shall`=103, `informational`=74, `not_permitted`=9, `may`=4.

### 3.1 approval_class semantics and the strictest-class join rule

`approval_class` is joined from the Appendix F "Specification Reference Guide" matrix:

| Class | Meaning |
|---|---|
| A | mandatory Jemena approval |
| B | subject to variation at Jemena discretion |
| C | typically N/A unless conditions vary |

**Join rule:** where a clause has multiple Appendix F rows with differing classes, the
**strictest class wins (A > B > C)** and is applied to all atoms of that clause. For
example clause 5.3 (rows C + A) resolves to A, and clause 3.3.2 (rows A + C) resolves
to A. Clauses absent from Appendix F get `approval_required=false` and
`approval_class=null`. This rule is recorded in `manifest.json` (`appendix_f_join_rule`)
and in [`matrices/appendix-f-legend.md`](../../knowledge/jem-gen-spc-m-014/matrices/appendix-f-legend.md).

### 3.2 Quantitative limits: current-state caveat (no fabrication)

The structured limit fields `parameter` / `value` / `operator` / `unit` are
**null for all narrative obligations** today. Quantitative limits present in the source
(for example ±0.50°, 300°C, 1,000 kPag, -40°C, 7 years, 1.5 x design pressure) remain
**verbatim inside `rule_text`** and are **not yet extracted into the structured
fields**. This is a deliberate no-fabrication stance: no limit is lifted into a
structured field unless it is unambiguously present as a single field in the source,
so the only atoms that currently populate these fields are the §2.4 ranked atoms
(`parameter=order_of_precedence`, `operator=rank`, `value=<1..4>`).

Structured numeric extraction (pulling the embedded limits into
`parameter`/`value`/`operator`/`unit`) is a candidate **future enhancement**, not a
solved feature. Because `rule_text` is verbatim, no information is lost in the meantime.

### 3.3 hold_witness_point

`hold_witness_point=true` flags the Clause 3.1 HOLD / WITNESS point obligations. This
lets the ITP generator (Section 7) pick up inspection hold and witness points directly
from the atoms.

## 4. File types produced

| Artifact | Path | Purpose |
|---|---|---|
| JSONL atoms | `atoms/jem-gen-spc-m-014.atoms.jsonl` | One rule object per line (UTF-8, `ensure_ascii=False`); each line independently parses. Primary grounding corpus. |
| Per-clause Markdown mirror | `clauses/clause-<n>-<m>.md` | YAML front-matter (clause metadata) + verbatim body listing each obligation with its `rule_id` and modality. |
| Clause index | `clauses/README.md` | Lists all clause files. |
| Document manifest | `manifest.json` | Document identity, section list, counts, Appendix F join rule, provenance note, draft marker. |
| Appendix F RTM | `matrices/appendix-f-reference-guide.csv` | Rebuilds Appendix F verbatim: `clause,requirement_description,class` (55 rows). |
| Appendix F legend | `matrices/appendix-f-legend.md` | A/B/C class legend + the join rule. |
| Reference register | `matrices/reference-register.csv`, `.json` | 52 referenced standards/specs with issuer and a licensing flag. |
| Template schemas | `schemas/*.json` | Field structure of the five spec forms (no copyrighted body text). |

## 5. Granularity and fidelity rules

- **Bullet / sentence-level atoms.** A clause with N discrete obligations yields N
  atoms, each linked to its parent clause via `section` / `clause` / `clause_title`.
- **`rule_text` is verbatim.** It is never paraphrased, summarised, normalised or
  reworded. Clause numbers, limits and acceptance criteria are copied, never invented.
- **`plain_summary` never replaces `rule_text`.** It is an optional, additive aid and
  is null unless explicitly supplied.
- **Stable, unique `rule_id`.** Per-clause zero-padded R-index keeps IDs stable across
  regenerations so citations do not drift.
- **Compound-sentence limitation (known).** Many source obligations are compound
  sentences, and `informational` atoms are predominantly definitional/descriptive
  clauses (1.1, 1.3, 2.1, 2.2) or compound sentences whose leading clause is
  descriptive. A future pass may split compound obligations into finer atoms. Because
  `rule_text` is verbatim, no information is lost; this is a reviewer refinement, not a
  correctness gap.

## 6. Licensing stance

Tied to the standards-licensing open question (OQ-1): AS2885/AS4645 and other external
standards are copyrighted Standards Australia / third-party documents, so their text is
not indexed or reproduced.

| Group | Example doc IDs | Licensing | Handling |
|---|---|---|---|
| Jemena-owned | JEM-GEN-SPC-M-014, GAS-980-PR-ME-003, GTS-960-SP-ME-001, GTS-960-SP-ME-010 | `jemena_owned` | Text may be stored, atomised and grounded. |
| External standards | AS / ASME / AWS / API / EN (and ASTM) | `copyrighted_external` | **Pointers / titles only.** Body text never reproduced. |

The reference register holds 52 entries: 4 `jemena_owned` and 48 `copyrighted_external`.
External references in atoms are pointer strings (title and/or clause pointer), never
reproduced standard bodies.

## 7. How it feeds downstream

- **tech-query Copilot grounding.** The JSONL atoms are a grounding source for the
  tech-query agent. Because each atom carries `rule_id`, `clause` and `clause_title`,
  the assistant can answer a question and **cite the specific rule** (e.g.
  "`JEM-GEN-SPC-M-014:5.2.2:R02`, Clause 5.2.2") rather than a whole-document citation.
  Modality, `approval_class` and `references` let it surface whether a requirement is
  mandatory, needs Jemena approval, or points to an external standard the user must
  consult directly.
- **ITP generator.** The ITP generator consumes `hold_witness_point` atoms (Clause 3.1
  HOLD / WITNESS points) and `approval_class` to seed inspection-and-test-plan line
  items and approval gates, keeping the generated ITP traceable to the specification
  clauses.

Both consumers are part of the EKA program and are delivered via the
`eka-foundation` branch; they are named here by role.

## 8. Known source anomalies

These are preserved exactly as printed, documented rather than silently "fixed":

- **6.3.2 / 6.3.3 / 6.3.4 numbering anomaly.** Section 6.3 is published with
  **6.3.2** *Inspection and NDE of Test Welds*, **6.3.3** *Approval of Welding
  Procedures*, **6.3.4** *Repair Procedures*. The atomiser preserves this printed
  numbering and does **not** renumber it. The PWHT (post-weld heat treatment) sentence
  is kept attached to clause 6.3.2 as in the source. A test asserts the three titles so
  the anomaly cannot be silently reintroduced-as-"corrected".
- **AS 2885.2 Clause 5.13 footnote.** The source footnote is attached to clause 5.2.2 as
  a reference **pointer** `AS 2885.2 Clause 5.13 - Distance between welds`
  (`copyrighted_external`, pointer / title only). The footnote is preserved faithfully as
  a pointer; the AS 2885.2 body text is not reproduced.

## 9. Order of Precedence atoms

Clause §2.4 Order of Precedence is captured as **explicit ranked atoms** so the
assistant can resolve conflicting requirements deterministically. The ranked list is:

1. Statutory Regulations / Acts
2. Australian & International Codes and Standards
3. this Fabrication Specification
4. Datasheets and / or drawings

Each ranked atom carries `order_of_precedence_rank` (1-4) and
`parameter=order_of_precedence` / `operator=rank` / `value=<rank>`, alongside the
verbatim narrative §2.4 atom. When requirements conflict, an agent walks the ranks from
1 downward.

## 10. Engineering review notes (risk lens)

Gas T&D shop fabrication is a safety-critical, high-consequence domain. The following
are deliberate controls and open review items for a qualified engineer:

- **Verbatim fidelity is a safety control.** `rule_text` is a verbatim copy of the
  source. Reviewers should spot-check atoms against the source transcription and the
  original specification; any paraphrase would be a defect.
- **No fabricated limits.** Quantitative limits are not invented into structured fields.
  They stay verbatim inside `rule_text` (Section 3.2). Reviewers should confirm no limit
  was dropped or altered when atoms are later read programmatically.
- **Human-in-the-loop.** The corpus and anything generated from it (ITPs, procedures,
  answers) are **drafts pending qualified engineering review and sign-off**. Generated
  deliverable template schemas carry the exact marker `DRAFT — pending engineering
  review`.
- **Copyrighted-standard pointers only.** External standards (AS/ASME/AWS/API/EN) are
  referenced as pointers; reviewers must consult the licensed standards directly for the
  authoritative text. The assistant must not be expected to quote them.
- **Compound-sentence / structured-limit caveat (review item).** Compound obligations
  are not yet split, and embedded quantitative limits are not yet extracted into
  structured fields. A reviewer deciding to rely on structured numeric filtering should
  treat this as a known gap and request the follow-up extraction pass; until then,
  numeric limits must be read from `rule_text`.
- **Transmission vs distribution.** This specification is Jemena shop fabrication; keep
  AS2885 (transmission pipelines) and AS4645 (distribution networks) distinct when the
  atoms are grounded alongside other corpora.
