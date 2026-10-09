#!/usr/bin/env python3
"""Unit tests for the ITP generator prototype (standard-library unittest).

These exercise the real generator functions so they would fail if the
generation logic were reverted or weakened. They cover:

  (a) correct number / shape of line items generated from input,
  (b) acceptance-criteria placeholders are emitted and NO fabricated clause
      numbers appear in output,
  (c) the exact "DRAFT — pending engineering review" marker is present,
  (d) Transmission (AS 2885) vs Distribution (AS/NZS 4645) are handled
      distinctly.
"""

import json
import os
import re
import unittest

import itp_generator as gen

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "sample-activities.json")


_UNSET = object()


def _transmission_input(activities=_UNSET):
    if activities is _UNSET:
        activities = [
            {"activity": "Hydrostatic test", "inspection_point": "Hold",
             "responsibility": "Test Supervisor"},
            {"activity": "Weld visual", "inspection_point": "Witness",
             "responsibility": "QA"},
        ]
    return {
        "title": "TX ITP",
        "project": "TX-1",
        "asset_type": "Transmission",
        "scope_of_work": "weld + test",
        "revision": "A",
        "activities": activities,
    }


def _distribution_input(activities=_UNSET):
    if activities is _UNSET:
        activities = [
            {"activity": "Mains pressure test", "inspection_point": "Hold",
             "responsibility": "Test Supervisor"},
        ]
    return {
        "title": "DX ITP",
        "project": "DX-1",
        "asset_type": "Distribution",
        "scope_of_work": "mains lay + test",
        "revision": "A",
        "activities": activities,
    }


