#!/usr/bin/env python3
"""ITP (Inspection & Test Plan) draft generator - logic prototype.

Validates the ITP generation rules documented in
``docs/modules/itp-design.md`` BEFORE they are implemented in low-code
(Power Automate / Power Apps). Standard library only - no third-party deps.

The generator takes a structured activity list (JSON) describing a scope of
work and produces a DRAFT ITP as a structured dict and as markdown following
``templates/itp/itp-template.md``.

Safety-critical rules enforced here (see steering domain-accuracy):

* Never fabricate a clause number or acceptance criterion. When a standard-
  derived acceptance criterion is required but not supplied from a licensed
  source, emit the exact placeholder
  ``[PLACEHOLDER - acceptance criterion from licensed <standard> <clause> rev <year>]``.
* Keep Transmission (AS 2885) and Distribution (AS/NZS 4645) distinct; the
  standard family label carried differs by asset type and the two are never
  blended.
* Stamp the exact marker ``DRAFT — pending engineering review`` on every output.

Run:
    python3 itp_generator.py sample-activities.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# --- Exact constant strings (must not drift; tests assert on these) ---------

DRAFT_MARKER = "DRAFT — pending engineering review"

# Standard family LABELS only. These are pointers to the governing standard
# family, NOT clause numbers and NOT acceptance-criteria text.
STANDARD_LABELS: Dict[str, str] = {
    "Transmission": "AS 2885 series",
    "Distribution": "AS/NZS 4645 series",
    "Not asset-specific": "project-supplied reference",
}

VALID_ASSET_TYPES = tuple(STANDARD_LABELS.keys())

# Hold / Witness / Review / Monitor classification.
INSPECTION_POINTS = {
    "H": "Hold Point",
    "W": "Witness Point",
    "R": "Review",
    "M": "Monitor",
}

# Map common synonyms onto the H/W/R/M codes.
_POINT_SYNONYMS = {
    "H": "H", "HOLD": "H", "HOLD POINT": "H",
    "W": "W", "WITNESS": "W", "WITNESS POINT": "W",
    "R": "R", "REVIEW": "R",
    "M": "M", "MONITOR": "M", "SURVEILLANCE": "M",
}

# Default inspection point when the input does not specify one. Deliberately
# "R" (Review), never "H": a missing classification must not silently downgrade
# (or upgrade) a safety-critical test; the reviewer sets Hold/Witness explicitly.
DEFAULT_INSPECTION_POINT = "R"

_TEST_UNSPECIFIED = "To be defined"


def acceptance_placeholder(standard_label: str) -> str:
    """Return the exact acceptance-criterion placeholder for a standard label.

    ``<clause>`` and ``<year>`` stay as literal tokens until an engineer fills
    them from the licensed source. The clause number is NEVER fabricated.
    """
    return (
        "[PLACEHOLDER - acceptance criterion from licensed "
        f"{standard_label} <clause> rev <year>]"
    )


def normalise_inspection_point(raw: Optional[str]) -> str:
    """Normalise an inspection-point value to an H/W/R/M code.

    Unknown / empty values fall back to the default (Review); the caller flags
    the fallback so the engineer confirms the classification.
    """
    if raw is None:
        return DEFAULT_INSPECTION_POINT
    key = str(raw).strip().upper()
    return _POINT_SYNONYMS.get(key, DEFAULT_INSPECTION_POINT)


@dataclass
class LineItem:
    """One ITP line item mirroring templates/itp/itp-template.md columns."""

    item_no: int
    activity: str
    inspection_test: str
    acceptance_criteria: str
    verifying_document: str
    inspection_point: str  # H/W/R/M code
    responsibility: str
    record_form: str
    status: str = "Draft"
    point_defaulted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_no": self.item_no,
            "activity": self.activity,
            "inspection_test": self.inspection_test,
            "acceptance_criteria": self.acceptance_criteria,
            "verifying_document": self.verifying_document,
            "inspection_point": self.inspection_point,
            "responsibility": self.responsibility,
            "record_form": self.record_form,
            "status": self.status,
            "point_defaulted": self.point_defaulted,
        }


@dataclass
class Itp:
    """A generated draft ITP: header + line items + the DRAFT marker."""

    title: str
    project: str
    asset_type: str
    standard_label: str
    scope_of_work: str
    revision: str
    prepared_by: str
    draft_marker: str = DRAFT_MARKER
    status: str = "Draft"
    line_items: List[LineItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "project": self.project,
            "asset_type": self.asset_type,
            "standard_label": self.standard_label,
            "scope_of_work": self.scope_of_work,
            "revision": self.revision,
            "prepared_by": self.prepared_by,
            "draft_marker": self.draft_marker,
            "status": self.status,
            "line_items": [li.to_dict() for li in self.line_items],
        }


def _resolve_acceptance(activity: Dict[str, Any], standard_label: str) -> str:
    """Resolve the acceptance-criteria cell for an activity.

    A verbatim, source-backed criterion is carried unchanged ONLY when the
    activity explicitly provides it together with a source. Otherwise the
    marked placeholder is emitted. Nothing is ever fabricated.
    """
    criterion = activity.get("acceptance_criteria")
    source = activity.get("acceptance_source")
    if criterion and source:
        return f"{str(criterion).strip()} (source: {str(source).strip()})"
    return acceptance_placeholder(standard_label)


def build_line_item(seq: int, activity: Dict[str, Any], standard_label: str) -> LineItem:
    """Map a single input activity to an ITP line item per the generation rules."""
    name = str(activity.get("activity", "")).strip()
    if not name:
        raise ValueError(f"activity #{seq} is missing a required 'activity' name")

    raw_point = activity.get("inspection_point")
    point = normalise_inspection_point(raw_point)
    defaulted = raw_point is None or str(raw_point).strip().upper() not in _POINT_SYNONYMS

    inspection_test = str(activity.get("inspection_test", "")).strip() or _TEST_UNSPECIFIED

    return LineItem(
        item_no=seq,
        activity=name,
        inspection_test=inspection_test,
        acceptance_criteria=_resolve_acceptance(activity, standard_label),
        verifying_document=str(activity.get("verifying_document", "")).strip() or _TEST_UNSPECIFIED,
        inspection_point=point,
        responsibility=str(activity.get("responsibility", "")).strip() or _TEST_UNSPECIFIED,
        record_form=str(activity.get("record_form", "")).strip() or _TEST_UNSPECIFIED,
        status="Draft",
        point_defaulted=defaulted,
    )


def generate_itp(data: Dict[str, Any]) -> Itp:
    """Generate a draft ITP from a structured input dict.

    ``data`` keys: ``title``, ``project``, ``asset_type`` (required, one of
    Transmission / Distribution / Not asset-specific), ``scope_of_work``,
    ``revision``, ``prepared_by``, and ``activities`` (list).
    """
    asset_type = str(data.get("asset_type", "")).strip()
    if asset_type not in VALID_ASSET_TYPES:
        raise ValueError(
            "asset_type must be one of "
            f"{VALID_ASSET_TYPES!r} to keep AS2885/AS4645 distinct; got {asset_type!r}"
        )
    standard_label = STANDARD_LABELS[asset_type]

    activities = data.get("activities")
    if not isinstance(activities, list) or not activities:
        raise ValueError("input must contain a non-empty 'activities' list")

    line_items = [
        build_line_item(i, activity, standard_label)
        for i, activity in enumerate(activities, start=1)
    ]

    return Itp(
        title=str(data.get("title", "")).strip() or "Untitled ITP",
        project=str(data.get("project", "")).strip() or "<project identifier>",
        asset_type=asset_type,
        standard_label=standard_label,
        scope_of_work=str(data.get("scope_of_work", "")).strip() or "<scope of work>",
        revision=str(data.get("revision", "")).strip() or "0",
        prepared_by=str(data.get("prepared_by", "")).strip() or "EKA ITP generator (draft)",
        line_items=line_items,
    )


def _md_escape(text: str) -> str:
    """Escape pipe characters so cell content does not break the markdown table."""
    return str(text).replace("|", "\\|")


def render_markdown(itp: Itp) -> str:
    """Render the ITP as markdown following templates/itp/itp-template.md."""
    lines: List[str] = []
    lines.append(f"# Inspection & Test Plan (ITP) - {_md_escape(itp.title)}")
    lines.append("")
    lines.append(f"> ## {DRAFT_MARKER}")
    lines.append(">")
    lines.append(
        "> Machine-generated draft. Not authoritative. A qualified engineer must review "
        "and sign off before use. Acceptance-criteria placeholders must be completed from "
        "the licensed/approved source; clause numbers and criteria are never fabricated. "
        "Do not issue for construction while this marker is present."
    )
    lines.append("")
    lines.append("## Header")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    lines.append(f"| ITP Title | {_md_escape(itp.title)} |")
    lines.append(f"| Project | {_md_escape(itp.project)} |")
    lines.append(f"| Asset Type | {_md_escape(itp.asset_type)} |")
    lines.append(f"| Standard References (labels only) | {_md_escape(itp.standard_label)} |")
    lines.append(f"| Scope of Work | {_md_escape(itp.scope_of_work)} |")
    lines.append(f"| Revision | {_md_escape(itp.revision)} |")
    lines.append(f"| Status | {itp.status} |")
    lines.append(f"| Prepared By | {_md_escape(itp.prepared_by)} |")
    lines.append("| Reviewed By | <qualified engineer - on sign-off> |")
    lines.append("| Approved By | <approver - on sign-off> |")
    lines.append("")
    lines.append(
        "> **Inspection point legend:** **H** = Hold Point · **W** = Witness Point · "
        "**R** = Review · **M** = Monitor / Surveillance."
    )
    lines.append("")
    lines.append("## ITP line items")
    lines.append("")
    lines.append(
        "| Item No | Activity/Operation | Inspection/Test | Acceptance Criteria (Reference) "
        "| Verifying Document | Inspection Point (H/W/R/M) | Responsibility | Record/Form | Status |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for li in itp.line_items:
        point = li.inspection_point
        if li.point_defaulted:
            point = f"{point} (confirm)"
        lines.append(
            f"| {li.item_no} | {_md_escape(li.activity)} | {_md_escape(li.inspection_test)} "
            f"| {_md_escape(li.acceptance_criteria)} | {_md_escape(li.verifying_document)} "
            f"| {point} | {_md_escape(li.responsibility)} | {_md_escape(li.record_form)} "
            f"| {li.status} |"
        )
    lines.append("")
    lines.append(
        "> `(confirm)` marks an inspection point that was defaulted to Review because the "
        "input did not specify one; the reviewing engineer must set Hold/Witness where the "
        "applicable standard requires (for example pressure testing, welding and NDT)."
    )
    lines.append("")
    return "\n".join(lines)


def load_input(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a DRAFT ITP (markdown) from a structured activity list (JSON)."
    )
    parser.add_argument("input", help="Path to the activity-list JSON input.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the structured ITP dict as JSON instead of markdown.",
    )
    args = parser.parse_args(argv)

    try:
        data = load_input(args.input)
        itp = generate_itp(data)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(itp.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(render_markdown(itp))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
