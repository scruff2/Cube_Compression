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
- Descriptor conclusion: estimate-vs-actual gap remains materially large.

### Target shift
- Primary competition target switched to ZIP-style baseline (`zlib`).
- Decision and matrix logic updated accordingly.

### Phase 3 status (ZIP-target framing)
- Re-ran scaling matrix batch: `reports/phase3_matrix/`
- Gate B result: `pass` (real-mode wins vs target baseline are repeatable in this batch)
- Updated memos:
  - `reports/phase3_gate.md`
  - `reports/roadmap_recommendation.md`

### Next actions
1. Add speed/memory benchmark harness and baseline comparisons.
2. Add format robustness checks and corruption behavior tests.
3. Expand corpus pack beyond current synthetic-heavy set.
