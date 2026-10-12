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
