# Phase 2 Descriptor Gap Report (Post-Refinement)

| run | fixed_actual-est | local_actual-est | entropy_actual-est | best_real_minus_family | redesign verdict |
|---|---:|---:|---:|---:|---|
| fixed128 | 240 | 339 | 712 | 179 | descriptor_redesign_fails |
| variable_scaling | 100 | 170 | 792.7 | 44 | descriptor_redesign_fails |

## Interpretation
- Entropy stream overhead dropped after route-only/canonical refinements, but remains far from entropy estimate.
- Fixed/local modes still carry substantial practical overhead over idealized estimates.
- Best real cube mode still loses to family-aware on both preset runs.

## Gate A Decision
- decision: fail
- status rationale: descriptor estimate-vs-actual gap remains materially large; no repeatable real-mode win in these preset runs.
