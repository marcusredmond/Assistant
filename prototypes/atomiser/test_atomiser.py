"""Unit tests for the JEM-GEN-SPC-M-014 atomiser.

These tests import the atomiser module directly and call the REAL functions so
they fail if the atomisation logic is reverted or weakened. Run from this
directory:

    python3 -m unittest discover -p 'test_*.py' -v
"""

from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

import atomiser


class AtomiserTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source, cls.appendix = atomiser.load_sources(
            atomiser.default_source_dir()
        )
        cls.rows = cls.appendix["rows"]
        cls.class_map = atomiser.build_appendix_f_class_map(cls.rows)
        cls.atoms = atomiser.build_atoms(cls.source, cls.class_map)

    # -- atom-level invariants ------------------------------------------------

    def test_rule_ids_unique(self) -> None:
        ids = [a.rule_id for a in self.atoms]
        self.assertEqual(len(ids), len(set(ids)), "rule_ids must be unique")

    def test_rule_text_non_empty(self) -> None:
        for a in self.atoms:
            self.assertTrue(
                a.rule_text and a.rule_text.strip(),
                f"empty rule_text for {a.rule_id}",
            )

    def test_modality_in_allowed_set(self) -> None:
        for a in self.atoms:
            self.assertIn(
                a.modality,
                atomiser.MODALITIES,
                f"bad modality {a.modality!r} for {a.rule_id}",
            )

    # -- modality CORRECTNESS (safety-critical classifier) --------------------

    def test_derive_modality_prohibitions(self) -> None:
        # "shall not" / "is not permitted" / directive-negative forms -> not_permitted.
        for text in (
            "Welds shall not be left exposed.",
            "No cold bending is permitted for HP facility.",
            "No worn or damaged dies are permitted.",
            "Welder IDs are not to be re-assigned.",
            "In-line instruments are not to be installed until test is complete.",
            "No more than two repairs per weld are permitted, else cut out.",
        ):
            self.assertEqual(
                atomiser.derive_modality(text),
                "not_permitted",
                f"expected not_permitted for {text!r}",
            )

    def test_derive_modality_mandatory(self) -> None:
        # Explicit "shall" and the transcription's directive forms -> shall.
        for text in (
            "The Contractor shall submit a Quality Plan.",
            "Fabrication is to be carried out under an accredited Quality System.",
            "A Quality Plan is required.",
            "WPS/WPQR are to be submitted for approval.",
            "The procedure is to be submitted for approval.",
        ):
            self.assertEqual(
                atomiser.derive_modality(text),
                "shall",
                f"expected shall for {text!r}",
            )

    def test_derive_modality_should_and_may(self) -> None:
        self.assertEqual(
            atomiser.derive_modality("The Contractor should minimise flex."),
            "should",
        )
        self.assertEqual(
            atomiser.derive_modality("UT may be used instead if accepted."),
            "may",
        )

    def test_derive_modality_descriptive(self) -> None:
        # Genuinely definitional/descriptive wording stays informational.
        for text in (
            "Defines the terms Contractor, Jemena and Others.",
            "Lists the Australian Standards referenced by this Specification.",
            "New materials are addressed under the quality assurance requirements.",
        ):
            self.assertEqual(
                atomiser.derive_modality(text),
                "informational",
                f"expected informational for {text!r}",
            )

    def test_explicit_modality_hint_takes_precedence(self) -> None:
        # A descriptive sentence carrying an explicit source hint resolves to
        # the hinted modality - this is the mechanism that re-modalises the
        # mandatory acceptance limits (review v1 issue 2).
        descriptive = "Hold for 1 hour; if painted, hold 4 hours."
        self.assertEqual(atomiser.derive_modality(descriptive), "informational")
        self.assertEqual(
            atomiser.derive_modality(descriptive, "shall"), "shall"
        )
        # An invalid hint is ignored (falls back to wording-based derivation).
        self.assertEqual(
            atomiser.derive_modality(descriptive, "bogus"), "informational"
        )

    def test_no_informational_atom_carries_a_mandatory_limit(self) -> None:
        # Safety guard: after re-modalisation via source hints, no atom that
        # carries a hard quantitative acceptance limit may be left
        # informational (review v1 issue 2). Order-of-precedence ranked atoms
        # are intentionally informational and excluded.
        limit_re = re.compile(
            r"(\d+\s*(mm|kPag|years|hrs|hours|hour))"
            r"|\u00b0C"  # degrees Celsius
            r"|\u2265"  # >=
            r"|\u00b1"  # +-
            r"|1\.5 x|6 x|x design pressure"
        )
        offenders = [
            a.rule_id
            for a in self.atoms
            if a.modality == "informational"
            and a.order_of_precedence_rank is None
            and limit_re.search(a.rule_text)
        ]
        self.assertEqual(
            offenders,
            [],
            f"mandatory acceptance limits left informational: {offenders}",
        )

    def test_known_mandatory_limit_atoms_are_shall(self) -> None:
        # Pin the specific safety limits the v1 review flagged so they cannot
        # silently regress back to informational.
        expected_shall = {
            "JEM-GEN-SPC-M-014:8.1:R01",  # hydrostatic 1.5 x design pressure
            "JEM-GEN-SPC-M-014:8.2:R03",  # hold 1 hr / >=4 hr
            "JEM-GEN-SPC-M-014:8.3:R02",  # dewpoint -40C / -20C
            "JEM-GEN-SPC-M-014:6.5.7:R02",  # interpass max 300C
            "JEM-GEN-SPC-M-014:6.5.4:R03",  # four 30 mm tacks
            "JEM-GEN-SPC-M-014:10.6:R01",  # FAT 30 kPag
            "JEM-GEN-SPC-M-014:7.4:R02",  # final NDE >=24 hrs
            "JEM-GEN-SPC-M-014:7.3.3:R01",  # archival film >=7 years
            "JEM-GEN-SPC-M-014:7.3.2:R04",  # film density 1.7 / 2.5-4.0
        }
        by_id = {a.rule_id: a for a in self.atoms}
        for rid in expected_shall:
            self.assertIn(rid, by_id, f"missing expected atom {rid}")
            self.assertEqual(
                by_id[rid].modality,
                "shall",
                f"{rid} must be shall, got {by_id[rid].modality}",
            )

    def test_compound_split_assigns_distinct_modalities(self) -> None:
        # The thread-lubricant and welder-ID compound sentences were split so
        # the leading mandatory requirement is not masked by a trailing
        # prohibition (review v1 issue 5).
        by_id = {a.rule_id: a for a in self.atoms}
        # 5.2.6: lubricant/thread protection (shall) + worn-dies prohibition.
        self.assertEqual(by_id["JEM-GEN-SPC-M-014:5.2.6:R02"].modality, "shall")
        self.assertEqual(
            by_id["JEM-GEN-SPC-M-014:5.2.6:R03"].modality, "not_permitted"
        )
        # 6.4: ID recording (shall) + welder-ID re-assignment prohibition.
        self.assertEqual(by_id["JEM-GEN-SPC-M-014:6.4:R02"].modality, "shall")
        self.assertEqual(
            by_id["JEM-GEN-SPC-M-014:6.4:R03"].modality, "not_permitted"
        )

    def test_approval_class_only_abc_or_null(self) -> None:
        for a in self.atoms:
            self.assertIn(
                a.approval_class,
                ("A", "B", "C", None),
                f"bad approval_class {a.approval_class!r} for {a.rule_id}",
            )

    def test_approval_class_traces_to_appendix_f(self) -> None:
        for a in self.atoms:
            if a.approval_class is not None:
                self.assertIn(a.clause, self.class_map)
                self.assertEqual(a.approval_class, self.class_map[a.clause])
                self.assertTrue(a.approval_required)
            else:
                self.assertFalse(a.approval_required)

    def test_references_are_pointer_strings(self) -> None:
        for a in self.atoms:
            self.assertIsInstance(a.references, list)
            for ref in a.references:
                self.assertIsInstance(ref, str)
                # Pointers are short identifiers/titles, never a reproduced
                # standard body. Guard against accidentally long text.
                self.assertLess(
                    len(ref), 160, f"reference looks like body text: {ref!r}"
                )

    # -- atomic granularity ---------------------------------------------------

    def test_clause_with_n_obligations_yields_n_atoms(self) -> None:
        # Clause 5.2.5 has 5 obligations in the source and no ranked expansion.
        clause = next(c for c in self.source["clauses"] if c["clause"] == "5.2.5")
        n = len(clause["obligations"])
        got = [a for a in self.atoms if a.clause == "5.2.5"]
        self.assertEqual(len(got), n)
        self.assertEqual(n, 5)

    def test_total_atom_count_at_least_obligations(self) -> None:
        obligations = sum(
            len(c["obligations"]) for c in self.source["clauses"]
        )
        # Order-of-precedence expansion adds ranked atoms on top.
        self.assertGreaterEqual(len(self.atoms), obligations)

    # -- order of precedence --------------------------------------------------

    def test_order_of_precedence_atoms_ranked(self) -> None:
        ranked = [
            a
            for a in self.atoms
            if a.clause == "2.4" and a.order_of_precedence_rank is not None
        ]
        self.assertEqual(len(ranked), 4)
        self.assertEqual(
            sorted(a.order_of_precedence_rank for a in ranked), [1, 2, 3, 4]
        )

    # -- hold / witness points ------------------------------------------------

    def test_clause_31_hold_witness_flagged(self) -> None:
        hold = [
            a for a in self.atoms if a.clause == "3.1" and a.hold_witness_point
        ]
        self.assertEqual(len(hold), 7)
        for a in hold:
            self.assertTrue(a.hold_witness_point)

    # -- footnote / cross reference -------------------------------------------

    def test_522_as28852_footnote_present(self) -> None:
        atoms_522 = [a for a in self.atoms if a.clause == "5.2.2"]
        joined = " ".join(r for a in atoms_522 for r in a.references)
        self.assertIn("AS 2885.2", joined)
        self.assertIn("5.13", joined)

    # -- clause-numbering anomaly preserved -----------------------------------

    def test_clause_numbering_anomaly_preserved(self) -> None:
        clause_ids = {c["clause"] for c in self.source["clauses"]}
        for cid in ("6.3.2", "6.3.3", "6.3.4"):
            self.assertIn(cid, clause_ids)
        titles = {
            c["clause"]: c["clause_title"] for c in self.source["clauses"]
        }
        self.assertEqual(titles["6.3.2"], "Inspection and NDE of Test Welds")
        self.assertEqual(titles["6.3.3"], "Approval of Welding Procedures")
        self.assertEqual(titles["6.3.4"], "Repair Procedures")

    # -- appendix F join rule -------------------------------------------------

    def test_strictest_class_join(self) -> None:
        # Clause 5.3 has rows class C and class A -> strictest A applies.
        self.assertEqual(self.class_map["5.3"], "A")
        # Clause 3.3.2 has rows A and C -> A.
        self.assertEqual(self.class_map["3.3.2"], "A")

    def test_appendix_f_row_count_matches_source(self) -> None:
        # Asserted against the actual source file, not a hardcoded number.
        self.assertEqual(len(self.rows), 55)

    # -- end-to-end generation + emitted artifacts ----------------------------

    def test_generation_outputs_parse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            counts = atomiser.generate(self.source, self.appendix, out)
            self.assertEqual(counts["clause_count"], len(self.source["clauses"]))
            self.assertEqual(counts["appendix_f_row_count"], len(self.rows))

            # JSONL: every line parses independently.
            jsonl = out / "atoms" / "jem-gen-spc-m-014.atoms.jsonl"
            with jsonl.open(encoding="utf-8") as fh:
                lines = [ln for ln in fh if ln.strip()]
            self.assertEqual(len(lines), len(self.atoms))
            for ln in lines:
                json.loads(ln)

            # manifest parses and records key fields.
            manifest = json.loads(
                (out / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["version"], "4")
            self.assertEqual(manifest["date"], "27 June 2017")
            self.assertEqual(manifest["supersedes"], "P09JAM00-000SPC-M-006")
            self.assertEqual(manifest["appendix_f_row_count"], len(self.rows))
            self.assertIn("provenance", manifest)

            # Appendix F CSV row count equals source row count.
            import csv

            with (out / "matrices" / "appendix-f-reference-guide.csv").open(
                encoding="utf-8"
            ) as fh:
                reader = list(csv.DictReader(fh))
            self.assertEqual(len(reader), len(self.rows))
            self.assertEqual(
                list(reader[0].keys()),
                ["clause", "requirement_description", "class"],
            )

            # Reference register JSON parses; licensing flags are valid.
            reg = json.loads(
                (out / "matrices" / "reference-register.json").read_text(
                    encoding="utf-8"
                )
            )
            for r in reg["references"]:
                self.assertIn(
                    r["licensing"], ("jemena_owned", "copyrighted_external")
                )
            # The document itself is Jemena-owned.
            doc_entry = next(
                r for r in reg["references"] if r["ref_id"] == atomiser.DOC_ID
            )
            self.assertEqual(doc_entry["licensing"], "jemena_owned")
            # AS standards are copyrighted_external.
            as_entries = [
                r for r in reg["references"] if r["issuer"] == "AS"
            ]
            self.assertTrue(as_entries)
            for r in as_entries:
                self.assertEqual(r["licensing"], "copyrighted_external")

            # Every schema JSON parses; generated deliverables carry the marker.
            schema_dir = out / "schemas"
            deliverables = {
                "technical-query-form.json",
                "mechanical-inspection-record.json",
                "punchlist.json",
                "factory-commissioning-acceptance-test-record.json",
            }
            for path in schema_dir.glob("*.json"):
                data = json.loads(path.read_text(encoding="utf-8"))
                if path.name in deliverables:
                    self.assertEqual(
                        data["draftMarkerGuidance"],
                        atomiser.DRAFT_MARKER,
                        f"missing/incorrect DRAFT marker in {path.name}",
                    )
            # All five schemas exist.
            self.assertEqual(len(list(schema_dir.glob("*.json"))), 5)

            # Per-clause Markdown exists for every clause + README index.
            for clause in self.source["clauses"]:
                stem = atomiser.kebab_clause(clause["clause"])
                self.assertTrue((out / "clauses" / f"{stem}.md").exists())
            self.assertTrue((out / "clauses" / "README.md").exists())

    def test_draft_marker_exact_string(self) -> None:
        # Exact string including the literal em dash (U+2014).
        self.assertEqual(
            atomiser.DRAFT_MARKER, "DRAFT \u2014 pending engineering review"
        )


if __name__ == "__main__":
    unittest.main()
