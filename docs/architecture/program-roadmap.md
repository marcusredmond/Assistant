# Engineering Knowledge Assistant - Program Roadmap

- **Title:** Engineering Knowledge Assistant (EKA) - Program Roadmap
- **Version:** 0.1.0
- **Status:** Draft
- **Audience:** Solution architects, Power Platform makers, engineering leads, program sponsors
- **Depends on:** [Solution Architecture](solution-architecture.md),
  [Information Architecture](../information-arch/information-architecture.md)

> **Scope note.** Design artifact only. The sandbox cannot deploy to a Power Platform
> tenant; everything here is declarative / design-only. This roadmap sequences the program
> of work and makes the two hard open-question preconditions (standards licensing and
> Inventor integration scope) explicit per module. It does not resolve them.

---

## 1. Program shape

EKA is a **program of composable modules**, not a single app. The foundation (solution +
information architecture + ingestion) is a prerequisite for every capability module, and
each capability module ships **end-to-end before the next begins** (modular-delivery
principle from the product definition). This roadmap covers **all nine** product capability
areas and marks which are delivered by the current foundation task and which remain.

The nine capability shorthands: `as2885`, `as4645`, `commissioning`, `welding`, `itp`,
`design-review`, `construction`, `risk-assessment`, `tech-query`.

---

## 2. Hard preconditions (open questions)

