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
- Generated descriptor estimate-vs-actual gap analysis.
- Implemented bounded descriptor refinements:
  - route-only packing for fixed/local/entropy streams
  - canonical Huffman table serialization for entropy mode
- Descriptor conclusion: estimate-vs-actual gap remains materially large.

### Target shift
- Primary competition target switched to ZIP-style baseline (`zlib`).
- Decision and matrix logic updated accordingly.

### Phase 3 status (ZIP-target framing)
- Re-ran scaling matrix batch: `reports/phase3_matrix/`
- Gate B result: `pass` (real-mode wins vs target baseline are repeatable in this batch)

### Phase 4/5 engineering status (in progress)
- Added performance harness: `cube_codec/perf.py`
- Added CLI command: `python -m cube_codec.cli perf ...`
- Added robustness tests for corrupt stream handling.
- Generated baseline perf artifact:
  - `reports/perf_baseline.json`
  - `reports/perf_baseline.md`
- Validation update: `pytest -q` -> `26 passed`

### Next actions
1. Add corruption-behavior notes to docs and format spec draft.
2. Expand perf runs across additional presets and summarize in `reports/perf_baseline.md`.
3. Build broader corpus pack manifest for stronger ZIP-target external validity.