class LineItemShapeTests(unittest.TestCase):
    def test_one_line_item_per_activity(self):
        activities = [
            {"activity": "A"},
            {"activity": "B"},
            {"activity": "C"},
        ]
        itp = gen.generate_itp(_transmission_input(activities))
        self.assertEqual(len(itp.line_items), 3)

    def test_item_numbers_are_sequential_from_one(self):
        activities = [{"activity": f"act {i}"} for i in range(5)]
        itp = gen.generate_itp(_transmission_input(activities))
        self.assertEqual([li.item_no for li in itp.line_items], [1, 2, 3, 4, 5])

    def test_line_item_preserves_input_order(self):
        activities = [{"activity": "first"}, {"activity": "second"}]
        itp = gen.generate_itp(_transmission_input(activities))
        self.assertEqual(itp.line_items[0].activity, "first")
        self.assertEqual(itp.line_items[1].activity, "second")

    def test_line_item_has_all_template_columns(self):
        itp = gen.generate_itp(_transmission_input())
        d = itp.line_items[0].to_dict()
        for key in (
            "item_no", "activity", "inspection_test", "acceptance_criteria",
            "verifying_document", "inspection_point", "responsibility",
            "record_form", "status",
        ):
            self.assertIn(key, d)

    def test_sample_file_generates_matching_line_item_count(self):
        with open(SAMPLE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        itp = gen.generate_itp(data)
        self.assertEqual(len(itp.line_items), len(data["activities"]))

    def test_empty_activities_rejected(self):
        with self.assertRaises(ValueError):
            gen.generate_itp(_transmission_input([]))

    def test_activity_without_name_rejected(self):
        with self.assertRaises(ValueError):
            gen.generate_itp(_transmission_input([{"inspection_point": "Hold"}]))

    def test_generated_line_item_status_is_draft(self):
        itp = gen.generate_itp(_transmission_input())
        self.assertTrue(all(li.status == "Draft" for li in itp.line_items))


class AcceptanceCriteriaTests(unittest.TestCase):
    """Placeholders emitted; nothing fabricated."""

    # Rough pattern for a clause number like "5.3", "X.Y.Z", "12.4.1".
    _CLAUSE_NUMBER = re.compile(r"\bclause\s+\d+(?:\.\d+)+\b", re.IGNORECASE)
    _BARE_CLAUSE = re.compile(r"\b\d+\.\d+(?:\.\d+)+\b")

    def test_placeholder_emitted_when_no_source_criterion(self):
        itp = gen.generate_itp(_transmission_input())
        for li in itp.line_items:
            self.assertIn(
                "[PLACEHOLDER - acceptance criterion from licensed",
                li.acceptance_criteria,
            )

    def test_placeholder_carries_asset_type_standard_label(self):
        tx = gen.generate_itp(_transmission_input())
        self.assertIn("AS 2885 series", tx.line_items[0].acceptance_criteria)
        dx = gen.generate_itp(_distribution_input())
        self.assertIn("AS/NZS 4645 series", dx.line_items[0].acceptance_criteria)

    def test_placeholder_keeps_literal_clause_and_year_tokens(self):
        itp = gen.generate_itp(_transmission_input())
        ac = itp.line_items[0].acceptance_criteria
        self.assertIn("<clause>", ac)
        self.assertIn("<year>", ac)

    def test_no_fabricated_clause_numbers_in_markdown(self):
        itp = gen.generate_itp(_transmission_input())
        md = gen.render_markdown(itp)
        self.assertIsNone(self._CLAUSE_NUMBER.search(md),
                           "no 'Clause N.N' should ever be fabricated")
        self.assertIsNone(self._BARE_CLAUSE.search(md),
                           "no bare dotted clause number should appear")

    def test_no_fabricated_clause_numbers_in_sample_output(self):
        with open(SAMPLE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        md = gen.render_markdown(gen.generate_itp(data))
        self.assertIsNone(self._CLAUSE_NUMBER.search(md))
        self.assertIsNone(self._BARE_CLAUSE.search(md))

    def test_source_backed_criterion_carried_verbatim_with_source(self):
        activities = [{
            "activity": "Documented test",
            "acceptance_criteria": "No visible leakage over the hold period",
            "acceptance_source": "Approved commissioning procedure CP-01",
        }]
        itp = gen.generate_itp(_transmission_input(activities))
        ac = itp.line_items[0].acceptance_criteria
        self.assertIn("No visible leakage over the hold period", ac)
        self.assertIn("CP-01", ac)
        self.assertNotIn("[PLACEHOLDER", ac)

    def test_criterion_without_source_falls_back_to_placeholder(self):
        # A criterion supplied WITHOUT a source must not be trusted/carried.
        activities = [{
            "activity": "Unsourced test",
            "acceptance_criteria": "Pressure held per standard",
        }]
        itp = gen.generate_itp(_transmission_input(activities))
        self.assertIn("[PLACEHOLDER", itp.line_items[0].acceptance_criteria)


class DraftMarkerTests(unittest.TestCase):
    def test_exact_marker_constant(self):
        self.assertEqual(gen.DRAFT_MARKER, "DRAFT — pending engineering review")

    def test_marker_on_itp_object(self):
        itp = gen.generate_itp(_transmission_input())
        self.assertEqual(itp.draft_marker, "DRAFT — pending engineering review")

    def test_marker_in_markdown_output(self):
        md = gen.render_markdown(gen.generate_itp(_transmission_input()))
        self.assertIn("DRAFT — pending engineering review", md)

    def test_marker_in_json_output(self):
        d = gen.generate_itp(_transmission_input()).to_dict()
        self.assertEqual(d["draft_marker"], "DRAFT — pending engineering review")
        self.assertEqual(d["status"], "Draft")


class AssetTypeSeparationTests(unittest.TestCase):
    def test_transmission_carries_as2885_label(self):
        itp = gen.generate_itp(_transmission_input())
        self.assertEqual(itp.standard_label, "AS 2885 series")

    def test_distribution_carries_as4645_label(self):
        itp = gen.generate_itp(_distribution_input())
        self.assertEqual(itp.standard_label, "AS/NZS 4645 series")

    def test_labels_differ_by_asset_type(self):
        tx = gen.generate_itp(_transmission_input())
        dx = gen.generate_itp(_distribution_input())
        self.assertNotEqual(tx.standard_label, dx.standard_label)

    def test_transmission_output_does_not_mention_distribution_standard(self):
        md = gen.render_markdown(gen.generate_itp(_transmission_input()))
        self.assertNotIn("AS/NZS 4645", md)

    def test_distribution_output_does_not_mention_transmission_standard(self):
        md = gen.render_markdown(gen.generate_itp(_distribution_input()))
        self.assertNotIn("AS 2885", md)

    def test_invalid_asset_type_rejected(self):
        bad = _transmission_input()
        bad["asset_type"] = "Pipeline"
        with self.assertRaises(ValueError):
            gen.generate_itp(bad)

    def test_missing_asset_type_rejected(self):
        bad = _transmission_input()
        del bad["asset_type"]
        with self.assertRaises(ValueError):
            gen.generate_itp(bad)


class InspectionPointTests(unittest.TestCase):
    def test_hold_synonyms_normalise_to_H(self):
        self.assertEqual(gen.normalise_inspection_point("Hold"), "H")
        self.assertEqual(gen.normalise_inspection_point("hold point"), "H")
        self.assertEqual(gen.normalise_inspection_point("H"), "H")

    def test_witness_review_monitor_normalise(self):
        self.assertEqual(gen.normalise_inspection_point("Witness"), "W")
        self.assertEqual(gen.normalise_inspection_point("Review"), "R")
        self.assertEqual(gen.normalise_inspection_point("Surveillance"), "M")

    def test_missing_point_defaults_to_review_not_hold(self):
        # Safety: a missing classification must NOT become a Hold silently.
        self.assertEqual(gen.normalise_inspection_point(None), "R")
        itp = gen.generate_itp(_transmission_input([{"activity": "x"}]))
        li = itp.line_items[0]
        self.assertEqual(li.inspection_point, "R")
        self.assertTrue(li.point_defaulted)

    def test_specified_point_is_not_flagged_defaulted(self):
        itp = gen.generate_itp(_transmission_input(
            [{"activity": "x", "inspection_point": "Hold"}]))
        self.assertFalse(itp.line_items[0].point_defaulted)


if __name__ == "__main__":
    unittest.main()
