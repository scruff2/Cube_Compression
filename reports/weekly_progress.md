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

## 2026-03-10

### Phase 1 completion
- Added locked corpus packs:
  - `corpora/phase1/semi_structured_narrow/`
  - `corpora/phase1/mixed_general/`
- Updated corpus docs and manifest:
  - `docs/corpora.md`
  - `docs/corpus_manifest.json`
- Added one-command preset runner:
  - `python -m cube_codec.cli benchmark-preset --preset <preset.json>`

### ZIP-target reporting cleanup
- Updated matrix reporting to target-baseline framing.
- Removed family-aware competition wording from benchmark report decisions.
- Added `delta_vs_target_baseline` in idealized mode tables.

### New benchmark/perf artifacts
- Generated preset benchmark outputs:
  - `reports/preset_structured_synth_metrics.json`
  - `reports/preset_semi_structured_narrow_metrics.json`
  - `reports/preset_mixed_general_metrics.json`
- Generated perf outputs:
  - `reports/perf_structured_synthetic.json`
  - `reports/perf_semi_structured_narrow.json`
  - `reports/perf_mixed_general.json`

### Phase 6 snapshot
- Added ZIP competition report with charts:
  - `reports/zip_competition_results.md`
- Gate C result: fail for ZIP-class positioning (wins are synthetic-only; broader corpora lose to zlib/lzma).

### Execution plan closure
- Added and completed `EXECUTION_PLAN.md`.
- Re-ran debug-first small E2E validation with exact decode match.
- Regenerated preset benchmark suite and perf suite artifacts.
- Validation gate: `pytest -q` -> `26 passed`.

### Descriptor redesign experiment: literal-side compression
- Implemented framed real-mode payloads with compressed literal side-stream for:
  - `cube_fixed_length_actual`
  - `cube_family_local_id_actual`
  - `cube_entropy_coded_actual`
- Added robustness and roundtrip tests for framed literal payload handling.
- Validation update: `pytest -q` -> `28 passed`.
- Impact on best real mode (`cube_family_local_id_actual`):
  - semi-structured narrow: `261,464 -> 190,568` bits (improved, still above zlib `57,920`)
  - mixed general: `125,160 -> 94,952` bits (improved, still above zlib `31,800`)

### Descriptor redesign experiment: token-side compression
- Added optional zlib compression for framed token payloads (`FLAG_TOKEN_ZLIB`) in fixed/local/entropy real modes.
- Added robustness test for invalid token-zlib flag/data combinations.
- Validation update: `pytest -q` -> `29 passed`.
- Additional impact on best real mode (`cube_family_local_id_actual`):
  - semi-structured narrow: `190,568 -> 78,408` bits (nearer to zlib `57,920`)
  - mixed general: `94,952 -> 42,832` bits (nearer to zlib `31,800`)

### Hybrid fast-path roadmap execution
- Added `HYBRID_EXECUTION_ROADMAP.md` and completed all milestones.
- Implemented stream-level literal-only fast path (`FLAG_LITERAL_ONLY_STREAM`) for real modes.
- Added fast-path decode corruption checks and roundtrip coverage.
- Validation update: `pytest -q` -> `31 passed`.
- Latest best-real results:
  - semi-structured narrow: `58,064` vs zlib `57,920` (delta `+144` bits)
  - mixed general: `31,944` vs zlib `31,800` (delta `+144` bits)

### Final-mile execution
- Added compact literal-only container (`CCL1`) with mode-preserving metadata and varint bit-length.
- Re-ran all validation and benchmark/perf artifacts.
- Updated plan file: `FINAL_MILE_PLAN.md`.
- Latest best-real results:
  - semi-structured narrow: `57,800` vs zlib `57,920` (delta `-120` bits)
  - mixed general: `31,792` vs zlib `31,800` (delta `-8` bits)

### Chunk-level hybrid execution
- Added `CCM3` chunked hybrid container with per-chunk route-vs-literal choice.
- Preserved backward decode compatibility for `CCM2` and `CCL1`.
- Tuned default chunk target to avoid context fragmentation regressions.
- Validation: `pytest -q` -> `31 passed`.
- Latest best-real results:
  - semi-structured narrow: `57,872` vs zlib `57,920` (delta `-48` bits)
  - mixed general: `31,864` vs zlib `31,800` (delta `+64` bits)
