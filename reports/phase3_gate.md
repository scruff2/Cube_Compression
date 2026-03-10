# Phase 3 Gate B Memo (ZIP-Target Framing)

Primary target baseline: zlib (ZIP-style comparator).

## Scaling Batch Summary
- runs: 4
- real-mode wins vs target baseline: 4
- gate criterion: >= 75% runs with real-mode win vs target baseline
- gate decision: pass

## Winning Runs
- run_000: best_real_mode=cube_family_local_id_actual, best_real_minus_target_bits=-1664
- run_001: best_real_mode=cube_family_local_id_actual, best_real_minus_target_bits=-1664
- run_002: best_real_mode=cube_family_local_id_actual, best_real_minus_target_bits=-1664
- run_003: best_real_mode=cube_family_local_id_actual, best_real_minus_target_bits=-1664

## Interpretation
- Under ZIP-target framing, cube real modes are competitive/superior in this benchmark batch.
- Continue toward performance and robustness phases for broader ZIP-style comparison.
