# JEM-GEN-SPC-M-014 Atomiser (logic prototype)

- **Title:** JEM-GEN-SPC-M-014 Atomiser
- **Version:** 0.1
- **Status:** Draft

## What it does

Reads the committed verbatim source transcription of the Jemena specification
**JEM-GEN-SPC-M-014** *Piping and Mechanical Equipment – Shop Fabrication
Specification For Facilities* (v4, 27 June 2017, supersedes P09JAM00-000SPC-M-006)
and emits a clause-by-clause, fully traceable atomised corpus optimised for an AI
assistant to read and identify rules.

Inputs (committed by FEAT-001, under `knowledge/jem-gen-spc-m-014/source/`):

- `jem-gen-spc-m-014.clauses.json` — 11 sections, 78 clauses, 186 obligations.
- `appendix-f.rows.json` — the Appendix F approval-class matrix (55 rows + legend).

Outputs (regenerated into `knowledge/jem-gen-spc-m-014/`):

| Artifact | Path |
|---|---|
| JSONL atoms (one rule per line) | `atoms/jem-gen-spc-m-014.atoms.jsonl` |
| Per-clause Markdown mirror + index | `clauses/*.md`, `clauses/README.md` |
| Document manifest | `manifest.json` |
| Appendix F RTM (CSV) + legend | `matrices/appendix-f-reference-guide.csv`, `matrices/appendix-f-legend.md` |
| Reference register (CSV + JSON) | `matrices/reference-register.csv`, `matrices/reference-register.json` |
| Template schemas (5 forms) | `schemas/*.json` |

## Atom schema (one obligation = one atom)

| Field | Notes |
|---|---|
| `rule_id` | Stable `JEM-GEN-SPC-M-014:<clause>:R<nn>` (zero-padded per clause). |
| `doc_id`, `doc_version`, `doc_title`, `supersedes` | Document identity. |
| `section`, `clause`, `clause_title`, `source_page` | Parent clause traceability. |
| `rule_text` | **Verbatim** obligation text; never paraphrased. |
| `plain_summary` | Null unless supplied; never replaces `rule_text`. |
| `modality` | One of `shall` / `should` / `may` / `not_permitted` / `prohibited` / `informational`, derived deterministically from wording. |
| `parameter`, `value`, `operator`, `unit` | Null unless a quantitative limit is explicitly present in the source. Not fabricated; units are not converted. |
| `applies_to`, `references`, `cross_references` | Scope list, external reference pointers, in-doc clause links. |
| `hold_witness_point` | `true` for the Clause 3.1 HOLD/WITNESS points. |
| `approval_required`, `approval_class` | Joined from Appendix F; class is `A`/`B`/`C` or null. |
| `order_of_precedence_rank` | Set on the ranked §2.4 Order-of-Precedence atoms. |

### Deterministic rules

- **Modality** is derived from the verbatim wording (explicit transcription
  hints win); the `rule_text` is never altered.
- **Appendix F join:** where a clause has multiple Appendix F rows with differing
  classes, the **strictest class (A > B > C)** is applied to that clause's atoms.
- **Order of Precedence (§2.4)** is emitted as explicit ranked atoms so an agent
  can resolve conflicts.
- The **6.3.2 / 6.3.3 / 6.3.4 clause-numbering anomaly** is preserved as printed.

## Safety rules

- `rule_text` is verbatim from the source; clause numbers, limits and acceptance
  criteria are never invented or paraphrased.
- Copyrighted external standards (AS/ASME/AWS/API/EN) are captured as reference
  **pointers / titles only**; their body text is never reproduced. Only
  JEM-/GAS-/GTS- (Jemena-owned) documents may be atomised/grounded.
- Generated deliverable template schemas carry the exact marker
  `DRAFT — pending engineering review`; every deliverable requires qualified
  engineer review and sign-off.

## Run

```sh
# Regenerate the full corpus into knowledge/jem-gen-spc-m-014/
python3 atomiser.py

# Write to an alternative output directory
python3 atomiser.py --out /tmp/eka-out

# Dry run: print the JSONL atoms to stdout, write nothing
python3 atomiser.py --stdout-jsonl
```

## Test

```sh
cd prototypes/atomiser
python3 -m unittest discover -p 'test_*.py' -v
```

## Scope note

Python **standard library only** — no third-party dependencies and no network
access. The sandbox is a Linux/web environment and cannot deploy to a Power
Platform tenant; this prototype validates the atomisation rules before any
low-code implementation.
