# EKA SharePoint Content Types (declarative)

- **Title:** Engineering Knowledge Assistant (EKA) - SharePoint Content Type Definitions
- **Version:** 0.1.0
- **Status:** Draft

## Purpose

One declarative JSON file per SharePoint content type defined in the
[information architecture](../../docs/information-arch/information-architecture.md)
section 4. These are tenant-neutral designs; the sandbox cannot deploy them. They are
written so they can be translated into a Power Platform / SharePoint solution import
(for example a `ContentType` + `Field` manifest in a SPFx/PnP provisioning template, or
a column-and-content-type sequence in a solution package).

## File format

Each file contains a single `contentType` object:

| Key | Meaning |
|---|---|
| `name` / `internalName` | Display and internal name of the content type. |
| `id` / `parentId` | Placeholder SharePoint content-type IDs. The hierarchy is encoded in the ID prefix (child IDs extend the parent ID). Real IDs are assigned on import. |
| `parentContentType` | Human-readable parent (`Document`, `Item`, or an EKA base type). |
| `group` | Content-type group in the gallery (`Engineering Knowledge Assistant`). |
| `description` | What the content type is for, with a pointer to the IA section. |
| `targetLibrary` / `targetList` | The library/list this type is bound to (see IA section 2). |
| `inheritsBaseColumns` | `true` when the type inherits the shared columns from `Base Engineering Document`. |
| `columnOverrides` | Changes to inherited columns (for example making `StandardReference` required, or setting a default). |
| `columns` | Columns added by this content type, each with `type`, `required`, and `choices`/`termSet`/`multiValue`/`defaultValue` where applicable. |

### Column types used

`Text`, `Note` (multi-line text), `Choice`, `Managed Metadata`, `DateTime`, `Person`,
`Boolean` (Yes/No), `Hyperlink`. `Managed Metadata` columns bind to a term set defined in
[`../term-sets/term-sets.json`](../term-sets/term-sets.json) via the `termSet` field.

## Content type hierarchy

```
Document (standard)
└── Base Engineering Document        base-engineering-document.json
    ├── Standards Extract            standard-extract.json
    ├── Procedure                    procedure.json
    ├── Project Document             project-document.json
    └── Generated Deliverable        generated-deliverable.json
        ├── Technical Query          generated-deliverable-technical-query.json
        ├── ITP                      generated-deliverable-itp.json
        └── Commissioning Procedure  generated-deliverable-commissioning-procedure.json

Item (standard)
└── Lesson Learned                   lesson-learned.json   (list-based; does not inherit base document columns)
```

## Column source integrity

Every `Managed Metadata` column references a term set that exists in
`../term-sets/term-sets.json`. Every other column is a standard SharePoint field type.
No content type references a term set or column that is not declared here or in the term
sets file.

## Domain-accuracy guard

- `StandardReference` is a **reference label only**; it never encodes clause text,
  acceptance criteria, or requirements.
- `ClauseSectionRef` on `Standards Extract` is populated **only** from a licensed source;
  otherwise it holds `[PLACEHOLDER - to be filled from licensed <standard> <clause> rev <year>]`.
- AS2885 (transmission) and AS4645 (distribution) stay distinct via the `Asset Type` and
  `Standard Reference` term sets.
- Generated deliverables carry `DraftMarker` = `DRAFT — pending engineering review` and
  `DocumentStatus` = `Draft` until a qualified engineer signs off (`ReviewedBy`).

## Mapping to user capabilities

| User capability | Content type | Library/list |
|---|---|---|
| Upload procedures | Procedure | Procedures |
| Upload standards extracts | Standards Extract | StandardsExtracts |
| Upload project documents | Project Document | ProjectDocuments |
| Search historical lessons learned | Lesson Learned | LessonsLearned |
| Generate technical queries | Technical Query | GeneratedDeliverables |
| Generate ITPs | ITP (+ Dataverse ITP register) | GeneratedDeliverables |
| Generate commissioning procedures | Commissioning Procedure | GeneratedDeliverables |
