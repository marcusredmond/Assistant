# EKA tech-query prototype (local, offline Q&A app)

- **Title:** Engineering Knowledge Assistant (EKA) — `tech-query` local prototype
- **Version:** 0.1.0
- **Status:** Draft

## What this is

A small, self-contained browser app that lets you try the grounded engineering
Q&A for yourself. Type an engineering question and get back the governing rule,
quoted **verbatim**, with its clause + `rule_id` citation, grounded on the
atomised **JEM-GEN-SPC-M-014** "Piping and Mechanical Equipment – Shop Fabrication
Specification For Facilities" (version 4) corpus.

It stands in for the designed Copilot Studio `tech-query` agent
([`agents/tech-query/agent-design.md`](../../agents/tech-query/agent-design.md))
so the grounding and citation behaviour can be demonstrated locally. It is a
**demonstration prototype**, not a product and not a deployment.

A second tab shows a read-only **Hold & witness / approvals checklist**: the
inspection hold/witness-point obligations and the Appendix F approval-class
obligations drawn verbatim from the corpus.

## Two ways to run it

### Option A — zero-setup, double-click (no Python, no server, no internet)

Open **`tech-query-standalone.html`** by double-clicking it. It opens in your
browser straight from the file system (`file://`). There is nothing to install,
no server to start, and no internet connection required. The entire corpus is
embedded in that one file and all retrieval runs in the browser.

Use this if you are on a locked-down PC with no dev tools, or if you tried the
server option and saw *"localhost refused to connect"* (that error means no
server was running; this file needs no server at all).

### Option B — run the local server (needs Python)

```
cd prototypes/tech-query-app && python3 server.py
```

Then open **http://localhost:8000** in your browser.

- Default port: **8000**. Override with `PORT=8080 python3 server.py` if 8000 is busy.
- Stop with `Ctrl+C`.
- Requires Python 3 only (tested on 3.11). No install step.

> Both options use the identical deterministic retrieval, citation format, and
> guardrails; only the delivery differs (one embeds the data and runs in the
> browser, the other serves it from a local Python process).

## Regenerating the standalone file

`tech-query-standalone.html` is **generated**, not hand-written. It is produced
from the committed corpus by a small stdlib script:

```
cd prototypes/tech-query-app && python3 build_standalone.py
```

The generator reads
`knowledge/jem-gen-spc-m-014/atoms/jem-gen-spc-m-014.atoms.jsonl`, embeds all
192 atoms into a `<script type="application/json" id="eka-atoms">` block, and
writes the single HTML file. It is deterministic and idempotent (re-running
produces byte-identical output), so the committed HTML stays in sync with the
corpus and shows no spurious diff.

## How retrieval works (grounded + deterministic, not generative)

Retrieval is a simple, transparent, **deterministic** keyword score — not a
language model and not generative. On a query the server tokenises your words
(lowercase, a tiny visible stop-word list) and scores every atom by weighted
token overlap over four fields:

| Field | Weight per matched token |
|---|---|
| `clause` (direct clause-number match, e.g. `6.5.7`) | 6 |
| `clause_title` | 4 |
| `applies_to` | 2 |
| `rule_text` | 1 |

Atoms scoring at or above the threshold are returned, highest first (ties break
by clause then `rule_id`, so ordering is stable). Each returned answer renders:

- the governing `rule_text` **verbatim** (units and symbols such as the en dash
  `–` and `300°C` are preserved exactly, never converted);
- the citation in the exact form
  `JEM-GEN-SPC-M-014 Clause X.Y (rule_id JEM-GEN-SPC-M-014:X.Y:Rnn)`;
- the clause title and source page;
- the **modality** with its plain meaning (`shall` = mandatory, `should` =
  recommended, `may` = permitted, `not_permitted`/`prohibited` = disallowed,
  `informational` = context);
- the **Appendix F approval class** with meaning **only when** `approval_required`
  is true (A = mandatory Jemena approval; B = subject to variation at Jemena
  discretion; C = typically N/A unless conditions vary);
