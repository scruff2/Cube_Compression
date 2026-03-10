# Benchmark Matrix Summary

| run | cube_actual_bits | family_aware_bits | best_cube_mode | best_cube_bits | best_cube_minus_family_aware | geometry_verdict |
|---|---:|---:|---|---:|---:|---|
| run_000 | 322.00 | 516.00 | cube_entropy_estimated.whole_route | 63.30 | -452.70 | geometry_promising |
| run_001 | 322.00 | 182.00 | cube_entropy_estimated.whole_route | 63.30 | -118.70 | geometry_promising |
| run_002 | 322.00 | 516.00 | cube_entropy_estimated.whole_route | 63.30 | -452.70 | geometry_promising |
| run_003 | 322.00 | 182.00 | cube_entropy_estimated.whole_route | 63.30 | -118.70 | geometry_promising |

## Runs Where Cube Idealization Beats Family-Aware
- run_000
- run_001
- run_002
- run_003

## Runs Where Any Real Cube Mode Beats Family-Aware
- run_000
- run_002

## Runs Where Only Idealized Cube Modes Beat Family-Aware
- run_001
- run_003

## Runs Where Larger Cubes Increased Route Span But Still Lost
- run_001
- run_003

## Runs Where Scaling Mostly Created Unused Capacity
- run_000
- run_001
- run_002
- run_003

## Final Scaling Interpretation
- scaling appears promising in at least some real-mode runs