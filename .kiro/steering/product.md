---
inclusion: always
---

# Product Overview

## What this is

An **engineering knowledge assistant** for gas transmission and distribution
(T&D) assets. It helps engineers get grounded, standards-compliant answers and
generate engineering deliverables, built on the Microsoft Power Platform with an
Autodesk Inventor integration.

## Who it serves

- **Design engineers** — design reviews, standards lookups, calculation support.
- **Construction & commissioning engineers** — ITPs, commissioning procedures,
  construction support, welding requirements.
- **Integrity / risk engineers** — risk assessments, safety management studies.
- **Field engineers** — technical queries, often on tablet/Teams.

## Capability areas

The system supports nine capability areas. These are a program of work, not a
single app — each should be designed as a composable module.

1. **AS2885 compliance** — pipeline systems (petroleum & gas).
2. **AS4645 compliance** — gas distribution networks.
3. **Commissioning procedures** — generation and guidance.
4. **Welding requirements** — WPS/PQR guidance, standards lookups.
5. **ITP generation** — Inspection & Test Plans.
6. **Design reviews** — checklists, standards cross-checks.
7. **Construction support** — on-site technical guidance.
8. **Risk assessments** — safety management studies, hazard identification.
9. **Technical queries** — general document-grounded Q&A.

## Guiding principles

- **Grounded, not generative-from-memory.** Every compliance or standards answer
  must be traceable to a source document (clause, section, revision). The
  assistant cites its sources; it never invents clause numbers or requirements.
- **Human-in-the-loop.** The assistant drafts and advises. A qualified engineer
  reviews and signs off. Generated deliverables (ITPs, risk assessments,
  procedures) are drafts pending engineering approval — label them as such.
- **Safety-critical domain.** Gas T&D is high-consequence. When uncertain, the
  assistant states uncertainty and defers to the authoritative document and the
  responsible engineer rather than guessing.
- **Modular delivery.** Deliver one capability end-to-end before expanding.

## Open questions (resolve before building the relevant module)

- **Standards licensing** — AS2885/AS4645 are copyrighted Standards Australia
  documents. Confirm licensing to index/ground AI on them before using their
  text as a knowledge source.
- **Inventor integration scope** — what data is extracted from Inventor models
  (BOM, parameters, drawing metadata) and how it reaches the Power Platform.
- **First module** — pick one capability (candidate: document-grounded
  compliance Q&A, or ITP generation) to design end-to-end first.