- a **hold / witness** flag only when `hold_witness_point` is true;
- `cross_references` and referenced external standards (named as **pointers
  only** — their text is never reproduced), only when present.

## Grounding / no-fabrication guarantees

- **Answers come only from the corpus.** The app loads the 192 atoms from
  [`knowledge/jem-gen-spc-m-014/atoms/jem-gen-spc-m-014.atoms.jsonl`](../../knowledge/jem-gen-spc-m-014/atoms/jem-gen-spc-m-014.atoms.jsonl)
  and answers only from them.
- **It never invents.** No clause numbers, limits, or acceptance criteria are
  synthesised. Quantitative values live verbatim inside `rule_text`; the app does
  not derive or restate them.
- **Honest no-answer path.** If nothing matches above the threshold, the app says
  so plainly and tells you to defer to the responsible engineer and the
  authoritative JEM-GEN-SPC-M-014 document. (Try a nonsense query to see this.)
- **Copyrighted standards are pointers only.** External standards named in an
  atom's `references[]` are shown by name; their text is never reproduced.
- **AS 2885 (transmission) and AS/NZS 4645 (distribution) are kept distinct.**
  This corpus is Jemena shop-fabrication scope and is neither network standard.
- **Drafts, not sign-off.** Any deliverable-style output (the checklist view)
  carries the verbatim marker `DRAFT — pending engineering review`. All outputs
  are drafts for qualified-engineer review.

## Offline / no-dependency guarantee

- **Python standard library only.** No third-party packages, no `pip install`.
  (The standalone file needs no Python at all once generated.)
- **No network, no CDNs.** Neither the server UI nor the standalone file loads
  any external fonts, scripts, or styles. The standalone file makes no network
  calls whatsoever and runs with the network fully off; the only URL the server
  prints is the `http://localhost` address of this very server.

## It does not deploy to Power Platform

This prototype **cannot and does not** deploy to a Power Platform / Microsoft 365
tenant. The sandbox has no tenant connection. The app runs entirely on your local
machine for demonstration. The deployable, declarative design for the real agent
lives under [`agents/tech-query/`](../../agents/tech-query/).

## Tests

```
cd prototypes/tech-query-app && python3 -m unittest
```

This runs both suites:

- `test_server.py` imports the server module without binding a port and asserts:
  the corpus loads to 192 atoms; `interpass` returns the `6.5.7:R02` atom as the
  top hit with `300°C` in its verbatim `rule_text` and the exact citation;
  `deviation` returns `2.3:R01` with `approval_class` `C` and `approval_required`
  true; a nonsense query returns no hits (the no-answer path); and every
  `rule_id` the search can return is a real corpus `rule_id`.
- `test_standalone.py` regenerates the standalone HTML and asserts: it embeds
  exactly 192 atoms whose `rule_id`s round-trip to the JSONL corpus; it
  references **no** external resources (no off-box `src`/`href`/`url()`, no CDN,
  no `fetch(`/`XMLHttpRequest`); it carries the verbatim `DRAFT — pending
  engineering review` marker and the exact citation format; it embeds the
  `6.5.7:R02` atom with `300°C`; and the generator is idempotent.

## Files

| File | Role |
|---|---|
| `server.py` | Stdlib HTTP server: loads the corpus, serves `index.html`, exposes `/api/search` and `/api/checklist`. Contains the pure, importable `load_atoms` / `search` functions and the inline UI. |
| `build_standalone.py` | Stdlib generator that embeds the 192-atom corpus into `tech-query-standalone.html`, reimplementing the identical retrieval/rendering in inline vanilla JS. Deterministic + idempotent. |
| `tech-query-standalone.html` | **Generated.** The single, double-clickable, offline app. Embeds the corpus; no server, no Python, no internet. |
| `test_server.py` | Stdlib `unittest` suite for the server. |
| `test_standalone.py` | Stdlib `unittest` suite for the generated standalone file. |
| `README.md` | This file. |
