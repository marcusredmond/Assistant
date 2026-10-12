"""Atomiser for JEM-GEN-SPC-M-014 (Piping and Mechanical Equipment - Shop
Fabrication Specification For Facilities).

Purpose
-------
Reads the committed source transcription of the Jemena specification (a faithful
rendering of the supplied extraction, with limits/units preserved verbatim) and
emits a fully traceable, clause-by-clause atomised corpus optimised for an AI
assistant to read and identify rules:

  * JSONL atoms            - one rule object per line (one obligation = one atom)
  * per-clause Markdown     - YAML front-matter + source body, one file / clause
  * document manifest       - counts + provenance
  * Appendix F RTM (CSV)    - the approval-class matrix, verbatim
  * reference register      - every referenced standard/spec + licensing flag
  * template schemas (JSON) - form field structure for the five appendix forms

Safety rules enforced by this module (SAFETY-CRITICAL domain)
-------------------------------------------------------------
  * rule_text is copied unchanged from the committed source obligation text. The
    source itself is a FAITHFUL RENDERING of the user-supplied (already-condensed)
    extraction, with all quantitative limits and units preserved verbatim and
    nothing invented. This module never paraphrases, rewrites, or invents rule
    text, clause numbers, limits or acceptance criteria; it emits the source text
    as-is.
  * parameter/value/operator/unit are left null unless a quantitative limit is
    explicitly present in the source; limits are NOT fabricated. (This module
    does not auto-extract numeric limits; it only carries explicit source fields.)
  * Units are kept exactly as written; nothing is converted.
  * Copyrighted external standards (AS/ASME/AWS/API/EN) are captured as reference
    POINTERS / titles only. Their body text is never reproduced. Only
    JEM-/GAS-/GTS- (Jemena-owned) documents may be atomised/grounded.
  * The clause-numbering anomaly around 6.3.2 / 6.3.3 / 6.3.4 is preserved as
    printed; it is never silently renumbered.
  * Generated deliverable template schemas carry the exact DRAFT marker string
    (see DRAFT_MARKER); every such deliverable requires qualified engineer review.

Scope note: Python standard library only. No third-party dependencies, no network.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants (exact strings - asserted by tests; do not alter casing/spacing)
# ---------------------------------------------------------------------------

DOC_ID = "JEM-GEN-SPC-M-014"
DOC_VERSION = "4"
DOC_DATE = "27 June 2017"
SUPERSEDES = "P09JAM00-000SPC-M-006"

# Required verbatim deliverable marker. The dash is a literal em dash (U+2014).
DRAFT_MARKER = "DRAFT — pending engineering review"

# Allowed modality values (tests assert membership).
MODALITIES = frozenset(
    {"shall", "should", "may", "not_permitted", "prohibited", "informational"}
)

# Appendix F approval-class ranking, strictest first (A > B > C).
APPROVAL_CLASS_RANK = {"A": 0, "B": 1, "C": 2}

# Issuer prefixes that are Jemena-owned (may be atomised/grounded).
JEMENA_PREFIXES = ("JEM", "GAS", "GTS")

# External issuers (copyrighted; pointers/titles only).
EXTERNAL_ISSUERS = ("AS", "ASME", "AWS", "API", "EN")


# ---------------------------------------------------------------------------
# Atom dataclass
# ---------------------------------------------------------------------------


@dataclass
class Atom:
    """A single atomic rule (one source obligation)."""

    rule_id: str
    doc_id: str
    doc_version: str
    doc_title: str
    supersedes: str
    section: str
    clause: str
    clause_title: str
    rule_text: str
    plain_summary: Optional[str]
    modality: str
    parameter: Optional[str]
    value: Optional[str]
    operator: Optional[str]
    unit: Optional[str]
    applies_to: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    cross_references: List[str] = field(default_factory=list)
    hold_witness_point: bool = False
    approval_required: bool = False
    approval_class: Optional[str] = None
    source_page: int = 0
    order_of_precedence_rank: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "doc_id": self.doc_id,
            "doc_version": self.doc_version,
            "doc_title": self.doc_title,
            "supersedes": self.supersedes,
            "section": self.section,
            "clause": self.clause,
            "clause_title": self.clause_title,
            "rule_text": self.rule_text,
            "plain_summary": self.plain_summary,
            "modality": self.modality,
            "parameter": self.parameter,
            "value": self.value,
            "operator": self.operator,
            "unit": self.unit,
            "applies_to": self.applies_to,
            "references": self.references,
            "cross_references": self.cross_references,
            "hold_witness_point": self.hold_witness_point,
            "approval_required": self.approval_required,
            "approval_class": self.approval_class,
            "source_page": self.source_page,
            "order_of_precedence_rank": self.order_of_precedence_rank,
        }


# ---------------------------------------------------------------------------
# Derivations (deterministic, no invention)
# ---------------------------------------------------------------------------


def derive_modality(text: str, hint: Optional[str] = None) -> str:
    """Derive modality deterministically.

    An explicit, valid transcription `modality` hint takes precedence (this is how
    mandatory acceptance criteria that the condensed source phrased descriptively
    are classified as `shall` rather than `informational`). Otherwise the modality
    is derived from the wording. The rule_text itself is never altered by this
    function.
    """
    if hint and hint in MODALITIES:
        return hint
    low = text.lower()
    # Negative / prohibitive forms first.
    if (
        "shall not be permitted" in low
        or "is not permitted" in low
        or "are not permitted" in low
        or "no cold bending is permitted" in low
        or re.search(r"\bno\b.*\bpermitted\b", low)
    ):
        return "not_permitted"
    if "shall not" in low or "must not" in low:
        return "not_permitted"
    # Unambiguous directive-negative forms ("are not to", "is not to",
    # "not to be ...") express a prohibition.
    if (
        "are not to " in low
        or "is not to " in low
        or re.search(r"\bnot to be\b", low)
    ):
        return "not_permitted"
    if re.search(r"\bprohibited\b", low):
        return "prohibited"
    if re.search(r"\bshall\b", low):
        return "shall"
    if re.search(r"\bshould\b", low):
        return "should"
    if re.search(r"\bmay\b", low):
        return "may"
    # The transcription renders most obligations in the directive "are to be" /
    # "is to be" / "is required" style, which is a shall-equivalent obligation.
    if (
        "are to be" in low
        or "is to be" in low
        or "to be submitted" in low
        or "is required" in low
        or "are required" in low
        or "is to " in low
        or "are to " in low
    ):
        return "shall"
    return "informational"


def reference_pointer(ref: Dict[str, Any]) -> str:
    """Render a reference dict as a compact external pointer string.

    Never reproduces standard body text - only identifier + (optional) clause,
    section and verbatim title where the Jemena source gives one.
    """
    std = ref.get("standard", "")
    parts = [std]
    if ref.get("clause"):
        parts.append("Clause " + str(ref["clause"]))
    if ref.get("section"):
        parts.append("Section " + str(ref["section"]))
    title = ref.get("title")
    pointer = " ".join(p for p in parts if p)
    if title:
        pointer = f"{pointer} - {title}"
    return pointer.strip()


def issuer_for(ref_id: str) -> str:
    """Classify a reference id to its issuer family."""
    rid = ref_id.strip()
    upper = rid.upper()
    for pfx in JEMENA_PREFIXES:
        if upper.startswith(pfx):
            return "Jemena"
    if upper.startswith("ASME"):
        return "ASME"
    if upper.startswith("AWS"):
        return "AWS"
    if upper.startswith("API"):
        return "API"
    if upper.startswith("EN"):
        return "EN"
    if upper.startswith("ASTM"):
        return "ASTM"
    if upper.startswith("AS"):  # AS and AS/NZS
        return "AS"
    return "Other"


def licensing_for(ref_id: str) -> str:
    """jemena_owned for JEM-/GAS-/GTS- docs; copyrighted_external otherwise."""
    upper = ref_id.strip().upper()
    for pfx in JEMENA_PREFIXES:
        if upper.startswith(pfx):
            return "jemena_owned"
    return "copyrighted_external"


# ---------------------------------------------------------------------------
# Appendix F join
# ---------------------------------------------------------------------------


def build_appendix_f_class_map(rows: List[Dict[str, Any]]) -> Dict[str, str]:
    """Return clause -> approval_class using the strictest class (A > B > C).

    Where Appendix F lists multiple rows for one clause with differing classes,
    the strictest (lowest-rank) class is applied to that clause's atoms. This
    deterministic join rule is documented in the module design doc (FEAT-003).
    """
    class_map: Dict[str, str] = {}
    for row in rows:
        clause = row["clause"]
        cls = row["class"]
        if clause not in class_map:
            class_map[clause] = cls
        else:
            if APPROVAL_CLASS_RANK[cls] < APPROVAL_CLASS_RANK[class_map[clause]]:
                class_map[clause] = cls
    return class_map


# ---------------------------------------------------------------------------
# Atomisation
# ---------------------------------------------------------------------------


def kebab_clause(clause: str) -> str:
    """clause id -> kebab file stem, e.g. '6.3.2' -> 'clause-6-3-2'."""
    return "clause-" + clause.replace(".", "-")


def build_atoms(
    source: Dict[str, Any], class_map: Dict[str, str]
) -> List[Atom]:
    doc = source["document"]
    doc_title = doc["doc_title"]
    atoms: List[Atom] = []

    for clause in source["clauses"]:
        clause_id = clause["clause"]
        section = clause["section"]
        clause_title = clause["clause_title"]
        page = int(clause.get("source_page", 0))
        approval_class = class_map.get(clause_id)
        approval_required = approval_class is not None

        for idx, ob in enumerate(clause["obligations"], start=1):
            rule_text = ob["text"]
            modality = derive_modality(rule_text, ob.get("modality"))

            refs = [reference_pointer(r) for r in ob.get("references", [])]
            cross_refs = list(ob.get("cross_references", []))
            applies_to = list(ob.get("applies_to", []))

            op_rank = None
            if "order_of_precedence" in ob:
                # Keep the obligation itself as one atom but record it is a
                # ranked precedence rule. Individual ranked items are emitted as
                # dedicated ranked atoms below.
                op_rank = None

            atom = Atom(
                rule_id=f"{DOC_ID}:{clause_id}:R{idx:02d}",
                doc_id=DOC_ID,
                doc_version=DOC_VERSION,
                doc_title=doc_title,
                supersedes=SUPERSEDES,
                section=section,
                clause=clause_id,
                clause_title=clause_title,
                rule_text=rule_text,
                plain_summary=ob.get("plain_summary"),
                modality=modality,
                parameter=ob.get("parameter"),
                value=ob.get("value"),
                operator=ob.get("operator"),
                unit=ob.get("unit"),
                applies_to=applies_to,
                references=refs,
                cross_references=cross_refs,
                hold_witness_point=bool(ob.get("hold_witness_point", False)),
                approval_required=approval_required,
                approval_class=approval_class,
                source_page=page,
                order_of_precedence_rank=op_rank,
            )
            atoms.append(atom)

            # Emit the §2.4 Order of Precedence as explicit ranked atoms so an
            # agent can resolve conflicts deterministically.
            if "order_of_precedence" in ob:
                base_count = len(clause["obligations"])
                for i, entry in enumerate(ob["order_of_precedence"], start=1):
                    ranked = Atom(
                        rule_id=f"{DOC_ID}:{clause_id}:R{base_count + i:02d}",
                        doc_id=DOC_ID,
                        doc_version=DOC_VERSION,
                        doc_title=doc_title,
                        supersedes=SUPERSEDES,
                        section=section,
                        clause=clause_id,
                        clause_title=clause_title,
                        rule_text=entry["item"],
                        plain_summary=None,
                        modality="informational",
                        parameter="order_of_precedence",
                        value=str(entry["rank"]),
                        operator="rank",
                        unit=None,
                        applies_to=[],
                        references=[],
                        cross_references=[],
                        hold_witness_point=False,
                        approval_required=approval_required,
                        approval_class=approval_class,
                        source_page=page,
                        order_of_precedence_rank=int(entry["rank"]),
                    )
                    atoms.append(ranked)

    return atoms


# ---------------------------------------------------------------------------
# Emitters
# ---------------------------------------------------------------------------


def emit_jsonl(atoms: List[Atom]) -> str:
    lines = [
        json.dumps(a.to_dict(), ensure_ascii=False, sort_keys=False)
        for a in atoms
    ]
    return "\n".join(lines) + "\n"


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    # Quote to keep special characters safe in the front-matter.
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _yaml_list(values: List[Any]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(_yaml_scalar(v) for v in values) + "]"


def emit_clause_markdown(
    clause: Dict[str, Any],
    clause_atoms: List[Atom],
    class_map: Dict[str, str],
) -> str:
    clause_id = clause["clause"]
    approval_class = class_map.get(clause_id)
    hold = any(a.hold_witness_point for a in clause_atoms)
    refs: List[str] = []
    cross: List[str] = []
    for a in clause_atoms:
        for r in a.references:
            if r not in refs:
                refs.append(r)
        for c in a.cross_references:
            if c not in cross:
                cross.append(c)

    front = [
        "---",
        f"doc_id: {_yaml_scalar(DOC_ID)}",
        f"doc_version: {_yaml_scalar(DOC_VERSION)}",
        f"clause: {_yaml_scalar(clause_id)}",
        f"clause_title: {_yaml_scalar(clause['clause_title'])}",
        f"section: {_yaml_scalar(clause['section'])}",
        f"approval_class: {_yaml_scalar(approval_class)}",
        f"approval_required: {_yaml_scalar(approval_class is not None)}",
        f"hold_witness_point: {_yaml_scalar(hold)}",
        f"source_page: {_yaml_scalar(int(clause.get('source_page', 0)))}",
        f"references: {_yaml_list(refs)}",
        f"cross_references: {_yaml_list(cross)}",
        f"atom_count: {_yaml_scalar(len(clause_atoms))}",
        "status: Draft",
        "---",
        "",
        f"# Clause {clause_id} — {clause['clause_title']}",
        "",
        f"Section {clause['section']} · {DOC_ID} v{DOC_VERSION} · "
        f"source page {clause.get('source_page', 0)}",
        "",
    ]
    if approval_class:
        front.append(
            f"**Appendix F approval class:** {approval_class} "
            f"(approval_required = true)"
        )
        front.append("")
    if hold:
        front.append("**Contains HOLD / WITNESS points.**")
        front.append("")

    front.append("## Atomic rules")
    front.append("")
    for a in clause_atoms:
        front.append(f"### {a.rule_id}")
        front.append("")
        front.append(f"- **modality:** {a.modality}")
        if a.hold_witness_point:
            front.append("- **hold_witness_point:** true")
        if a.order_of_precedence_rank is not None:
            front.append(
                f"- **order_of_precedence_rank:** {a.order_of_precedence_rank}"
            )
        if a.references:
            front.append("- **references:** " + "; ".join(a.references))
        if a.cross_references:
            front.append(
                "- **cross_references:** " + "; ".join(a.cross_references)
            )
        front.append("")
        front.append(f"> {a.rule_text}")
        front.append("")
    return "\n".join(front).rstrip() + "\n"


def emit_clauses_readme(source: Dict[str, Any]) -> str:
    lines = [
        f"# {DOC_ID} — per-clause atom mirror",
        "",
        "Status: Draft",
        "",
        "One Markdown file per clause. Each file carries YAML front-matter with "
        "clause metadata and a body listing every obligation's rule text (a "
        "faithful rendering of the source, limits/units verbatim) with its "
        "stable `rule_id` and derived modality.",
        "",
        "| Clause | Title | Section | File |",
        "|---|---|---|---|",
    ]
    for clause in source["clauses"]:
        cid = clause["clause"]
        stem = kebab_clause(cid)
        lines.append(
            f"| {cid} | {clause['clause_title']} | {clause['section']} | "
            f"[{stem}.md]({stem}.md) |"
        )
    lines.append("")
    return "\n".join(lines)


def emit_manifest(
    source: Dict[str, Any],
    atoms: List[Atom],
    appendix_f_rows: List[Dict[str, Any]],
) -> str:
    doc = source["document"]
    manifest = {
        "doc_id": DOC_ID,
        "title": doc["doc_title"],
        "version": DOC_VERSION,
        "date": DOC_DATE,
        "supersedes": SUPERSEDES,
        "issuer": doc.get("issuer"),
        "status": "Draft",
        "licensing": doc.get("licensing", "jemena_owned"),
        "sections": [
            {"number": s["number"], "title": s["title"]}
            for s in source["sections"]
        ],
        "atom_count": len(atoms),
        "clause_count": len(source["clauses"]),
        "appendix_f_row_count": len(appendix_f_rows),
        "appendix_f_join_rule": (
            "Where Appendix F lists multiple rows for one clause with differing "
            "classes, the strictest class (A > B > C) is applied to that "
            "clause's atoms."
        ),
        "provenance": (
            "Generated by prototypes/atomiser/atomiser.py from the committed "
            "source transcription under knowledge/jem-gen-spc-m-014/source/. "
            "The source is a faithful rendering of a user-provided (already "
            "condensed) PDF extraction; all quantitative limits and units are "
            "preserved verbatim and not converted, and nothing is invented. "
            "Mandatory acceptance criteria the source phrased descriptively "
            "carry an explicit modality hint so they classify as shall. "
            "Copyrighted external standards are captured as pointers/titles "
            "only. The 6.3.2/6.3.3/6.3.4 clause-numbering anomaly is preserved "
            "as printed."
        ),
        "draft_marker": DRAFT_MARKER,
    }
    return json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"


def emit_appendix_f_csv(rows: List[Dict[str, Any]]) -> str:
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["clause", "requirement_description", "class"])
    for row in rows:
        writer.writerow(
            [row["clause"], row["requirement_description"], row["class"]]
        )
    return buf.getvalue()


def emit_appendix_f_legend(appendix: Dict[str, Any]) -> str:
    legend = appendix.get("class_legend", {})
    lines = [
        f"# Appendix F — {appendix.get('title', 'Specification Reference Guide')}",
        "",
        "Status: Draft",
        "",
        f"Approval-class matrix for {DOC_ID}. The CSV sibling "
        "`appendix-f-reference-guide.csv` carries all rows verbatim.",
        "",
        "## Class legend",
        "",
        "| Class | Meaning |",
        "|---|---|",
    ]
    for cls in ("A", "B", "C"):
        if cls in legend:
            lines.append(f"| {cls} | {legend[cls]} |")
    lines.append("")
    lines.append(
        "**Join rule (atoms):** where a clause has multiple Appendix F rows "
        "with differing classes, the strictest class (A > B > C) is applied to "
        "that clause's atoms."
    )
    lines.append("")
    return "\n".join(lines)


def collect_references(source: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Collect a de-duplicated reference register from the source obligations.

    Also seeds the register with the document itself (Jemena-owned)."""
    seen: Dict[str, Dict[str, Any]] = {}

    def add(ref_id: str, title: Optional[str], licensing: Optional[str]) -> None:
        ref_id = ref_id.strip()
        if not ref_id:
            return
        existing = seen.get(ref_id)
        if existing is None:
            seen[ref_id] = {
                "ref_id": ref_id,
                "title": title,
                "issuer": issuer_for(ref_id),
                "licensing": licensing or licensing_for(ref_id),
            }
        else:
            # Prefer a non-null verbatim title if one appears later.
            if existing["title"] is None and title is not None:
                existing["title"] = title

    # The specification itself.
    add(DOC_ID, source["document"]["doc_title"], "jemena_owned")

    for clause in source["clauses"]:
        for ob in clause["obligations"]:
            for ref in ob.get("references", []):
                std = ref.get("standard", "")
                add(std, ref.get("title"), ref.get("licensing"))

    return [seen[k] for k in sorted(seen.keys())]


