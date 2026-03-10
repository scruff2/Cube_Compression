# CODEX 5.4 Implementation Requirements
## Cube Route Codec v1.3
### Focus: convert promising idealized cube modes into real encoded-stream wins

## Objective

v1.2 established the key decision point:
- the current **actual** cube stream is still worse than the family-aware baseline
- but several **plausible idealized cube modes** beat the family-aware baseline
- the dominant problem is now **route descriptor coding**, not cube geometry

Therefore, v1.3 shall **not** expand geometry, path complexity, or model scope.

The sole purpose of v1.3 is to answer this implementation question:

> Can the current cube/region design beat the family-aware baseline once route descriptors are coded in a way that matches the v1.2 promising modes?

This must be answered with a real encoded stream, not just analysis tables.

---

# 1) Scope of v1.3

## In scope

v1.3 shall implement, benchmark, and compare these real stream modes:

1. **cube_fixed_length_actual**
   - remove optional length field when phrase length is fixed
   - encode real route tokens with packed fixed-length fields

2. **cube_family_local_id_actual**
   - replace current route field stream with region-local route ids or family-local ids
   - encode real token stream using those local ids

3. **cube_entropy_coded_actual**
   - implement a simple real entropy-coded route stream for route descriptors
   - this may be static-model entropy coding for v1.3
   - keep it transparent and deterministic

4. existing comparison baselines:
   - raw literals
   - flat dictionary baseline
   - family-aware structured baseline
   - zlib or existing general-purpose baseline

## Out of scope

Do **not** implement in v1.3:
- new cube geometry
- new region semantics
- arbitrary 3D traversal rules
- cross-region continuation logic
- adaptive cube mutation
- neural models
- complicated learned probability models
- arithmetic coding sophistication beyond what is necessary to encode route ids and route fields
- broad architecture redesign

v1.3 is a descriptor-coding pass, not a geometry pass.

---

# 2) Required implementation goals

## Goal A: real fixed-length optimization

The current implementation incurs unnecessary cost from an optional length field even when phrase length is fixed.

### Requirement A1
If the benchmark/config uses fixed phrase length and full-route emission, the route stream format shall omit the emitted-length field entirely.

### Requirement A2
The benchmark must report both:
- prior v1.2 analytical estimate for `cube_fixed_length_optimized`
- actual v1.3 measured encoded size for `cube_fixed_length_actual`

### Requirement A3
The report shall explicitly compare:
- old actual route size
- new fixed-length actual route size
- family-aware baseline size

---

## Goal B: real family-local route ids

v1.2 showed that a family-local route naming scheme is promising.

### Requirement B1
Implement a real encoded-stream mode where each route is represented by:
- token type
- region id or family id
- local route id inside that region/family

The local route id may correspond to:
- a combined `(middle_id, suffix_id)` local index
- or another equivalent region-local compact identifier

### Requirement B2
This mode shall be called:
- `cube_family_local_id_actual`

### Requirement B3
The implementation shall provide a deterministic mapping from route structure to local ids and back.

### Requirement B4
The benchmark must report:
- number of local ids defined per region
- number of local ids actually used per region
- average code length of local ids
- total compressed size for this actual stream mode
- difference versus the family-aware baseline

---

## Goal C: real entropy-coded route stream

v1.2 indicates that non-entropy-coded route usage is the largest remaining overhead.

### Requirement C1
Implement a real entropy-coded route descriptor mode called:
- `cube_entropy_coded_actual`

### Requirement C2
The entropy-coded mode may be static-model for v1.3.
That means probabilities may be estimated from:
- the training corpus
- the encoded route usage distribution from a first pass
- or another transparent deterministic method

Do not implement a complicated adaptive entropy model unless needed.

### Requirement C3
At minimum, entropy coding must be applicable to one of these designs:

#### Option 1: whole-route symbol entropy coding
Encode each used route descriptor as a symbol from a route vocabulary.

#### Option 2: factorized entropy coding
Encode route fields with conditional probabilities, such as:
- region id
- local route id given region
- or region id, middle id given region, suffix id given region and middle

Either is acceptable for v1.3, but the implementation must clearly state which one is used.

### Requirement C4
If both whole-route and factorized entropy-coded real streams are feasible, implement both and report both.
If only one is implemented, justify it in the report.

### Requirement C5
The benchmark must compare:
- v1.2 estimated entropy-coded size
- v1.3 actual entropy-coded size
- family-aware baseline size
- flat dictionary baseline size

---

# 3) Required benchmark output changes

For every benchmark run, `metrics.json` and `metrics.md` shall include a new section:

## Real descriptor-coding modes
Report actual compressed size and ratio for:
- `cube_actual_legacy` or equivalent old mode, if preserved for comparison
- `cube_fixed_length_actual`
- `cube_family_local_id_actual`
- `cube_entropy_coded_actual`

Also report any non-implemented mode as `not_implemented` rather than omitting it.

---

# 4) Required decision section

Every benchmark report shall include a new decision block answering:

1. Does `cube_fixed_length_actual` beat family-aware?
2. Does `cube_family_local_id_actual` beat family-aware?
3. Does `cube_entropy_coded_actual` beat family-aware?
4. Which real cube mode is best?
5. How close is each real mode to its v1.2 idealized estimate?
6. Is the remaining gap mostly due to:
   - stream coding inefficiency
   - route vocabulary size
   - low route reuse
   - local-id design
   - entropy model mismatch
