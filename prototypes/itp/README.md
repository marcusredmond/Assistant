# ITP Generator - Logic Prototype

- **Title:** Engineering Knowledge Assistant (EKA) - ITP Generation Logic Prototype
- **Version:** 0.1.0
- **Status:** Draft

A Python 3 **standard-library-only** prototype that validates the Inspection & Test Plan
(ITP) generation rules documented in [`docs/modules/itp-design.md`](../../docs/modules/itp-design.md)
**before** they are implemented in low-code (Power Automate / Power Apps). It is a design
aid, not a deployed component.

## What it does

Takes a structured activity list (JSON) describing a scope of work and produces a **draft**
ITP as markdown (or a structured JSON dict) following
[`templates/itp/itp-template.md`](../../templates/itp/itp-template.md). It enforces the
safety-critical rules:

- stamps the exact marker **`DRAFT — pending engineering review`** on every output;
- emits the exact placeholder
  `[PLACEHOLDER - acceptance criterion from licensed <standard> <clause> rev <year>]`
  whenever a standard-derived acceptance criterion is required but not supplied from a
  licensed/approved source - it **never** fabricates a clause number or criterion;
- keeps **Transmission (AS 2885 series)** and **Distribution (AS/NZS 4645 series)**
  distinct, carrying the asset-type-appropriate standard family **label** and never
  blending the two;
- defaults a missing inspection point to **Review** (never silently to Hold) and flags it
  for engineering confirmation.

## Files

| File | Purpose |
|---|---|
| `itp_generator.py` | The generator (stdlib only: `argparse`, `json`, `dataclasses`, ...). |
| `sample-activities.json` | A sample transmission activity list. |
| `test_itp_generator.py` | `unittest` suite exercising the generator logic. |

## Run the generator

From this directory (`prototypes/itp`):

```sh
python3 itp_generator.py sample-activities.json
```

Emit the structured dict as JSON instead of markdown:

```sh
python3 itp_generator.py sample-activities.json --json
```

## Run the tests

From this directory:

```sh
python3 -m unittest discover -p 'test_*.py' -v
```

The tests cover (a) line-item count/shape from input, (b) acceptance-criteria placeholders
and absence of fabricated clause numbers, (c) the DRAFT marker, and (d) transmission vs
distribution distinctness. They call the real generator functions, so they fail if the
generation logic is reverted or weakened.

## Input format

```json
{
  "title": "...",
  "project": "...",
  "asset_type": "Transmission | Distribution | Not asset-specific",
  "scope_of_work": "...",
  "revision": "A",
  "prepared_by": "...",
  "activities": [
    {
      "activity": "<required: activity/operation name>",
      "inspection_test": "<inspection or test description>",
      "inspection_point": "Hold | Witness | Review | Monitor",
      "responsibility": "<who performs/verifies>",
      "verifying_document": "<evidence document>",
      "record_form": "<record/form produced>",
      "acceptance_criteria": "<optional: verbatim criterion from a source>",
      "acceptance_source": "<required if acceptance_criteria is given>"
    }
  ]
}
```

`acceptance_criteria` is carried into the ITP **only** when `acceptance_source` is also
supplied (a verbatim, source-backed criterion). Otherwise the marked placeholder is used.
This prevents an unsourced criterion from being treated as authoritative.

## Scope note

Standard library only; no `pip` installs (the sandbox is network-restricted). All output
is a **draft** requiring qualified-engineer review and sign-off.
