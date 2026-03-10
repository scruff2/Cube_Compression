# Benchmark Schema (Phase 0)

This document defines the minimum stable schema for benchmark artifacts.

## metrics.json (required top-level keys)

- `config`
- `corpus_split`
- `compression`
- `coverage`
- `search`
- `training`
- `runtime`
- `quality`
- `baselines`
- `real_descriptor_coding_modes`
- `cube_descriptor_idealization`
- `decision`

## diagnostics.json (required top-level keys)

- `cube_modes`
- `descriptor_overhead_diagnosis`
- `real_mode_diagnostics`
- `length_aware_diagnostics`
- `larger_cube_utilization`
- `scaling_diagnostics`
- `training_diagnostics`
- `decision`

## Deterministic fields (same input/config/seed)

The following should be invariant across reruns:

- compression bits and ratio values
- baseline compressed bits
- real mode compressed bits and decode success
- decision verdict fields
- cube and metadata size metrics

Expected non-invariant fields:

- runtime timings (`train_wall_time_sec`, `encode_wall_time_sec`, `decode_wall_time_sec`)

## Validation strategy

- Schema regression tests assert required keys.
- Reproducibility tests run benchmark twice and assert deterministic fields are identical.
