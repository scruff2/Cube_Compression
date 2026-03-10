# CODEX 5.4 Requirements
## Cube Route Codec v1.2
### Final diagnostic iteration for the geometric hypothesis

## Purpose

v1.0 established that the prototype is operational and lossless.

v1.1 established that:
- the cube/route codec can achieve full route coverage on structured corpora
- the region/family clustering is functioning
- the cube codec still loses badly to both the flat dictionary baseline and the family-aware structured baseline
- the main failure mode is descriptor inefficiency, not coverage failure

The purpose of v1.2 is **not** to improve the product broadly.
The purpose of v1.2 is to answer one specific question:

> If route descriptor overhead were made close to ideal, could the cube-based representation beat the family-aware structured baseline?

This is the final decision-point iteration for the geometric compression hypothesis.

---

## Top-level objective

Implement a diagnostics-first analysis pass that quantifies how much of the cube codec’s loss is due to:

1. current route field overhead
2. non-entropy-coded descriptor representation
3. unnecessary fixed fields for fixed-length phrases
4. lack of family-local compact ids

The goal is to determine whether the cube has any remaining plausible compression advantage after descriptor overhead is idealized.

---

## Non-goals

Do **not** implement any of the following in v1.2:
- arbitrary 3D walk support
- new cube geometries
- neural models
- arithmetic coding of the actual output stream
- cross-region continuation logic
- adaptive online training
- performance tuning for production use
- broad architecture changes

v1.2 is an **analysis iteration**, not a feature iteration.

---

## Required outcome

At the end of v1.2, the benchmark reports must clearly answer:

1. How much of the cube deficit is due to current descriptor coding?
2. How much would the cube improve under idealized descriptor assumptions?
3. Would the cube beat the family-aware structured baseline under those idealized assumptions?
4. If not, is there any remaining evidence that geometry itself adds value?

---

# 1) New analysis modes to implement

Implement the following analysis modes for the cube codec.

These are **analysis-only** modes unless otherwise stated. They do not need to produce a physical compressed stream unless explicitly required.

## 1.1 Actual route cost mode
This is the existing measured mode.

Definition:
- use the current route token fields and current cost model exactly as in v1.1

Purpose:
- provide the baseline measured cube result

Label in reports:
- `cube_actual`

---

## 1.2 Fixed-length optimized route mode
Analysis mode only.

Assumptions:
- if phrase length is fixed for a run, route descriptors do not need an explicit emit-length field
- any route fields that are constant across all routes in the run should be omitted from estimated cost

Purpose:
- isolate waste caused by unnecessary fixed fields

Label in reports:
- `cube_fixed_length_optimized`

Required report outputs:
- estimated average bits per route token
- estimated total compressed bits
- improvement over `cube_actual`

---

## 1.3 Empirical entropy route mode
Analysis mode only.

Assumptions:
- estimate the ideal code length for route descriptors using empirical frequencies observed in the encoded token stream
- compute both:
  - whole-route symbol entropy estimate
  - factorized field entropy estimate

Required estimates:
- whole-route entropy:
  \[
  H(Route)
  \]
- factorized entropy:
  \[
  H(Region) + H(Middle\mid Region) + H(Suffix\mid Region, Middle)
  \]
- if length exists, include:
  \[
  H(Length\mid Region, Middle, Suffix)
  \]

Purpose:
- estimate how much the cube could improve if descriptor coding were near-optimal without changing geometry

Label in reports:
- `cube_entropy_estimated`

Required report outputs:
- estimated average bits per route under whole-route entropy
- estimated average bits per route under factorized entropy
- estimated total compressed bits under both variants
- gap between actual and estimated route coding

---

## 1.4 Family-local id mode
Analysis mode only, but it may be implemented as an alternate costing path.

Assumptions:
- within each region/family, assign compact local ids to distinct used route variants
- cost route descriptors as:
  - region id cost
  - local route id cost within the region
- do **not** require explicit middle/suffix field accounting in this mode

This is meant to answer:
- if route naming were made compact at the family level, would the cube become competitive?

Label in reports:
- `cube_family_local_id`

Required outputs:
- average local-id width per used region
- estimated average bits per route
- estimated total compressed bits
- comparison against family-aware baseline

---

## 1.5 Minimal cube descriptor oracle
Analysis-only oracle.

This is the most important new mode.

Assumptions:
- for each used route, compute the shortest idealized code length consistent with uniquely identifying that route among the used routes, or among the routes in its family, depending on the chosen oracle variant
- do not include fields that would be unnecessary under ideal route naming
- this is an **oracle lower bound** on descriptor cost under the current cube structure

Required oracle variants:

