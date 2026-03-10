# Cube Codec ZIP-Competition Roadmap

## Purpose

Define a disciplined path from the current research prototype to a codec that can be credibly compared against ZIP-style compression in real-world conditions.

This roadmap prioritizes measurable evidence over optimism.

## Current Baseline (Starting Point)

- Prototype status: deterministic, testable, domain-structured results
- Strongest in-domain competitor: family-aware baseline
- Current gap: cube real modes still often lose to family-aware
- Positive signal: cube can beat zlib/lzma on some structured synthetic runs
- Conclusion: not ZIP-competitive yet

## Success Definition

A phase is successful only if it meets its acceptance thresholds.

Final success target:
- On a mixed public benchmark suite, best real cube mode is competitive with ZIP-class baselines on at least one meaningful data niche **without regressions in correctness and reproducibility**.

## Hard Constraints

- Preserve exact lossless decode across all modes.
- Keep deterministic outputs with fixed seeds/configs.
- Keep all benchmark comparisons fair: same corpus splits, same accounting rules.
- Do not claim general-purpose competitiveness until Phase 6 criteria are met.

---

## Phase 0: Measurement Integrity

### Goal
Ensure benchmark numbers are trustworthy before pursuing performance.

### Work
- Standardize metric definitions (bits, ratio, artifact overhead accounting).
- Freeze benchmark schema (`metrics.json`, `diagnostics.json`, matrix outputs).
- Add reproducibility checks (same config/seed => same outputs).
- Add CI test for benchmark schema stability.

### Acceptance Thresholds
- 100% decode success on all existing tests.
- Re-run variance of reported compressed bits is exactly 0 for deterministic configs.
- `pytest -q` remains all-pass.

### Deliverables
- `docs/benchmark_schema.md`
- schema regression tests

---

## Phase 1: Corpus Expansion and Fair Benchmark Suite

### Goal
Stop overfitting to synthetic toy sets and establish realistic evaluation.

### Work
- Build corpus packs:
  - structured synthetic (existing + scaled)
  - semi-structured real narrow-domain corpus
  - mixed general corpora (text, binaries, logs, media-like byte streams)
- Define train/validation/test split files and lock them.
- Add benchmark presets for each corpus family.

### Acceptance Thresholds
- At least 3 corpus families with documented sizes and splits.
- At least 1 real narrow-domain corpus included.
- One-command benchmark preset runner for each family.

### Deliverables
- `docs/corpora.md`
- `configs/presets/*.json`

---

## Phase 2: Descriptor Coding Maturity

### Goal
Close the gap between idealized descriptor estimates and real coded streams.

### Work
- Improve real entropy-coded route mode:
  - evaluate whole-route vs factorized coding in actual stream
  - minimize model header overhead
- Improve local-id coding stability and packing efficiency.
- Add diagnostics for estimate-vs-actual coding gap by regime and length class.

### Acceptance Thresholds
- On structured synthetic prefix/family corpora:
  - best real cube mode within 10% of its v1.2/v1.3 idealized estimate.
- No decode failures across all real modes.

### Deliverables
- `docs/descriptor_coding.md`
- updated mode comparison tables

---

## Phase 3: Scale Validation

### Goal
Prove whether increasing cube capacity/training data creates repeatable wins.

### Work
- Run tiered scale matrix:
  - training size: small/medium/large/extra_large
  - capacity: max regions, selected phrases, variants
  - regimes: fixed 128, fixed 256, variable [64,128,192,256]
- Track utilization efficiency:
  - region usage fraction
  - selected phrase exercised fraction
  - route span growth vs bit savings

### Acceptance Thresholds
- At least one repeatable regime where a real cube mode beats family-aware across 3+ runs with different seeds/splits.
- If not met, mark scale hypothesis as failed and gate further investment.

### Deliverables
- `reports/scaling_matrix_summary.md`
- decision memo: continue or stop scale path

---

## Phase 4: ZIP-Compatibility Readiness (Engineering)

### Goal
Move from research artifact toward practical codec discipline.

### Work
- Define stable container format versioning.
- Add integrity features (checksums, corruption detection behavior).
- Add CLI ergonomics for archive-like workflows.
- Add fuzz/property tests for decode robustness.

### Acceptance Thresholds
- Format roundtrip and backward-compat tests pass.
- Fuzz/property campaign finds no crash-level decoder defects in target budget.

### Deliverables
- `docs/format_spec.md`
- robustness test reports

---

## Phase 5: Performance Envelope (Speed/Memory)

### Goal
Reach practical runtime/memory characteristics for serious comparison.

### Work
- Profile encode/decode hotspots.
- Implement bounded-memory options.
- Add throughput benchmarks (MB/s) and peak RAM metrics.

### Acceptance Thresholds
- Documented throughput and memory figures across benchmark suite.
- No catastrophic memory growth with larger cube sizes.

### Deliverables
- `reports/perf_baseline.md`

---

## Phase 6: ZIP-Class Competition Evaluation

### Goal
Run a fair head-to-head comparison with ZIP-class techniques.

### Baselines
- zlib (ZIP-class)
- optionally zstd/brotli/lzma for context
- family-aware and flat dictionary retained as internal controls

### Work
- Evaluate on locked public + real corpus suite.
- Report per-corpus and aggregate results:
  - compression ratio
  - speed
  - memory
  - artifact overhead
- Separate niche wins from general losses.

### Acceptance Thresholds (for "competitive in niche" claim)
- On at least one documented data niche:
  - real cube mode >= zlib ratio by meaningful margin (>=5%)
  - while staying within acceptable speed/memory envelope for that niche
- If not met: no ZIP-competitive claim.

### Deliverables
- `reports/zip_competition_results.md`
- final recommendation

---

## Decision Gates (Stop/Continue)

- Gate A (after Phase 2): if estimate-vs-actual gap remains large, stop descriptor path.
- Gate B (after Phase 3): if scaling fails to produce repeatable family-aware wins, stop cube investment.
- Gate C (after Phase 6): if no niche beats zlib with acceptable runtime/memory, do not position as ZIP competitor.

---

## Weekly Execution Template

For each week/run batch, record:
- config preset
- corpus and split
- seed
- best real cube mode and bits
- family-aware bits
- zlib/lzma bits
- decode success
- speed/memory notes
- pass/fail against current phase thresholds

Recommended file:
- `reports/weekly_progress.md`

---

## Immediate Next Actions (Concrete)

1. Lock benchmark schema and add regression test (Phase 0).
2. Create corpus manifest with at least one larger real narrow-domain dataset (Phase 1).
3. Run descriptor estimate-vs-actual gap analysis on existing v1.5 presets (Phase 2).
4. Execute first scaled matrix batch and issue Gate B decision memo (Phase 3).

---

## How We Use This Roadmap

- Treat each phase threshold as mandatory.
- Only proceed when the current gate is passed.
- If a gate fails, document failure clearly and pivot/stop instead of broadening scope.
