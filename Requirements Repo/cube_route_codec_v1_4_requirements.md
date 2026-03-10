# Cube Route Codec v1.4 Requirements
## Long-Phrase Hypothesis Test
### Purpose: determine whether the cube becomes competitive only when it can encode materially longer structured segments

## Objective

v1.3 established a practical no-go for the current cube codec configuration based on 64-bit phrases and tiny learned cubes. The next step is **not** to broaden geometry or add major complexity.

The purpose of v1.4 is to answer one specific question:

> Does the cube become competitive against the family-aware baseline when it is allowed to learn and encode materially longer phrases, such as 128-bit, 256-bit, and variable-length structured segments?

This is a hypothesis test, not a general optimization pass.

---

## Top-level scope

v1.4 shall focus on these four things only:

1. support longer fixed-length phrase regimes
2. support variable-length structured segment regimes
3. scale the training/build pipeline enough to populate larger cubes meaningfully
4. rerun fair comparisons against the same strongest baselines

Do not add arbitrary new geometry, neural methods, or unrelated codec complexity.

---

# 1) Required experimental regimes

v1.4 shall support these phrase regimes:

## 1.1 Fixed 128-bit phrase regime
- train using 128-bit phrases
- encode/decode using 128-bit route outputs where possible

## 1.2 Fixed 256-bit phrase regime
- train using 256-bit phrases
- encode/decode using 256-bit route outputs where possible

## 1.3 Variable-length structured segment regime
Support phrase lengths drawn from a small fixed set, default:
- 64
- 128
- 192
- 256

This regime is intended to test whether structured phrase families benefit from longer trunks and controlled stop points without paying arbitrary-length overhead.

---

# 2) Implementation constraints

## 2.1 No geometry expansion
Do not add:
- arbitrary 3D walks
- new region graph topologies
- cross-region path continuation
- learned geometry placement
- complex new path grammars

Retain the current region-family structure and descriptor-coding focus.

## 2.2 No major entropy-system redesign
Do not add a large new entropy-coding subsystem beyond what already exists for v1.3 unless needed for parity across long-phrase modes.

## 2.3 Preserve comparability
All new long-phrase experiments must remain directly comparable to:
- flat dictionary baseline
- family-aware baseline
- oracle / analysis baselines already present
- existing cube real modes where applicable

---

# 3) Required configuration support

Add config support for:

## 3.1 Phrase regime selection
Example config fields:
```json
{
  "phrase_mode": "fixed",
  "phrase_length": 128
}
```

```json
{
  "phrase_mode": "variable",
  "phrase_lengths": [64, 128, 192, 256]
}
```

## 3.2 Extraction stride
Support:
- stride equal to phrase length
- stride smaller than phrase length
- a configurable overlap strategy

This is required because longer phrases may only become visible under overlapping extraction.

## 3.3 Training corpus scale controls
Add config fields to control:
- max extracted phrases
- max selected phrases
- max regions
- max variants per region
- optional minimum frequency per phrase length class

These controls are required so larger learned cubes can be populated meaningfully from larger training corpora.

---

# 4) Required training pipeline changes

## 4.1 Fixed-length training support
The training pipeline shall support extracting, selecting, clustering, and building regions for:
- 128-bit phrases
- 256-bit phrases

## 4.2 Variable-length training support
The training pipeline shall support extracting phrases from multiple configured lengths in one run.

Required outputs:
- selected phrase counts by length
- selected source mass by length
- clusters/regions by length
- train coverage by length

## 4.3 Larger-corpus support
The training pipeline shall be capable of operating on materially larger corpora than the tiny v1.x smoke-test corpora.

No production-scale optimization is required, but the implementation must be able to run meaningful longer-phrase experiments without being hard-coded to very small inputs.

---

# 5) Required region/layout support

## 5.1 Longer fixed-length routes
The region layout must support phrase families whose total route output length is:
- 128 bits
- 256 bits

