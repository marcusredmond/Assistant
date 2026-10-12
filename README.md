# Assistant

## Knowledge corpus: JEM-GEN-SPC-M-014 atomisation

Atomisation of the Jemena-owned specification **JEM-GEN-SPC-M-014** *Piping and
Mechanical Equipment – Shop Fabrication Specification For Facilities* (v4, 27 June
2017) into clause-traceable, AI-readable rule atoms. See the module design doc for
the schema, provenance, licensing stance and downstream usage.

| Artifact | Path | Purpose |
|---|---|---|
| Module design doc | [`docs/modules/spec-atomisation-design.md`](docs/modules/spec-atomisation-design.md) | Atom schema, provenance, file types, licensing, downstream feed, source anomalies, risk-lens review notes. |
| Atomiser prototype | [`prototypes/atomiser/`](prototypes/atomiser/) | Python-stdlib logic prototype that generates the corpus from the committed source. |
| Source transcription | [`knowledge/jem-gen-spc-m-014/source/`](knowledge/jem-gen-spc-m-014/source/) | Verbatim atomiser input (committed clauses + Appendix F rows). |
| JSONL atoms | [`knowledge/jem-gen-spc-m-014/atoms/`](knowledge/jem-gen-spc-m-014/atoms/) | One rule object per line; the primary grounding corpus. |
| Per-clause Markdown mirror | [`knowledge/jem-gen-spc-m-014/clauses/`](knowledge/jem-gen-spc-m-014/clauses/) | Human-readable mirror with YAML front-matter and verbatim bodies. |
| Matrices | [`knowledge/jem-gen-spc-m-014/matrices/`](knowledge/jem-gen-spc-m-014/matrices/) | Appendix F RTM + legend and the reference register. |
| Template schemas | [`knowledge/jem-gen-spc-m-014/schemas/`](knowledge/jem-gen-spc-m-014/schemas/) | Field structure of the five spec forms. |
| Manifest | [`knowledge/jem-gen-spc-m-014/manifest.json`](knowledge/jem-gen-spc-m-014/manifest.json) | Document identity, counts, Appendix F join rule and provenance. |

## tech-query Copilot agent (atom-grounded)

A declarative, importable Copilot Studio agent design grounded on the
JEM-GEN-SPC-M-014 atom corpus. It answers engineering questions and generates
Technical Query drafts, citing `rule_id` + clause for every claim. These are
tenant-neutral design artifacts; the sandbox cannot deploy to a Power Platform
tenant (see the deployment/import note in the design doc).

| Artifact | Path | Purpose |
|---|---|---|
| Agent design | [`agents/tech-query/agent-design.md`](agents/tech-query/agent-design.md) | Purpose, grounded knowledge source, citation behaviour, guardrails, system prompt, worked examples, and the tenant-admin deployment/import note. |
| Topic: ask an engineering question | [`agents/tech-query/topics/ask-engineering-question.json`](agents/tech-query/topics/ask-engineering-question.json) | Document-grounded Q&A topic; quotes `rule_text` verbatim and cites `rule_id` + clause. |
| Topic: generate a technical query | [`agents/tech-query/topics/generate-technical-query.json`](agents/tech-query/topics/generate-technical-query.json) | Collects the ES.DEG.FORM.009 Rev A fields and emits a DRAFT Technical Query. |
| Citation validator | [`prototypes/tech-query/`](prototypes/tech-query/) | Python-stdlib unittest that asserts every `rule_id` cited in the agent artifacts exists in the corpus. |
