# Phase 1 Gate Memo

## Scope Completed

- Locked corpus manifest added: `docs/corpus_manifest.json`
- Preset configs added: `configs/presets/fixed128.json`, `configs/presets/variable_scaling.json`
- Preset benchmark artifacts generated and stored in `reports/`

## Evidence

- `reports/preset_fixed128_metrics.json`
- `reports/preset_variable_metrics.json`
- Deterministic benchmark schema/repro tests passing (`test_benchmark_schema.py`)

## Gate Decision

- status: `pass_with_limitations`

## Rationale

- Structured synthetic corpus families and locked splits are in place.
- One-command presets are available and validated.
- A larger real narrow-domain corpus is still missing; this limits external validity for later phases.

## Next Step

Proceed to Phase 2 descriptor estimate-vs-actual gap analysis (Gate A).