## 5.2 Variable-length family support
For variable-length mode, region metadata shall support one of these approaches:
- family-local length class ids
- family-local stop ids
- fixed enumerated length choices

Do **not** use a wasteful arbitrary integer length field if the length is selected from a small known set.

## 5.3 Length-aware diagnostics
Per region, report:
- region phrase length or length class
- average emitted bits
- route usage by length class
- whether longer routes are actually being used at encode time

---

# 6) Required route stream modes

v1.4 shall preserve existing real stream modes and extend them to the longer phrase regimes where applicable.

Required support:
- cube_fixed_length_actual for 128-bit and 256-bit modes
- cube_family_local_id_actual for 128-bit and 256-bit modes
- entropy-coded real mode if currently implemented for these regimes
- variable-length real mode using compact length-class or stop-id signaling

If a current real mode cannot be cleanly generalized to long phrases, report that limitation explicitly in diagnostics and metrics.

---

# 7) Required baselines

All long-phrase experiments must include:

## 7.1 Flat dictionary baseline
Extended to the same fixed-length and variable-length phrase regimes.

## 7.2 Family-aware baseline
Extended to the same phrase regimes.
This remains the primary comparison target.

## 7.3 Oracle / analysis baselines
Retain and extend the existing oracle analysis where meaningful, especially for variable-length structured families.

## 7.4 General-purpose codec baseline
Retain at least one conventional baseline such as zlib, zstd, or lzma.

---

# 8) Required synthetic corpora additions

Extend the synthetic corpus generator to produce longer-phrase-friendly corpora.

Add or adapt modes so they can emit structured data where:
- 128-bit phrases repeat
- 256-bit phrases repeat
- variable-length families share long prefixes and controlled variants
- phrase overlap exists at shifted offsets

At minimum, support these long-phrase test cases:

## 8.1 Long exact-repeat mode
Exact repeated phrases of length 128 and 256.

Purpose:
- control condition
- should usually favor flat dictionary

## 8.2 Long prefix-variant mode
Long shared prefixes with controlled middle/suffix variants.

Purpose:
- should favor the cube if longer trunks matter

## 8.3 Long family-mixture mode
Several phrase families with different frequencies and different length classes.

Purpose:
- test region allocation and reuse under longer phrases

## 8.4 Long shifted-overlap mode
Long repeated structure that is not perfectly aligned to phrase-length stride.

Purpose:
- test whether overlap-aware extraction unlocks longer useful routes

---

# 9) Required benchmark matrix extensions

Add benchmark matrix support for the long-phrase hypothesis test.

Required sweep dimensions:
- phrase_mode
- phrase_length or phrase_lengths
- extraction stride
- max regions
- max variants per region
- literal block size

Do not add unrelated sweep dimensions.

The matrix summary shall include, per run:
- original bits
- cube size bits/bytes
- metadata size
- selected phrases by length
- regions by length
- average emitted bits per route
- route coverage fraction
- best real cube mode
- best real cube bits
- family-aware bits
- best_real_cube_minus_family_aware_bits
- long_phrase_verdict

---

# 10) Required diagnostics

## 10.1 Length-aware coverage diagnostics
Report:
- route coverage by length class
- literal fallback by length class
- average route-emitted length
- max route-emitted length
- distribution of emitted lengths

## 10.2 Descriptor efficiency by length class
For each length class, report:
- average descriptor bits
- average emitted bits
- descriptor bits per emitted source bit
- top routes by usage

## 10.3 Larger-cube utilization diagnostics
Report:
- cube payload size
- metadata size
- number of regions built
- number of regions used
- per-region emitted bits
- whether larger cube capacity was actually exercised

## 10.4 Comparative diagnostics
For each benchmark run, explicitly compare cube vs family-aware for:
- fixed 128-bit mode
- fixed 256-bit mode
- variable-length mode

---

# 11) Required decision outputs

Each benchmark run shall emit a decision section containing at least:

