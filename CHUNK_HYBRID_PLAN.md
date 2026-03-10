# Chunk-Level Hybrid Plan

Date: 2026-03-10

## Goal

Implement true chunk-level hybrid mode selection inside the stream container so each chunk can choose route-coded or literal-only representation, then validate and publish updated results.

## Steps

- [x] Implement `CCM3` chunked container format.
- [x] For each chunk, choose smaller of route-coded chunk vs literal-only chunk.
- [x] Preserve backward decode compatibility for existing `CCM2` and `CCL1` streams.
- [x] Update tests for chunked container behavior and corruption handling.
- [x] Rerun benchmark presets and perf baselines.
- [x] Refresh README and reports.
- [x] Commit and push.

## Outcome

- Validation: `pytest -q` => `31 passed`.
- Semi-structured: `57,872` vs zlib `57,920` (cube `-48` bits).
- Mixed-general: `31,864` vs zlib `31,800` (cube `+64` bits).
- Result: stable near-parity; meaningful-margin target not yet met.
