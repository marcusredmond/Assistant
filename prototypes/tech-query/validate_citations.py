"""Citation validator for the JEM-GEN-SPC-M-014 tech-query agent artifacts.

Purpose
-------
Guards the GROUNDED-NOT-GENERATIVE rule for the ``tech-query`` Copilot agent
design: every ``rule_id`` cited anywhere in the agent design doc, the two topic
JSON files and the deployment/import note MUST exist in the atom corpus. The test
checks SET MEMBERSHIP against the corpus, so it fails loudly on any invented or
mistyped citation (not a static hardcoded assertion).

What it does
------------
  * loads ``knowledge/jem-gen-spc-m-014/atoms/jem-gen-spc-m-014.atoms.jsonl``
    into a set of ``rule_id`` values;
  * asserts the two topic JSON files load as valid JSON;
  * extracts every ``rule_id``-shaped token (regex
    ``JEM-GEN-SPC-M-014:[0-9.]+:R[0-9]+``) from the agent design doc, the two
    topic JSON files and any ``import-notes.md`` present under the agent folder;
  * asserts EVERY extracted ``rule_id`` is a member of the corpus set.

Scope note: Python standard library only. No third-party dependencies, no network.
pytest is NOT installed in this sandbox; run with unittest.

How to run
----------
From inside this directory::

    cd prototypes/tech-query
    python3 -m unittest validate_citations

See also ``prototypes/tech-query/README.md``.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

# This file lives at <repo>/prototypes/tech-query/validate_citations.py, so the
# repo root is two directories up. Resolve relative to the script's own location
# so the test runs correctly from its own directory.
REPO_ROOT = Path(__file__).resolve().parents[2]

ATOMS_JSONL = (
    REPO_ROOT
    / "knowledge"
    / "jem-gen-spc-m-014"
    / "atoms"
    / "jem-gen-spc-m-014.atoms.jsonl"
)
AGENT_DIR = REPO_ROOT / "agents" / "tech-query"
AGENT_DESIGN = AGENT_DIR / "agent-design.md"
TOPIC_FILES = [
    AGENT_DIR / "topics" / "ask-engineering-question.json",
    AGENT_DIR / "topics" / "generate-technical-query.json",
]
IMPORT_NOTES = AGENT_DIR / "import-notes.md"  # optional sibling note

# Matches a JEM-GEN-SPC-M-014 rule_id token, e.g. JEM-GEN-SPC-M-014:6.5.7:R02.
RULE_ID_RE = re.compile(r"JEM-GEN-SPC-M-014:[0-9.]+:R[0-9]+")


def load_corpus_rule_ids(path: Path) -> set[str]:
    """Load the atoms JSONL into a set of rule_id values."""
    rule_ids: set[str] = set()
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            atom = json.loads(line)
            rule_ids.add(atom["rule_id"])
    return rule_ids


def extract_rule_ids(text: str) -> set[str]:
    """Return every rule_id-shaped token found in text."""
    return set(RULE_ID_RE.findall(text))


class CitationValidationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus_rule_ids = load_corpus_rule_ids(ATOMS_JSONL)
        # Collect the artifact files that must only cite real rule_ids.
        cls.artifact_files = [AGENT_DESIGN, *TOPIC_FILES]
        if IMPORT_NOTES.exists():
            cls.artifact_files.append(IMPORT_NOTES)

    def test_corpus_loaded(self) -> None:
        # Sanity: the corpus must load and must contain the two atoms the
        # worked examples rely on, so the membership check is meaningful.
        self.assertTrue(ATOMS_JSONL.exists(), f"missing corpus: {ATOMS_JSONL}")
        self.assertGreater(len(self.corpus_rule_ids), 0, "empty corpus")
        self.assertIn("JEM-GEN-SPC-M-014:6.5.7:R02", self.corpus_rule_ids)
        self.assertIn("JEM-GEN-SPC-M-014:2.3:R01", self.corpus_rule_ids)

    def test_topic_json_files_parse(self) -> None:
        for path in TOPIC_FILES:
            self.assertTrue(path.exists(), f"missing topic file: {path}")
            with path.open(encoding="utf-8") as fh:
                data = json.load(fh)  # raises on invalid JSON
            self.assertIn("topic", data, f"no 'topic' key in {path.name}")

    def test_agent_design_exists(self) -> None:
        self.assertTrue(
            AGENT_DESIGN.exists(), f"missing agent design: {AGENT_DESIGN}"
        )

    def test_every_cited_rule_id_exists_in_corpus(self) -> None:
        # The core guard: SET MEMBERSHIP against the corpus. If any artifact
        # cites a rule_id that is not in the atoms JSONL, this fails loudly and
        # names the offending token(s) and file.
        offenders: dict[str, list[str]] = {}
        total_citations = 0
        for path in self.artifact_files:
            text = path.read_text(encoding="utf-8")
            cited = extract_rule_ids(text)
            total_citations += len(cited)
            bogus = sorted(cited - self.corpus_rule_ids)
            if bogus:
                offenders[str(path.relative_to(REPO_ROOT))] = bogus
        self.assertEqual(
            offenders,
            {},
            "cited rule_id(s) not found in the corpus (invented citation): "
            f"{offenders}",
        )
        # Guard against a vacuous pass: the worked examples must actually cite
        # at least one rule_id, otherwise the membership check proves nothing.
        self.assertGreater(
            total_citations,
            0,
            "no rule_id citations found in the agent artifacts; "
            "the worked example should cite at least one rule_id",
        )

    def test_worked_example_rule_ids_present(self) -> None:
        # The two documented worked examples must be cited in the design doc.
        design_text = AGENT_DESIGN.read_text(encoding="utf-8")
        cited = extract_rule_ids(design_text)
        self.assertIn("JEM-GEN-SPC-M-014:6.5.7:R02", cited)
        self.assertIn("JEM-GEN-SPC-M-014:2.3:R01", cited)


if __name__ == "__main__":
    unittest.main()
