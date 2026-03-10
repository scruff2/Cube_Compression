# Cube Route Codec v1.5 Requirements
## Large-Cube Scaling Hypothesis Test
### Purpose: determine whether substantially larger cubes and larger training corpora unlock a regime where real cube modes beat the family-aware baseline

## Objective

v1.4 showed that longer phrases can materially increase route span, but the real cube codec still generally loses to the family-aware baseline in the detailed runs examined. Because compute and storage headroom remain available, the next step is a **bounded scaling experiment**, not a new architectural redesign.

The purpose of v1.5 is to answer one specific question:

> If the cube is allowed to become substantially larger and is trained on materially larger corpora, while preserving the same geometry and descriptor families, do any real cube modes become consistently competitive with or superior to the family-aware baseline?

This is a scaling hypothesis test. It is not permission to broaden geometry, invent new path systems, or change the conceptual codec.

---

## Top-level scope

v1.5 shall focus on these five things only:

1. scale training corpus size materially upward
2. scale cube capacity materially upward
3. test longer fixed and variable-length phrase regimes under that larger capacity
4. preserve fair comparison against the strongest baselines
5. produce clear decision outputs about whether larger cubes help enough to matter

Do not add unrelated algorithmic sophistication.

---

# 1) Hard constraints

## 1.1 No geometry redesign
Do not add:
- arbitrary 3D walks
- new region graph topologies
- cross-region continuation logic
- new semantic region classes
- learned geometry placement systems

Retain the current region-family geometry.

## 1.2 No new codec family
Do not replace the current cube codec with a different coding concept.
The point is to test scale, not pivot architecture.

## 1.3 Preserve comparability
All v1.5 runs must remain directly comparable to:
- flat dictionary baseline
- family-aware baseline
- general-purpose baseline
- existing real cube modes from v1.3/v1.4 where applicable

---

# 2) Required experimental question

Every v1.5 run must ultimately help answer:

1. Does a larger cube lead to materially longer real route usage?
2. Does a larger cube improve real cube competitiveness against family-aware?
3. Does descriptor efficiency degrade as cube size grows?
4. Is there any repeatable scaling regime where a real cube mode wins?

The implementation and reporting should revolve around these questions.

---

# 3) Required scaling dimensions

v1.5 shall support scaling along these dimensions:

## 3.1 Training corpus size
Support materially larger train corpora than prior smoke-scale runs.
Expose config for:
- max training bytes or bits to ingest
- optional sampling cap
- reproducible subsampling seed when sampling is enabled

## 3.2 Cube capacity
Expose config for:
- max regions
- max selected phrases
- max variants per region
- max extracted phrases
- optional per-length-class caps

The implementation must be able to build cubes significantly larger than the earlier 32-byte / 48-byte toy payloads.

## 3.3 Phrase regimes
Support these regimes in scaling studies:
- fixed 128
- fixed 256
- variable-length [64, 128, 192, 256]

## 3.4 Overlap-aware extraction
Support extraction stride and overlap strategy in scaling runs, since longer useful phrases may emerge only under overlapping extraction.

---

# 4) Required configuration additions

Add or preserve config support for the following scaling controls:

```json
{
  "max_training_bytes": null,
  "train_sampling_seed": 123,
  "max_extracted_phrases": 200000,
  "max_selected_phrases": 50000,
  "max_regions": 1024,
  "max_middle_variants": 32,
  "max_suffix_variants": 32
}
```

Exact defaults may differ, but the implementation shall support materially larger limits than earlier versions.

Also support:
```json
{
  "phrase_mode": "fixed",
  "phrase_length": 128,
  "stride": 32,
  "overlap_strategy": "rolling"
}
```

and

```json
{
  "phrase_mode": "variable",
  "phrase_lengths": [64, 128, 192, 256],
  "stride": 32,
  "overlap_strategy": "rolling"
}
```

---

# 5) Required benchmark regimes

v1.5 shall run both synthetic and real-corpus scaling experiments.

## 5.1 Synthetic scaling regimes
Extend or reuse synthetic corpus generation for larger runs in these modes:
- exact-repeat
- prefix-variant
- family-mixture
- shifted-overlap

These shall be runnable at larger sizes than earlier smoke tests.

## 5.2 Real-corpus scaling regimes
If a larger narrow-domain corpus is available, benchmark on that as well.
If no larger real corpus is available, synthetic scaling must still be completed.

## 5.3 Length regimes
For each selected corpus family, support these benchmark families:
- fixed 128
- fixed 256
- variable-length

---

# 6) Required matrix study

Add or extend a matrix runner for large-cube scaling.

Required sweep dimensions:
- training corpus size tier
- max regions
- max selected phrases
- phrase mode / phrase length regime
- extraction stride
- max variants per region

Do not add unrelated sweep dimensions.

Example size tiers:
- small
- medium
- large
- extra_large

Exact byte sizes may be configurable, but the summary must clearly report the actual ingested training size.

---

# 7) Required real cube modes

Retain and benchmark the existing real cube modes where applicable:
- cube_actual_legacy
- cube_fixed_length_actual
- cube_family_local_id_actual
- cube_entropy_coded_actual

If a mode is not meaningful in a given regime, state that explicitly in outputs rather than silently omitting it.

---

# 8) Required baselines

Every benchmark run must include:

## 8.1 Flat dictionary baseline
Extended to the same corpus and phrase regime.

## 8.2 Family-aware baseline
This remains the primary comparison target.

## 8.3 General-purpose baseline
At least one conventional compressor such as zlib, zstd, or lzma.