def emit_reference_register_json(refs: List[Dict[str, Any]]) -> str:
    payload = {
        "doc_id": DOC_ID,
        "status": "Draft",
        "note": (
            "Reference register for " + DOC_ID + ". Copyrighted external "
            "standards (AS/ASME/AWS/API/EN/ASTM) are pointers/titles only; "
            "their body text is never reproduced. JEM-/GAS-/GTS- documents are "
            "Jemena-owned."
        ),
        "references": refs,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def emit_reference_register_csv(refs: List[Dict[str, Any]]) -> str:
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ref_id", "title", "issuer", "licensing"])
    for r in refs:
        writer.writerow(
            [
                r["ref_id"],
                "" if r["title"] is None else r["title"],
                r["issuer"],
                r["licensing"],
            ]
        )
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Template schemas (field structure only; no copyrighted standard text)
# ---------------------------------------------------------------------------


def _schema(
    schema_id: str,
    title: str,
    form_number: str,
    revision: Optional[str],
    is_generated_deliverable: bool,
    fields: Any,
) -> Dict[str, Any]:
    schema: Dict[str, Any] = {
        "$schema": "https://json-schema.org/draft-07/schema#",
        "schemaId": schema_id,
        "title": title,
        "formNumber": form_number,
        "sourceDoc": DOC_ID,
        "status": "Draft",
    }
    if revision is not None:
        schema["revision"] = revision
    if is_generated_deliverable:
        schema["draftMarkerGuidance"] = DRAFT_MARKER
    schema["fields"] = fields
    return schema


def build_template_schemas() -> Dict[str, Dict[str, Any]]:
    schemas: Dict[str, Dict[str, Any]] = {}

    # Appendix A — Technical Query Form (generated deliverable).
    schemas["technical-query-form.json"] = _schema(
        "technical-query-form",
        "Technical Query Form (Appendix A)",
        "ES.DEG.FORM.009",
        "Rev A",
        True,
        {
            "header": [
                "Project",
                "TQ No",
                "Project No",
                "Date",
                "Originators Name",
                "Answer by (Immediate / 24 hrs / 1 week)",
                "Originator's Company/Dept",
                "Recipient",
                "Title of Query",
                "Area Affected",
                "Documents/Drawings Affected",
            ],
            "query": ["Query Description", "Originator", "Date"],
            "review": ["Reviewed by", "Date"],
            "answer": [
                "Answer (Comment / Approval)",
                "Recipient Signature",
                "Date",
            ],
            "furtherAction": [
                "Further Action (Yes/No)",
                "Action Required",
                "Originator Signature",
                "Date",
            ],
            "variationControl": [
                "Scope Change Required (Yes/No)",
                "Change No",
                "Project Manager Signature",
                "Date",
            ],
        },
    )

    # Appendix C — Mechanical Inspection Record (generated deliverable).
    mir_groups = [
        {"group": "1 Filters", "items": ["1.1", "1.2", "1.3", "1.4"]},
        {"group": "2 Regulators", "items": ["2.1", "2.2"]},
        {"group": "3 Pilots", "items": ["3.1", "3.2", "3.3"]},
        {"group": "4 Relief valves", "items": ["4.1", "4.2", "4.3", "4.4", "4.5"]},
        {"group": "5 Valves", "items": ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6"]},
        {"group": "6 Non Return Valves", "items": ["6.1", "6.2"]},
        {"group": "7 Pipe Work", "items": ["7.1", "7.2", "7.3", "7.4"]},
        {"group": "8 Small Bore Pipe Work", "items": ["8.1", "8.2", "8.3"]},
        {"group": "9 Pressure Gauges", "items": ["9.1", "9.2"]},
        {
            "group": "10 Electrical/Instrumentation",
            "items": ["10.1", "10.2", "10.3"],
        },
        {"group": "11 Paint Work", "items": ["11.1", "11.2"]},
        {"group": "12 Skid", "items": ["12.1", "12.2"]},
        {"group": "13 Tagging", "items": ["13.1", "13.2"]},
    ]
    schemas["mechanical-inspection-record.json"] = _schema(
        "mechanical-inspection-record",
        "Mechanical Inspection Record (Appendix C)",
        "JAM-GEN-FM-M-001",
        "Rev 0",
        True,
        {
            "header": [
                "Project No",
                "Site",
                "Inspection Date",
                "Inspector Name",
                "Contractor Name",
                "Jemena Specification / reference drawings",
            ],
            "itemResponseOptions": ["Yes", "No", "N/A", "Comments"],
            "itemGroups": mir_groups,
            "signoff": ["Inspector's Signature"],
        },
    )

    # Appendix D — Punchlist (generated deliverable).
    schemas["punchlist.json"] = _schema(
        "punchlist",
        "Punchlist Template (Appendix D)",
        "JAM-GEN-FM-M-002",
        "Rev 0",
        True,
        {
            "header": [
                "Project No",
                "Site",
                "Inspection Date",
                "Inspector Name",
                "Contractor Name",
                "Jemena Specification / reference drawings",
            ],
            "tables": [
                {
                    "name": "Nonconformances recorded on Mechanical Inspection Record",
                    "columns": [
                        "Item No",
                        "Description of Defect",
                        "Defect Rectified (Signature)",
                        "Date",
                    ],
                },
                {
                    "name": "Other nonconformances identified by Jemena",
                    "columns": [
                        "Item No",
                        "Description of Defect",
                        "Defect Rectified (Signature)",
                        "Date",
                    ],
                },
            ],
        },
    )

    # Appendix E — Factory/Commissioning Acceptance Test Record (deliverable).
    setpoint_rows = [
        "Active Control Pilot Setting",
        "1st Stage Pilot Setting",
        "2nd Stage Cut Setting",
        "Monitor Override Pilot Setting",
        "Active Regulator Lock Up",
        "Monitor Regulator Lock Up",
        "Slamshut Setting",
        "Relief Valve Setting",
    ]
    schemas["factory-commissioning-acceptance-test-record.json"] = _schema(
        "factory-commissioning-acceptance-test-record",
        "Factory/Commissioning Acceptance Test Record (Appendix E) — "
        "Trunk and Primary Regulating Stations",
        "JAM-GEN-FM-M-003",
        "Rev 0",
        True,
        {
            "header": [
                "Project No",
                "Date of Test",
                "Site",
                "Serial Numbers (Run 1)",
                "Serial Numbers (Run 2)",
            ],
            "equipment": [
                "Regulators (Active)",
                "Regulators (Monitor)",
                "Pilots (1st Stage)",
                "Pilots (Monitor Override)",
                "Pilots (Active)",
                "Filter",
                "Slam Shuts",
                "Outlet Relief Valves",
            ],
            "setpointChecks": {
                "columns": [
                    "P&ID Setpoint kPa",
                    "Actual Setpoint Achieved",
                    "Comments",
                ],
                "runs": ["RUN 1", "RUN 2"],
                "rows": setpoint_rows,
            },
            "finalStatus": [
                "Skid commissioning complete",
                "Positive nitrogen pressure 30 kPa",
                "Inlet/outlet blank flanged",
            ],
            "witnessVerification": {
                "roles": [
                    "Verified by Supv/Subcontractor",
                    "Verified by Project",
                    "Reviewed by QA/QC Ind./Third Party",
                ],
                "columns": ["Print Name", "Organisation", "Date"],
            },
        },
    )

    # Appendix G — Shop Fabrication Compliance Checklist (not a Jemena form #).
    schemas["appendix-g-shop-fabrication-compliance-checklist.json"] = _schema(
        "appendix-g-shop-fabrication-compliance-checklist",
        "Shop Fabrication Compliance Checklist (Appendix G)",
        "Appendix G",
        None,
        False,
        {
            "header": [
                "Project Name",
                "Contractor",
                "Fabrication Sub-contractor",
                "Date of contract commencement",
                "Jemena Project Manager",
                "Jemena Quality Manager",
            ],
            "tableColumns": [
                "Clause(s)",
                "Items requiring evidence",
                "Document #",
                "Checked by",
            ],
            "rows": [
                {"clauses": "3.1", "item": "Fabricator's CQS"},
                {"clauses": "3.1", "item": "External inspection body (if no CQS)"},
                {"clauses": "3.1", "item": "ITP"},
                {
                    "clauses": "3.2 & 11.2",
                    "item": "Material Control Procedure",
                    "subItems": [
                        "Goods receipt",
                        "Traceability of sub-contractors' material",
                        "Marking and identification",
                        "Handling",
                        "Storage incl quarantine",
                        "Packing and transport",
                    ],
                },
                {"clauses": "5.4.2", "item": "Bolt torque procedure"},
                {"clauses": "6.1", "item": "Welding WPS"},
                {"clauses": "6.1", "item": "Welding WPQR"},
                {"clauses": "7.3.1", "item": "Weld Sentencing report"},
                {"clauses": "8.2", "item": "Testing procedure"},
                {"clauses": "8.3", "item": "Drying procedure"},
                {
                    "clauses": "9",
                    "item": "Coating Inspection report AS2312/3894.10",
                },
                {"clauses": "10.4", "item": "MDR"},
            ],
        },
    )

    return schemas


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def repo_root() -> Path:
    """Resolve the repo root relative to this script file (prototypes/atomiser)."""
    return Path(__file__).resolve().parents[2]


def default_source_dir() -> Path:
    return repo_root() / "knowledge" / "jem-gen-spc-m-014" / "source"


def default_out_dir() -> Path:
    return repo_root() / "knowledge" / "jem-gen-spc-m-014"


def load_sources(source_dir: Path):
    source = json.loads(
        (source_dir / "jem-gen-spc-m-014.clauses.json").read_text(
            encoding="utf-8"
        )
    )
    appendix = json.loads(
        (source_dir / "appendix-f.rows.json").read_text(encoding="utf-8")
    )
    return source, appendix


def generate(
    source: Dict[str, Any],
    appendix: Dict[str, Any],
    out_dir: Path,
) -> Dict[str, int]:
    rows = appendix["rows"]
    class_map = build_appendix_f_class_map(rows)
    atoms = build_atoms(source, class_map)

    atoms_dir = out_dir / "atoms"
    clauses_dir = out_dir / "clauses"
    matrices_dir = out_dir / "matrices"
    schemas_dir = out_dir / "schemas"
    for d in (atoms_dir, clauses_dir, matrices_dir, schemas_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Emitter 1 - JSONL atoms.
    (atoms_dir / "jem-gen-spc-m-014.atoms.jsonl").write_text(
        emit_jsonl(atoms), encoding="utf-8"
    )

    # Emitter 2 - per-clause Markdown mirror + index.
    atoms_by_clause: Dict[str, List[Atom]] = {}
    for a in atoms:
        atoms_by_clause.setdefault(a.clause, []).append(a)
    for clause in source["clauses"]:
        cid = clause["clause"]
        md = emit_clause_markdown(clause, atoms_by_clause[cid], class_map)
        (clauses_dir / f"{kebab_clause(cid)}.md").write_text(
            md, encoding="utf-8"
        )
    (clauses_dir / "README.md").write_text(
        emit_clauses_readme(source), encoding="utf-8"
    )

    # Emitter 3 - manifest.
    (out_dir / "manifest.json").write_text(
        emit_manifest(source, atoms, rows), encoding="utf-8"
    )

    # Emitter 4 - Appendix F RTM CSV + legend.
    (matrices_dir / "appendix-f-reference-guide.csv").write_text(
        emit_appendix_f_csv(rows), encoding="utf-8"
    )
    (matrices_dir / "appendix-f-legend.md").write_text(
        emit_appendix_f_legend(appendix), encoding="utf-8"
    )

    # Emitter 5 - reference register (CSV + JSON).
    refs = collect_references(source)
    (matrices_dir / "reference-register.csv").write_text(
        emit_reference_register_csv(refs), encoding="utf-8"
    )
    (matrices_dir / "reference-register.json").write_text(
        emit_reference_register_json(refs), encoding="utf-8"
    )

    # Emitter 6 - template schemas.
    schemas = build_template_schemas()
    for fname, schema in schemas.items():
        (schemas_dir / fname).write_text(
            json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return {
        "atom_count": len(atoms),
        "clause_count": len(source["clauses"]),
        "appendix_f_row_count": len(rows),
        "reference_count": len(refs),
        "schema_count": len(schemas),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Atomise JEM-GEN-SPC-M-014 into a clause-traceable corpus (atoms, "
            "clause mirror, manifest, Appendix F RTM, reference register, "
            "template schemas)."
        )
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=default_source_dir(),
        help="Directory holding the source transcription JSON files.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=default_out_dir(),
        help="Output directory (defaults to knowledge/jem-gen-spc-m-014).",
    )
    parser.add_argument(
        "--stdout-jsonl",
        action="store_true",
        help="Dry run: print the JSONL atoms to stdout, write nothing.",
    )
    args = parser.parse_args(argv)

    source, appendix = load_sources(args.source_dir)

    if args.stdout_jsonl:
        rows = appendix["rows"]
        class_map = build_appendix_f_class_map(rows)
        atoms = build_atoms(source, class_map)
        print(emit_jsonl(atoms), end="")
        return 0

    counts = generate(source, appendix, args.out)
    print(
        "Atomised {doc}: atom_count={a}, clause_count={c}, "
        "appendix_f_row_count={f} (references={r}, schemas={s}) -> {out}".format(
            doc=DOC_ID,
            a=counts["atom_count"],
            c=counts["clause_count"],
            f=counts["appendix_f_row_count"],
            r=counts["reference_count"],
            s=counts["schema_count"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