7. What is the implementation recommendation?

The report shall produce a machine-readable verdict field such as:
- `descriptor_redesign_succeeds`
- `descriptor_redesign_partially_succeeds`
- `descriptor_redesign_fails`
- `inconclusive`

---

# 5) Required diagnostics

## 5.1 Fixed-length mode diagnostics
Report:
- whether length field is present or omitted
- bits saved relative to legacy route coding
- total token count
- average route token bit length

## 5.2 Family-local-id diagnostics
Report:
- local route table size per region
- actual used local ids per region
- max local id width
- average local id width
- region id width
- token overhead width
- total size breakdown

## 5.3 Entropy-coded diagnostics
Report:
- coding model used
- symbol alphabet size
- estimated entropy
- actual coded bits
- coding overhead if any
- mismatch between estimated and actual entropy-coded bits

## 5.4 Fair-baseline diagnostics
Continue reporting full breakdowns for:
- flat dictionary baseline
- family-aware baseline

These remain mandatory.

---

# 6) Required file-format work

## 6.1 Route stream formats
The implementation shall support explicit binary serialization formats for each actual cube mode.

At minimum:
- one legacy/fixed-width route format
- one family-local-id route format
- one entropy-coded route format if implemented

## 6.2 Decoder support
The decoder shall be able to decode each supported route stream mode exactly.

## 6.3 Stream metadata
Encoded files must identify which route stream mode was used.
This may be done via a small header or metadata field.

---

# 7) Required CLI changes

Add support to select route stream mode explicitly during benchmark and encode.

Examples:

```bash
python -m cube_codec.cli encode --config sample_config.json --cube-dir artifacts --input test.bin --output out.bin --mode cube_fixed_length_actual
python -m cube_codec.cli encode --config sample_config.json --cube-dir artifacts --input test.bin --output out.bin --mode cube_family_local_id_actual
python -m cube_codec.cli encode --config sample_config.json --cube-dir artifacts --input test.bin --output out.bin --mode cube_entropy_coded_actual
```

The benchmark command shall evaluate all implemented actual cube modes in one run.

---

# 8) Required matrix changes

Extend benchmark matrix output to include columns for:
- `cube_fixed_length_actual_bits`
- `cube_family_local_id_actual_bits`
- `cube_entropy_coded_actual_bits`
- `best_real_cube_mode`
- `best_real_cube_minus_family_aware_bits`
- `descriptor_redesign_verdict`

Also include a markdown summary section:
- runs where any **real** cube mode beats family-aware
- runs where only idealized cube modes beat family-aware

This distinction is critical.

---

# 9) Required tests

Add/update tests for:

## 9.1 Fixed-length stream tests
- route encoding omits length when phrase length is fixed
- decoder round-trip succeeds
- actual bit count matches expected packed structure

## 9.2 Family-local-id tests
- deterministic region-local id mapping
- encode/decode round-trip
- local id packing correctness

## 9.3 Entropy-coded stream tests
- encode/decode round-trip for entropy-coded mode
- deterministic output with fixed model
- actual coded size is reported correctly

## 9.4 Benchmark tests
- metrics include all new actual modes
- decision fields are populated
- reports compare actual modes vs v1.2 estimates

All existing tests must continue to pass.

---

# 10) Required README updates

README shall be updated to explain:
- why v1.3 exists
- how to run each new mode
- how to interpret the decision fields
- the difference between:
  - legacy cube route coding
  - family-local-id coding
  - entropy-coded route stream
- what constitutes success or failure in v1.3

---

# 11) Required success criteria

v1.3 is successful if it yields a clear implementation verdict.

## Strong success
At least one **real** cube stream mode beats the family-aware baseline on the intended structured synthetic corpus and preferably on at least one additional relevant corpus.

## Partial success
A real cube stream mode reaches near parity with family-aware and the remaining gap is small, well-explained, and clearly attributable to stream coding details rather than geometry.

## Failure
No real cube stream mode beats or approaches family-aware, even though idealized v1.2 modes appeared promising.

That would imply the idealized gains are not realistically capturable and the cube should likely be deprioritized as a compression mechanism.

---

# 12) Required implementation restraint

Do not add new speculative compression ideas in v1.3.
Do not change the cube structure to try to rescue the result.
Do not broaden the experiment matrix beyond what is needed.

The only goal is to turn the promising v1.2 descriptor analyses into actual encoded-stream measurements.

---

# 13) Deliverables

v1.3 shall deliver:
- updated code implementing the new actual route stream modes
- updated tests
- updated README
- benchmark outputs showing real-mode comparisons
- matrix outputs including real-vs-idealized distinctions
- clear recommendation on whether to continue or stop pursuing the cube approach

---

# 14) Suggested short cover note

Use this with the request if helpful:

> Please implement v1.3 as a tightly scoped descriptor-coding pass. Do not modify cube geometry. The purpose is to convert the promising v1.2 idealized cube modes into real encoded-stream modes and determine whether any real cube stream can beat the family-aware baseline. Prioritize determinism, transparent reporting, and fair comparison over sophistication.