### Oracle A: used-route oracle
Code length based on number of distinct routes actually used in the encoded stream:
\[
\lceil \log_2(|UsedRoutes|) \rceil
\]
or, preferably, an empirical entropy estimate over used-route frequencies.

### Oracle B: region-local used-route oracle
Code route as:
- region identifier
- local id among routes used in that region

### Oracle C: ideal factorized oracle
Use the shortest plausible factorized descriptor based on observed support sets.

Purpose:
- determine whether the cube could plausibly beat the family-aware baseline even under very favorable descriptor assumptions

Label in reports:
- `cube_oracle_used_route`
- `cube_oracle_region_local`
- `cube_oracle_factorized`

---

# 2) Comparative baseline requirements

Keep all v1.1 baselines and add stronger comparison framing.

Required baselines in every relevant report:
- `cube_actual`
- `cube_fixed_length_optimized`
- `cube_entropy_estimated`
- `cube_family_local_id`
- `cube_oracle_used_route`
- `cube_oracle_region_local`
- `cube_oracle_factorized`
- `flat_dictionary`
- `family_aware`
- `phrase_family_oracle`
- `raw_literals`
- `zlib` or existing general-purpose baseline

---

# 3) Required decision analysis

Add a benchmark decision section that explicitly answers the following.

## 3.1 Geometry viability question
For each run, determine:

> Does any cube idealization mode beat the family-aware structured baseline?

If yes, report:
- which mode(s) do so
- by how much
- whether the gain is marginal or substantial

If no, report clearly:
- that the cube does not appear competitive even under idealized descriptor assumptions

---

## 3.2 Descriptor-overhead attribution
For each run, report how much of the cube-vs-family-aware gap is attributable to:
- fixed length field overhead
- explicit field decomposition overhead
- non-entropy-coded route usage
- global versus local route naming inefficiency

This should be reported numerically where possible.

Example format:
- actual cube average bits/phrase: X
- fixed-length optimized: Y
- entropy-estimated: Z
- family-local id: W
- family-aware baseline: B
- remaining gap after idealization: W - B

---

## 3.3 Final verdict label
Each benchmark report must classify the result into exactly one of these labels:

- `geometry_promising`
- `geometry_marginal`
- `geometry_unnecessary`
- `inconclusive`

Definitions:

### geometry_promising
At least one realistic idealization mode makes the cube clearly competitive with or better than the family-aware baseline.

### geometry_marginal
The cube approaches the family-aware baseline only under very favorable assumptions, with little remaining headroom.

### geometry_unnecessary
Even strong idealizations do not let the cube beat the family-aware baseline.

### inconclusive
Data or run conditions are too weak to support a decision.

---

# 4) Required report changes

## 4.1 metrics.md additions
Add a section:

### Cube descriptor idealization table
Must include a table with rows for all cube modes and columns for:
- total estimated compressed bits
- bits per source bit
- compression ratio
- average bits per route token
- delta vs `cube_actual`
- delta vs `family_aware`

---

## 4.2 diagnostics.md additions
Add a section:

### Descriptor-overhead diagnosis
Must include:
- route count
- used route count
- used route frequency distribution summary
- region-local route support sizes
- field-wise route cost contribution
- idealized route cost estimates
- narrative interpretation of the biggest overhead source

Also add:

### Cube viability decision
This section must explicitly state whether geometry still appears to have a plausible path to victory.

---

## 4.3 diagnostics.json additions
Must expose machine-readable fields for all new modes and all decision outputs.

Suggested structure:

```json
{
  "cube_modes": {
    "cube_actual": {...},
    "cube_fixed_length_optimized": {...},
    "cube_entropy_estimated": {
      "whole_route": {...},
      "factorized": {...}
    },
    "cube_family_local_id": {...},
    "cube_oracle_used_route": {...},
    "cube_oracle_region_local": {...},
    "cube_oracle_factorized": {...}
  },
  "decision": {
    "beats_family_aware_in_any_mode": true,
    "best_cube_mode": "cube_entropy_estimated.factorized",
    "final_verdict": "geometry_marginal"
  }
}
```

---

# 5) Required corpus coverage

Run v1.2 on at least the following corpora or modes.

## 5.1 Existing synthetic corpus from v1.1
Reuse the same synthetic run type that produced the current discouraging result.

Purpose:
- maintain continuity with prior findings

## 5.2 Prefix-variant synthetic corpus
This is the most important corpus for v1.2.

Purpose:
- test the cube in the niche it was designed for

## 5.3 Family-mixture synthetic corpus
Purpose:
- test whether local family reuse improves idealized descriptor economics

