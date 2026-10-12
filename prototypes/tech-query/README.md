# tech-query citation validator

- **Title:** `tech-query` Agent Citation Validator
- **Version:** 0.1.0
- **Status:** Draft

A Python-standard-library check that enforces the **grounded, not generative**
rule for the `tech-query` Copilot agent design: every `rule_id` cited in the agent
artifacts must exist in the atomised JEM-GEN-SPC-M-014 corpus.

## What it checks

[`validate_citations.py`](validate_citations.py):

1. Loads `knowledge/jem-gen-spc-m-014/atoms/jem-gen-spc-m-014.atoms.jsonl` into a
   set of `rule_id` values.
2. Asserts the two topic JSON files parse as valid JSON.
3. Extracts every `rule_id`-shaped token (regex
   `JEM-GEN-SPC-M-014:[0-9.]+:R[0-9]+`) from
   [`agents/tech-query/agent-design.md`](../../agents/tech-query/agent-design.md),
   the two topic JSON files, and any `agents/tech-query/import-notes.md` present.
4. Asserts **every** extracted `rule_id` is a member of the corpus set, so the
   test fails loudly on any invented or mistyped citation. This is a membership
   check against the live corpus, not a static assertion.

## How to run

No dependencies to install. `pytest` is not available in this sandbox; use
`unittest`:

```sh
cd prototypes/tech-query
python3 -m unittest validate_citations
```

The repo root is resolved relative to the script's own location, so the test runs
correctly from this directory.
