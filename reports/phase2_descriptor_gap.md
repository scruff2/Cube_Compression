# Phase 2 Descriptor Gap Report

This report compares v1.2/v1.3-style idealized descriptor estimates with real coded stream sizes.

## Summary Table

| run | fixed_actual-est | local_actual-est | entropy_actual-est | best_real_minus_family | redesign verdict |
|---|---:|---:|---:|---:|---|
| fixed128 | 232 | 331 | 904 | 171 | descriptor_redesign_fails |
| variable_scaling | 108 | 178 | 1144.7 | 52 | descriptor_redesign_fails |

## Interpretation
- Fixed/local real modes are consistently above their idealized estimates due to stream/header and coding overhead.
- Entropy-coded real stream remains far above entropy estimate in these runs, indicating model/header inefficiency.
- Best real mode is still often above family-aware on key runs.

## Gate A Decision
- decision: fail
- rationale: estimate-vs-actual descriptor gap remains too large and no consistent real-mode competitiveness against family-aware.
- action: proceed with bounded descriptor-coding refinements before advancing to ZIP-competition claims.