## 5.4 Exact-repeat control corpus
Purpose:
- verify that even idealized cube descriptors should usually not beat the best explicit dictionary on pure exact repetition

---

# 6) Required benchmark matrix extension

Do not broaden the sweep dimensions. Reuse v1.1 benchmark matrix support, but add summary columns for the new cube idealization modes.

Required additional summary columns:
- `cube_actual_bits`
- `cube_fixed_length_optimized_bits`
- `cube_entropy_whole_route_bits`
- `cube_entropy_factorized_bits`
- `cube_family_local_id_bits`
- `cube_oracle_region_local_bits`
- `family_aware_bits`
- `best_cube_mode`
- `best_cube_bits`
- `best_cube_minus_family_aware`
- `geometry_verdict`

The matrix summary markdown must include a section listing runs where any cube idealization beats the family-aware baseline.

---

# 7) Required CLI additions

No large CLI redesign is needed.

Add only what is necessary to expose the new analysis modes.

Acceptable approaches:
- extend existing `benchmark` command to compute all analysis modes automatically
- optionally add a flag such as:

```bash
python -m cube_codec.cli benchmark --config ... --train ... --test ... --analysis-level full
```

If flags are added, document them in the README.

---

# 8) Required implementation details

## 8.1 Cost-model module updates
Update or extend `cube_codec/cost_model.py` to support:
- actual measured route field cost
- fixed-length-optimized cost
- empirical entropy estimates
- family-local id estimates
- oracle lower-bound estimates

This module should remain transparent and easy to inspect.

## 8.2 Benchmark module updates
Update `cube_codec/benchmark.py` so that one benchmark run computes all cube modes and all comparisons in a single pass.

## 8.3 Baselines module updates
If useful, extend `cube_codec/baselines.py` only enough to keep comparisons consistent and clearly formatted.

## 8.4 No stream-format changes required
You do not need to change the actual encoded stream format unless needed for consistency in measured `cube_actual` mode.

All idealized cube modes may remain analysis-only estimates.

---

# 9) Required tests

Add tests for the new analysis logic.

Minimum required tests:

## 9.1 Fixed-length optimization test
Verify that when phrase length is fixed, the optimized analysis mode does not charge an explicit length field.

## 9.2 Entropy estimate sanity test
Use a small synthetic route distribution and verify computed entropies are reasonable and consistent.

## 9.3 Family-local id estimate test
Verify that local-id costing is lower than or equal to explicit field costing when route support is small.

## 9.4 Oracle monotonicity test
Verify that oracle modes never estimate higher cost than the corresponding actual mode.

## 9.5 Report output test
Verify that metrics and diagnostics outputs include all required v1.2 sections and fields.

## 9.6 Matrix summary test
Verify that matrix outputs contain new summary columns and a geometry verdict.

---

# 10) Required README updates

Update README with a v1.2 section describing:
- the purpose of descriptor idealization analysis
- the meaning of each cube mode
- the meaning of the final geometry verdict labels
- example commands for running a full diagnostic benchmark
- how to interpret a result where the cube still loses under oracle assumptions

---

# 11) Required interpretation guidance

Every markdown report must conclude with a short explicit recommendation in plain language.

Possible recommendations:
- `continue cube investigation`
- `cube only worth pursuing if descriptor redesign is implemented`
- `pivot to family-aware structured coding`
- `insufficient evidence, rerun on stronger corpus`

This recommendation must be derived from the benchmark results and verdict logic.

---

# 12) Success criteria for v1.2

v1.2 is successful if it yields a clear answer to this question:

> After idealizing route descriptor overhead, does the cube still have any plausible advantage over the family-aware structured baseline?

Success does **not** require the cube to win.

Success requires the report to make one of these conclusions defensibly:
- yes, the cube still has credible headroom
- no, the cube appears unnecessary
- only marginal headroom remains

---

# 13) Preferred coding priority

Prioritize in this order:
1. correctness of analysis
2. fairness of comparison
3. interpretability of outputs
4. determinism
5. minimal code changes

Do not prioritize new compression features.

---

# 14) Deliverables

v1.2 deliverables must include:
- updated code
- updated tests
- updated README
- benchmark outputs containing all new cube analysis modes
- matrix summary with geometry verdicts

---

# 15) Cover note to CODEX

Use this exact intent for implementation:

> Implement v1.2 as a final diagnostic iteration for the geometric hypothesis. Do not broaden scope. The purpose is to determine whether the cube could become competitive with the family-aware baseline if descriptor overhead were near-ideal. Add analysis modes, oracle-style comparisons, report-level verdicts, and minimal supporting tests. Prefer analysis over new codec features.
