"""Unit tests for the EKA tech-query prototype server.

Dependency-free (stdlib unittest). Imports the server module WITHOUT binding a
port by exercising the pure `load_atoms` / `search` functions directly.

Run:
    cd prototypes/tech-query-app && python3 -m unittest
"""

import unittest

import server


class CorpusLoadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atoms = server.load_atoms()

    def test_corpus_loads_192_atoms(self):
        self.assertEqual(len(self.atoms), 192)

    def test_every_atom_has_a_rule_id(self):
        for atom in self.atoms:
            self.assertTrue(atom.get("rule_id"), "atom missing rule_id")


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atoms = server.load_atoms()
        cls.rule_ids = {a["rule_id"] for a in cls.atoms}

    def test_interpass_returns_657_as_top_hit_with_300c(self):
        results = server.search("interpass", self.atoms)
        self.assertTrue(results, "expected at least one hit for 'interpass'")
        top = results[0]
        self.assertEqual(top["rule_id"], "JEM-GEN-SPC-M-014:6.5.7:R02")
        self.assertIn("300\u00b0C", top["rule_text"])  # verbatim degree symbol
        # Citation uses the exact designed form.
        self.assertEqual(
            top["_citation"],
            "JEM-GEN-SPC-M-014 Clause 6.5.7 (rule_id JEM-GEN-SPC-M-014:6.5.7:R02)",
        )

    def test_deviation_returns_23_with_approval_class_c(self):
        results = server.search("deviation", self.atoms)
        self.assertTrue(results, "expected at least one hit for 'deviation'")
        ids = [r["rule_id"] for r in results]
        self.assertIn("JEM-GEN-SPC-M-014:2.3:R01", ids)
        atom = next(r for r in results if r["rule_id"] == "JEM-GEN-SPC-M-014:2.3:R01")
        self.assertEqual(atom["approval_class"], "C")
        self.assertTrue(atom["approval_required"])
        self.assertIn("Appendix F approval class C", atom["_approval_line"])

    def test_nonsense_query_returns_no_hits(self):
        results = server.search("zzzxyq", self.atoms)
        self.assertEqual(results, [], "nonsense query must return the no-answer path")

    def test_empty_query_returns_no_hits(self):
        self.assertEqual(server.search("", self.atoms), [])

    def test_every_returnable_rule_id_is_real(self):
        # Across a spread of queries, every rule_id the search can return must be
        # a genuine corpus rule_id (no synthesis).
        for q in ["interpass", "deviation", "branch", "weld", "preheat", "inspection"]:
            for r in server.search(q, self.atoms):
                self.assertIn(r["rule_id"], self.rule_ids)


class ChecklistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atoms = server.load_atoms()

    def test_hold_witness_atoms_all_flagged(self):
        hw = server.hold_witness_atoms(self.atoms)
        self.assertTrue(hw)
        for a in hw:
            self.assertTrue(a["hold_witness_point"])

    def test_approval_atoms_all_require_approval_with_class(self):
        ap = server.approval_atoms(self.atoms)
        self.assertTrue(ap)
        for a in ap:
            self.assertTrue(a["approval_required"])
            self.assertIn(a["approval_class"], ("A", "B", "C"))

    def test_draft_marker_is_verbatim(self):
        self.assertEqual(server.DRAFT_MARKER, "DRAFT \u2014 pending engineering review")


if __name__ == "__main__":
    unittest.main()