## 8.4 Analysis baselines
Retain existing oracle/idealized analysis modes where available, but keep them clearly separate from real modes.

---

# 9) Required scale-aware diagnostics

## 9.1 Cube size diagnostics
For every run, report:
- cube payload bits
- cube payload bytes
- metadata bytes
- total shared artifact size
- region count built
- region count used
- selected phrases
- selected phrases by length class
- variants by region statistics

## 9.2 Route span diagnostics
For every run, report:
- average emitted bits per route
- median emitted bits per route
- max emitted bits per route
- emitted length distribution
- coverage by length class

## 9.3 Descriptor efficiency diagnostics
For every run, report:
- average descriptor bits per route
- descriptor bits per emitted source bit
- top-used route counts
- unique route count
- whether descriptor efficiency gets worse as cube size increases

## 9.4 Larger-cube utilization diagnostics
Report whether increased cube capacity was actually used:
- fraction of regions used
- fraction of selected phrases that were ever exercised in encoding
- whether larger cubes created longer real route selections or merely more unused capacity

## 9.5 Comparative diagnostics
For every run, explicitly compare:
- best real cube mode
- family-aware
- flat dictionary
- general-purpose baseline

---

# 10) Required scaling decision outputs

Each benchmark run shall emit at least:

- `scaling_train_bits`
- `scaling_cube_payload_bits`
- `scaling_region_count`
- `scaling_best_real_cube_mode`
- `scaling_best_real_cube_bits`
- `scaling_best_real_cube_minus_family_aware_bits`
- `scaling_any_real_cube_beats_family_aware`
- `scaling_average_route_emitted_bits`
- `scaling_verdict`
- `scaling_recommendation`

Allowed verdict values:
- `scaling_promising`
- `scaling_marginal`
- `scaling_not_helping`
- `inconclusive`

Interpretation guidance:
- `scaling_promising` if one or more real cube modes beat family-aware in a repeatable scaling regime
- `scaling_marginal` if larger cubes help but wins remain sparse or fragile
- `scaling_not_helping` if larger cubes mostly increase capacity/cost without creating real wins

---

# 11) Required matrix summary outputs

The matrix summary shall include, for each run:

- training corpus size
- phrase regime
- stride
- cube payload size
- metadata size
- region count
- average route emitted bits
- best real cube mode
- best real cube bits
- family-aware bits
- best_real_cube_minus_family_aware_bits
- scaling verdict

The markdown summary shall also include these sections:

## 11.1 Runs where any real cube mode beats family-aware
List all such runs explicitly.

## 11.2 Runs where larger cubes increased route span but still lost
List runs where average route length improved materially but family-aware still won.

## 11.3 Runs where scaling mostly created unused capacity
List runs with low region utilization or weak larger-cube usage.

## 11.4 Final scaling interpretation
Provide a plain-language summary of whether cube scale is rescuing the idea.

---

# 12) Required success criteria

v1.5 is successful if it provides a clear answer to the scaling hypothesis.

Success does **not** require the cube to win overall.

v1.5 is successful if it can clearly determine one of the following:

## Outcome A
Larger cubes create a repeatable regime where one or more real cube modes beat family-aware.

Interpretation:
- scale matters
- cube investigation can continue, but only in that scaling niche

## Outcome B
Larger cubes increase route span and coverage, but real cube modes still generally lose.

Interpretation:
- scale helps mechanically but not enough practically
- cube remains inferior as a practical codec

## Outcome C
Larger cubes mostly add unused capacity or descriptor burden and do not materially improve competitiveness.

Interpretation:
- the scaling hypothesis is not supported
- stop cube work

---

# 13) Required restraint

Do not add:
- arbitrary geometry changes
- new modeling paradigms
- large entropy-coder redesigns unrelated to scale
- production optimization
- UI or workflow extras

The goal is a fair and disciplined scale test.

---

# 14) Deliverables

v1.5 shall include:
- updated code
- updated tests
- updated README with v1.5 instructions
- one or more large-cube sample configs
- benchmark outputs and matrix summaries with required scaling fields
- clear markdown interpretation of whether scale helps enough

---

# 15) Recommended experiment set

Run at least these experiment groups:

## Experiment group 1: synthetic exact-repeat scaling
- small/medium/large cube capacity
- fixed 128 and fixed 256

## Experiment group 2: synthetic prefix-variant scaling
- small/medium/large cube capacity
- fixed 128 and fixed 256

## Experiment group 3: synthetic family-mixture scaling
- variable-length mode
- small/medium/large cube capacity

## Experiment group 4: shifted-overlap scaling
- variable-length mode
- overlapping extraction stride
- medium/large capacity

## Experiment group 5: larger real narrow corpus, if available
- fixed 128
- fixed 256
- variable-length

Each run shall produce:
- metrics.json
- metrics.md
- diagnostics.json
- diagnostics.md

Each matrix run shall additionally produce:
- summary.csv
- summary.md

---

# 16) Code quality priority

Prioritize:
1. clarity
2. determinism
3. fair comparison
4. observability
5. restraint

Do not over-engineer.

---

# 17) Cover note for CODEX

Use this note with the requirements:

> Please implement v1.5 as a bounded large-cube scaling hypothesis test. Do not broaden geometry or add unrelated codec ideas. The goal is to determine whether substantially larger cubes and larger training corpora unlock a repeatable regime where any real cube mode beats the family-aware baseline. Prioritize fair scaling experiments, clear diagnostics, and explicit stop/continue evidence over sophistication.