- `long_phrase_best_real_cube_mode`
- `long_phrase_best_real_cube_bits`
- `long_phrase_best_real_cube_minus_family_aware_bits`
- `long_phrase_any_real_cube_beats_family_aware`
- `long_phrase_best_length_class`
- `long_phrase_verdict`
- `long_phrase_recommendation`

Allowed verdict values:
- `long_phrases_promising`
- `long_phrases_marginal`
- `long_phrases_not_helping`
- `inconclusive`

Interpretation rule:
- If no real long-phrase cube mode beats family-aware, verdict should normally be `long_phrases_not_helping` unless coverage/utilization is clearly too weak to judge.
- If one or more real long-phrase modes beat family-aware on structured corpora, verdict should normally be `long_phrases_promising`.

---

# 12) Required markdown report sections

Each `metrics.md` or diagnostics markdown report for v1.4 shall include:

## 12.1 Long-phrase regime summary
- fixed 128 results
- fixed 256 results
- variable-length results

## 12.2 Longer-segment utilization
- did average emitted length materially increase over 64-bit runs
- were 128/256 routes actually used
- were variable-length longer routes actually selected

## 12.3 Comparative baseline table
Show:
- cube best real mode
- family-aware
- flat dictionary
- general-purpose baseline

## 12.4 Decision section
A plain-language statement answering:
1. Did larger cubes and longer phrases materially increase encoded segment length?
2. Did longer phrases improve cube competitiveness?
3. Did any real cube mode beat family-aware?
4. Is the long-phrase hypothesis supported?

---

# 13) Required success criteria

v1.4 is successful if it provides a clear answer to the long-phrase hypothesis.

Success does **not** require the cube to win overall.

v1.4 is successful if it can clearly determine one of the following:

## Outcome A
Real cube modes beat the family-aware baseline in one or more long-phrase regimes.
Interpretation:
- long phrases are the missing ingredient
- cube investigation should continue in that niche

## Outcome B
Longer phrases increase route span but still do not beat family-aware.
Interpretation:
- longer phrases help coverage but not enough
- cube remains inferior as a practical codec

## Outcome C
Longer phrases do not materially improve route span or competitiveness.
Interpretation:
- larger cube / longer phrase hypothesis is not supported
- stop cube work and keep only family-aware structured coding

---

# 14) Required implementation restraint

Do not add:
- arbitrary new geometry
- neural compression components
- advanced learned clustering beyond what is needed for length support
- production optimization
- unrelated file formats or UI

The goal of v1.4 is a clean hypothesis test.

---

# 15) Deliverables

v1.4 shall include:
- updated code
- updated tests
- updated README with v1.4 instructions
- one or more long-phrase sample configs
- synthetic corpus generation for long-phrase modes
- benchmark and matrix outputs with the required decision fields

---

# 16) Recommended immediate experiment set

After implementation, run at least these experiments:

## Experiment 1
Synthetic exact-repeat, fixed 128

## Experiment 2
Synthetic exact-repeat, fixed 256

## Experiment 3
Synthetic prefix-variant, fixed 128

## Experiment 4
Synthetic prefix-variant, fixed 256

## Experiment 5
Synthetic family-mixture, variable-length [64,128,192,256]

## Experiment 6
Shifted-overlap corpus with overlapping extraction stride

## Experiment 7
At least one larger real narrow corpus, if available

Each experiment shall produce:
- metrics.json
- metrics.md
- diagnostics.json
- diagnostics.md

Matrix runs shall additionally produce:
- summary.csv
- summary.md

---

# 17) Code quality priority

Prioritize:
1. clarity
2. determinism
3. observability
4. fair comparison
5. restraint

Do not over-engineer.

---

# 18) Cover note for CODEX

Use this note with the requirements:

> Please implement v1.4 as a narrow long-phrase hypothesis test. Do not broaden geometry or add unrelated complexity. The goal is to determine whether larger learned cubes and longer fixed or structured variable-length phrases allow any real cube mode to beat the family-aware baseline. Prioritize clean diagnostics and fair comparisons over sophistication.