Two open questions from the product definition and
[solution-architecture section 8](solution-architecture.md#8-assumptions-risks--open-questions)
are **hard preconditions** for specific modules. They are not silently decided.

| Ref | Open question | Status | Blocks |
|---|---|---|---|
| **OQ-1** | **Standards licensing** - AS2885 / AS4645 are copyrighted Standards Australia documents; confirm licensing to index / ground AI on their text. | **Unresolved** | **Hard precondition** for grounding on standard **text** in `as2885`, `as4645`, and `welding` (standards lookups), and for standards cross-checks in `design-review`. Until confirmed, those modules cannot ground on standard clauses and must use clearly-marked placeholders. |
| **OQ-2** | **Inventor integration scope** - what is extracted (BOM, parameters, drawing metadata) and how it reaches the platform. | **Unresolved** | **Precondition** for any module needing model / BOM data: the CAD-seeded portions of `itp`, `commissioning`, `construction`, and CAD-grounded `tech-query`. Does not block document-grounded Q&A or the structural generators. |
| OQ-3 | First-module selection. | Recommendation offered (`tech-query` first, `itp` first generator); team to confirm. | Sequencing only. |

> **OQ-1 is a hard precondition for `as2885`, `as4645`, and `welding` standards grounding.
> OQ-2 is a precondition for every model / BOM-dependent module.** These modules can begin
> design and non-standards scaffolding earlier, but cannot be completed and grounded until
> the respective open question is resolved.

---

## 3. Delivered by this task

| Area | Shorthand | What was delivered | Status |
|---|---|---|---|
| Foundation | - | Solution architecture, information architecture, SharePoint content types, term sets, Dataverse table designs, document ingestion flow (upload backbone for procedures / standards extracts / project documents / lessons learned). | Delivered (Draft) |
| Technical queries + document-grounded Q&A | `tech-query` | Module design, Copilot Studio agent + topic designs (ask / search lessons / generate TQ), technical-query template. Serves: ask engineering questions, search lessons learned, generate technical queries. | Delivered (Draft) |
| Lessons-learned search | (within `tech-query`) | Lesson Learned content type + search topic. | Delivered (Draft) |
| ITP generation | `itp` | Module design, ITP template, generation flow spec + definition, Python-stdlib logic prototype with unit tests, ITP register (Dataverse). | Delivered (Draft) |
| Commissioning procedures | `commissioning` | Module design, procedure template, generation flow spec + definition. | Delivered (Draft) |

All delivered artifacts are **Draft** design artifacts for implementation and
qualified-engineer review in the target tenant.

---

## 4. Remaining modules

Each remaining module below lists a one-paragraph scope, its dependencies, and its blocking
preconditions. The standards-grounded modules (`as2885`, `as4645`, `welding`,
`design-review`) all share the OQ-1 hard precondition.

### 4.1 `as2885` - AS2885 compliance (transmission)

- **Scope.** Compliance support for **transmission** pipeline systems (petroleum & gas) under
  the `AS 2885` series: grounded Q&A, compliance checks, and clause-referenced guidance for
  transmission assets, kept strictly distinct from distribution. Builds on the `tech-query`
  grounding foundation with transmission-specific retrieval and citation.
- **Dependencies.** Foundation (ingestion + IA + Copilot grounding), `tech-query` grounding
  pattern, licensed AS2885 standards extracts ingested with `LicenceConfirmed = Yes`.
- **Blocking preconditions.** **OQ-1 (hard)** - cannot ground on AS2885 clause text until
  licensing is confirmed; until then operates in placeholder mode. Must preserve the
  AS2885 / AS4645 separation.

### 4.2 `as4645` - AS4645 compliance (distribution)

- **Scope.** Compliance support for **distribution** gas networks under the `AS/NZS 4645`
  series: grounded Q&A, compliance checks, and clause-referenced guidance for distribution
  assets, kept strictly distinct from transmission. Mirrors `as2885` but on the distribution
  standard family.
- **Dependencies.** Foundation, `tech-query` grounding pattern, licensed AS/NZS 4645 standards
  extracts ingested with `LicenceConfirmed = Yes`.
- **Blocking preconditions.** **OQ-1 (hard)** - cannot ground on AS/NZS 4645 clause text until
  licensing is confirmed. Must preserve the AS2885 / AS4645 separation (distinct scope,
  taxonomy, and retrieval).

### 4.3 `welding` - Welding requirements

- **Scope.** WPS / PQR guidance and welding standards lookups: grounded answers on welding
  procedure and welder qualification requirements, feeding welding / NDT inspection points in
  ITPs. Welding standards are recorded under `Standard Reference = Other`.
- **Dependencies.** Foundation, `tech-query` grounding pattern; downstream link to `itp` for
  welding / NDT inspection points.
- **Blocking preconditions.** **OQ-1 (hard)** for grounding on the applicable welding
  standard's text; until then operates in placeholder mode on company-controlled WPS / PQR
  documents.

### 4.4 `design-review` - Design reviews

- **Scope.** Design-review checklists and standards cross-checks: structured checklists and
  grounded cross-checks against the applicable standard family for the asset type, surfacing
  lessons learned relevant to the design under review.
- **Dependencies.** Foundation, `tech-query` grounding + lessons-learned search; the generator
  pattern (`itp` / `commissioning`) for checklist deliverables.
- **Blocking preconditions.** **OQ-1 (hard)** for the standards-cross-check portion
  (AS2885 / AS4645 clause text); the checklist structure and lessons-learned surfacing can be
  built without it.

### 4.5 `construction` - Construction support

- **Scope.** On-site technical guidance for construction: grounded Q&A for field engineers
  (tablet / Teams) on construction methods, drawing / project-document lookups, and
  surfacing of relevant procedures and lessons learned.
- **Dependencies.** Foundation, `tech-query` grounding pattern; `ProjectDocuments` grounding
  (may include Inventor exports).
- **Blocking preconditions.** **OQ-2** for any CAD / BOM-dependent lookups (model-derived
  data); document-grounded field guidance proceeds without it. **OQ-1** only where answers
  need standard clause text.

### 4.6 `risk-assessment` - Risk assessments

- **Scope.** Safety management studies and hazard identification: structured risk-assessment
  deliverables (hazard identification, consequence / likelihood capture) generated from
  structured inputs, grounded on cited procedures and surfacing relevant lessons learned.
  Reuses the generator + human-in-the-loop pattern.
- **Dependencies.** Foundation, `tech-query` grounding + lessons-learned search, the generator
  pattern (`itp` / `commissioning`).
- **Blocking preconditions.** None that are hard: builds on company-controlled procedures and
  lessons learned. **OQ-1** only where a risk control references standard clause text; **OQ-2**
  only where model / BOM data seeds the asset description.

---

## 5. Recommended delivery order

Sequenced to validate the foundation earliest, deliver value without being blocked by OQ-1,
and defer the standards-grounded modules until licensing is confirmed. Each module ships
end-to-end before the next begins.

| Order | Module | Rationale | Gated by |
|---|---|---|---|
| 1 (done) | `tech-query` | Exercises the whole foundation (ingestion -> IA -> Copilot grounding + citations); delivers value without OQ-1. | - |
| 2 (done) | `itp` | First generator; structured output; exercises human-in-the-loop. | OQ-2 for CAD-seeded activities only |
| 3 (done) | `commissioning` | Second generator; reuses the `itp` pattern. | OQ-2 for model-seeded scope only |
| 4 | `risk-assessment` | Generator + lessons-learned; not blocked by OQ-1. | none hard |
| 5 | `construction` | Document-grounded field guidance; not blocked by OQ-1. | OQ-2 for CAD lookups |
| 6 | `design-review` | Checklists first; standards cross-check added once OQ-1 confirmed. | OQ-1 for cross-checks |
| 7 | `as2885` | Transmission standards grounding. | **OQ-1 (hard)** |
| 8 | `as4645` | Distribution standards grounding. | **OQ-1 (hard)** |
| 9 | `welding` | Welding standards lookups; feeds `itp` welding / NDT points. | **OQ-1 (hard)** |

> The standards-grounded modules (`as2885`, `as4645`, `welding`, and the cross-check portion
> of `design-review`) are deliberately **last** because they depend on resolving **OQ-1**. If
> licensing is confirmed earlier, they can be brought forward, but they must not be shipped
> grounding on unlicensed standard text. Likewise, any module's model / BOM-dependent portion
> must wait on **OQ-2**.

---

## 6. Modular-delivery principle

- Deliver **one capability end-to-end** (module design + declarative artifacts + template /
  flow / agent as applicable) **before** expanding to the next.
- Reuse established patterns: the `tech-query` grounding + citation pattern and the
  `itp` / `commissioning` generator + human-in-the-loop pattern are the two templates every
  later module instantiates.
- Keep AS2885 (transmission) and AS/NZS 4645 (distribution) distinct in scope, taxonomy,
  grounding, and generation throughout.
- Treat every generated engineering deliverable as a **DRAFT — pending engineering review**
  until a qualified engineer signs off.
