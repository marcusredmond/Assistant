# EKA Dataverse Table Designs (declarative)

- **Title:** Engineering Knowledge Assistant (EKA) - Dataverse Table Designs
- **Version:** 0.1.0
- **Status:** Draft

## Purpose

Declarative, tenant-neutral designs for the **structured** data that is not well suited
to a SharePoint document library (per
[information architecture](../../docs/information-arch/information-architecture.md)
section 2 and the solution architecture grounding model). The sandbox cannot deploy these;
they are written to translate into a Power Platform solution (table + column + relationship
definitions).

## Tables

### `itp-register.json`

| Table | Role |
|---|---|
| `eka_itpregister` | Header for one generated ITP (title, project, asset type, status, draft marker, link to the SharePoint document, reviewer). |
| `eka_itplineitem` | Individual inspection/test line items belonging to a header (activity, inspection type, acceptance criteria, reference document, responsible party, record required). |

Relationship: `eka_itpregister` 1 : N `eka_itplineitem` (cascade delete). The `ITP`
content type (`schemas/content-types/generated-deliverable-itp.json`) links to the header
via `ItpRegisterId`.

> Acceptance criteria and reference-document values are populated **only** from a
> licensed/approved source. They default to
> `[PLACEHOLDER - to be filled from licensed <standard> <clause> rev <year>]` and are never
> fabricated. AS2885 (transmission) and AS4645 (distribution) stay distinct via
> `eka_assettype`.

### `technical-query-register.json`

| Table | Role |
|---|---|
| `eka_technicalquery` | Each raised technical query, its grounded draft response, source citations, asset type, capability, and review state. |

### `generation-audit.json`

| Table | Role |
|---|---|
| `eka_generationrequest` | Audit trail for every generation request across generators and the ingestion pipeline: deliverable type (`technical-query` / `itp` / `commissioning-procedure` / `ingestion`), requester, timestamp, input, template used, source citations, OQ-1 licence-gate result, output link, status, reviewer. |

> The generation flows write **only** the columns defined above. The table has no dedicated
> asset-type or project columns, so the ITP and commissioning flows record asset type and
> project inside `eka_requestinput` (a free-text memo); the transmission/distribution
> separation itself is enforced upstream by each flow's asset-type validation, not by this
> audit record.

## Conventions

- Logical names use the `eka_` publisher prefix (placeholder; set to the real prefix on import).
- Lookups to `systemuser` represent the standard Dataverse user table.
- Choice option sets mirror the managed-metadata term sets in
  [`../term-sets/term-sets.json`](../term-sets/term-sets.json) (`Document Status`,
  `Asset Type`, `Capability`) so SharePoint and Dataverse classification stay aligned.
- Status columns default to `Draft` and all generated outputs carry the
  `DRAFT — pending engineering review` marker until a qualified engineer signs off,
  enforcing the human-in-the-loop principle.
