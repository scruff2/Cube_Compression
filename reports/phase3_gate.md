# Phase 3 Gate B Memo

## Scaling Batch Summary
- runs: 4
- real-mode wins vs family-aware: 2
- gate criterion: >= 3 repeatable real-mode wins across distinct regimes/splits
- gate decision: fail

## Real-Mode Winning Runs
- run_000: best_real_mode=cube_family_local_id_actual, delta=-276
- run_002: best_real_mode=cube_family_local_id_actual, delta=-276

## Interpretation
- Wins are sparse/fragile and not repeatable enough under current evidence.
- Scaling does not yet rescue competitiveness vs family-aware in a robust way.
- Per roadmap, this is a stop/pivot signal unless new corpus evidence changes the outcome.
