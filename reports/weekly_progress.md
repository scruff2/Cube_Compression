# Weekly Progress

## 2026-03-09

### Phase 0 status
- Added benchmark schema documentation: `docs/benchmark_schema.md`
- Added schema/repro tests for benchmark outputs (`test_benchmark_schema.py`)
- Validation: `pytest -q` -> `23 passed`

### Phase 1 status
- Added corpus planning document: `docs/corpora.md`
- Added locked corpus manifest: `docs/corpus_manifest.json`
- Added benchmark presets under `configs/presets/`
- Generated preset benchmark artifacts in `reports/`
- Gate result: `pass_with_limitations` (real large narrow-domain corpus not yet available)

### Phase 2 status
- Generated descriptor estimate-vs-actual gap analysis:
  - `reports/phase2_descriptor_gap.md`
  - `reports/phase2_descriptor_gap.json`
- Implemented bounded descriptor refinements:
  - route-only packing for fixed/local/entropy streams
  - canonical Huffman table serialization for entropy mode
- Re-ran presets and recomputed gap report.
- Gate A result (post-refinement): `fail`
  - entropy overhead improved but remains materially above estimate
  - best real cube mode still loses to family-aware on preset runs

### Next actions
1. Proceed to Phase 3 scaling batch as negative-control evidence collection.
2. Generate Gate B memo: determine if scaling can produce repeatable real-mode wins.
3. If Gate B fails, follow roadmap stop guidance.
