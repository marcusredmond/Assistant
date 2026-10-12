"""Unit tests for the single-file, offline EKA tech-query standalone app.

Dependency-free (stdlib unittest). Needs no browser. Regenerates the standalone
HTML from the committed corpus, then asserts the generated file:
  * embeds exactly 192 atoms whose rule_ids round-trip to the JSONL corpus;
  * references NO external resources (no off-box src/href/url(), no CDN, no web
    font, no fetch/XHR);
  * carries the verbatim DRAFT marker and the exact citation format;
  * embeds the 300C interpass atom (JEM-GEN-SPC-M-014:6.5.7:R02) verbatim;
  * is deterministic/idempotent (re-running the generator is a no-op).

Run:
    cd prototypes/tech-query-app && python3 -m unittest
"""

import json
import os
import re
import unittest

import build_standalone


_HERE = os.path.dirname(os.path.abspath(__file__))


def _extract_embedded_json(html):
    """Pull the raw text of the <script type="application/json" id="eka-atoms"> block."""
    m = re.search(
        r'<script[^>]*id="eka-atoms"[^>]*>(.*?)</script>',
        html,
        flags=re.DOTALL,
    )
    assert m, "could not find the eka-atoms embedded JSON block"
    raw = m.group(1)
    # The generator escapes "</" as "<\/" inside the block so it cannot close the
    # tag prematurely. Reverse that before JSON-parsing (it is a lossless swap).
    return raw.replace("<\\/", "</")


class StandaloneBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Always regenerate so the test reflects the current generator + corpus.
        build_standalone.build()
        with open(build_standalone.OUTPUT_PATH, "r", encoding="utf-8") as fh:
            cls.html = fh.read()
        cls.atoms = json.loads(_extract_embedded_json(cls.html))
        cls.corpus = build_standalone.load_atoms()

    def test_output_file_exists(self):
        self.assertTrue(os.path.isfile(build_standalone.OUTPUT_PATH))

    def test_embeds_exactly_192_atoms(self):
        self.assertEqual(len(self.atoms), 192)

    def test_embedded_rule_ids_round_trip_to_corpus(self):
        embedded_ids = sorted(a["rule_id"] for a in self.atoms)
        corpus_ids = sorted(a["rule_id"] for a in self.corpus)
        self.assertEqual(embedded_ids, corpus_ids)
        # Also assert full-object round-trip (no field loss / mutation).
        self.assertEqual(
            {a["rule_id"]: a for a in self.atoms},
            {a["rule_id"]: a for a in self.corpus},
        )

    def test_no_external_resource_references(self):
        html = self.html
        lowered = html.lower()
        # No external script/style/font/image loads, no analytics, no bundler imports.
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)
        self.assertNotIn("//cdn", lowered)
        self.assertNotIn("fetch(", html)
        self.assertNotIn("xmlhttprequest", lowered)
        self.assertNotIn("import(", html)
        # No src=/href= attributes at all (everything is inline).
        self.assertFalse(
            re.search(r'\bsrc\s*=', html),
            "standalone file must not reference external resources via src=",
        )
        self.assertFalse(
            re.search(r'\bhref\s*=', html),
            "standalone file must not reference external resources via href=",
        )
        # No CSS url() references pulling in off-box assets.
        self.assertFalse(
            re.search(r'url\(', html),
            "standalone file must not use CSS url() references",
        )

    def test_draft_marker_present_verbatim(self):
        self.assertEqual(
            build_standalone.DRAFT_MARKER,
            "DRAFT \u2014 pending engineering review",
        )
        # The exact marker string is embedded (as a JS constant assignment).
        self.assertIn("DRAFT \u2014 pending engineering review", self.html)

    def test_citation_format_present(self):
        # The citation builder uses the exact designed form:
        #   JEM-GEN-SPC-M-014 Clause {clause} (rule_id {rule_id})
        self.assertIn('"JEM-GEN-SPC-M-014 Clause " + atom.clause', self.html)
        self.assertIn('" (rule_id " + atom.rule_id + ")"', self.html)

    def test_interpass_atom_embedded_with_300c(self):
        by_id = {a["rule_id"]: a for a in self.atoms}
        atom = by_id.get("JEM-GEN-SPC-M-014:6.5.7:R02")
        self.assertIsNotNone(atom, "expected the interpass atom to be embedded")
        self.assertIn("300\u00b0C", atom["rule_text"])  # verbatim degree symbol
        self.assertEqual(atom["clause"], "6.5.7")

    def test_no_answer_message_matches_server(self):
        # Keep the honest no-answer text aligned with the server prototype.
        self.assertIn("defer to the responsible engineer", self.html)
        self.assertIn("will not guess, infer, or", self.html)

    def test_generator_is_idempotent(self):
        with open(build_standalone.OUTPUT_PATH, "r", encoding="utf-8") as fh:
            first = fh.read()
        build_standalone.build()
        with open(build_standalone.OUTPUT_PATH, "r", encoding="utf-8") as fh:
            second = fh.read()
        self.assertEqual(first, second, "re-running the generator must be a no-op")


if __name__ == "__main__":
    unittest.main()
