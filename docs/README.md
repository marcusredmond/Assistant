# Engineering Knowledge Assistant - Design Documentation

- **Title:** EKA Design Documentation Index
- **Version:** 0.1.0
- **Status:** Draft

This directory holds the design and architecture documentation for the Engineering
Knowledge Assistant (EKA), a gas T&D engineering knowledge assistant built on the
Microsoft Power Platform with SharePoint as the document repository.

> **Sandbox note.** This is a config/design-first project. The sandbox cannot deploy to
> a Power Platform tenant; all artifacts here are declarative/design-only.

## Index

| Area | Document | Status |
|---|---|---|
| Architecture | [architecture/solution-architecture.md](architecture/solution-architecture.md) | Draft |
| Information architecture | [information-arch/information-architecture.md](information-arch/information-architecture.md) | Draft |
| Architecture index | [architecture/README.md](architecture/README.md) | Draft |
| Information-arch index | [information-arch/README.md](information-arch/README.md) | Draft |
| Per-module designs | `modules/` (created as modules start) | n/a |

## Status conventions

Every design document states its **status** in the header:

| Status | Meaning |
|---|---|
| **Draft** | Working document, not yet reviewed. |
| **In Review** | Submitted for review. |
| **Approved** | Reviewed and signed off. |

## Domain-accuracy & grounding conventions

- Compliance content **cites its source** (standard, clause/section, revision/year).
- Clause numbers, acceptance criteria, and requirements from AS2885/AS4645 (or any
  standard) are **never invented**. Where source text is unavailable, a clearly-marked
  placeholder is used: `[PLACEHOLDER - to be filled from licensed <standard> <clause> rev <year>]`.
- **AS2885 (transmission)** and **AS4645 (distribution)** are kept distinct.
- Generated deliverables are **DRAFT — pending engineering review** until a qualified
  engineer signs off.
