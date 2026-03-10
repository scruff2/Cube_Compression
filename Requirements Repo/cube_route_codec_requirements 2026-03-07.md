# Shared 3D Cube Route-Descriptor Lossless Compressor
## Engineering Requirements for CODEX 5.4
### Prototype implementation and test suite specification

## 1. Purpose

Build a proof-of-concept lossless compressor based on a shared 3D binary cube that acts as a reusable structured codebook.

The compressor must:
- train a shared cube from a binary corpus
- encode test data losslessly using route tokens and literal tokens
- decode exactly
- benchmark compression performance, coverage, and search cost
- compare against simple baselines

This is a prototype for field experiments, not a production codec.

---

## 2. Core hypothesis

A shared 3D cube, organized into structured phrase-family regions and traversed by compact route descriptors, can compress a narrow source family better than naive literal transmission and possibly better than a simple explicit flat phrase dictionary.

---

## 3. Scope of version 1

### In scope
- fixed-length phrase extraction during training
- region-based cube layout
- one route token representing one deterministic region traversal
- literal fallback
- dynamic-programming encoder
- exact decoder
- binary and debug-readable serialized formats
- benchmark harness
- automated test suite

### Out of scope
- arbitrary 3D walk search
- cross-region continuation tokens
- adaptive online cube updates during encoding
- learned neural models
- advanced entropy coding in v1
- production optimization
- attempts to beat general-purpose codecs in all settings

---

## 4. Assumptions

1. Encoder and decoder share the same cube file and metadata.
2. Shared cube cost is amortized and excluded from per-message compression ratio, but must still be reported separately.
3. Target corpus is narrow, repetitive, and phrase-rich.
4. Reconstruction must be exact bit-for-bit.
5. Version 1 uses structured region geometry, not free-form geometry.

---

## 5. Conceptual model

The shared cube is represented as a 3D binary array:

```python
cube[region_id][lane_id][position]
```

Interpretation:
- `region_id`: phrase-family region
- `lane_id`: trunk lane or branch lane
- `position`: phrase progression coordinate

Each region represents a phrase family with:
- one common trunk prefix
- multiple middle-variant lanes
- multiple suffix-variant lanes or suffix tables

A route token specifies a deterministic traversal through one region. The decoder reconstructs the route and emits the corresponding bits. Literal tokens are used when no profitable route is available.

---

## 6. Deliverables

CODEX 5.4 must generate:

1. source code for the prototype compressor
2. source code for the decoder
3. training pipeline
4. cube builder and serializer
5. route index builder
6. benchmark harness
7. baseline implementations
8. automated unit tests
9. automated integration tests
10. sample configuration files
11. README with setup and usage instructions

---

## 7. Required project structure

Use Python for the first prototype.

Suggested package structure:

```text
cube_codec/
    __init__.py
    config.py
    bitutils.py
    corpus.py
    phrases.py
    clustering.py
    region_builder.py
    cube_model.py
    cube_io.py
    route_model.py
    route_index.py
    encoder.py
    decoder.py
    baselines.py
    benchmark.py
    metrics.py
    cli.py
    tests/
        test_bitutils.py
        test_cube_io.py
        test_route_model.py
        test_region_builder.py
        test_encoder_decoder_roundtrip.py
        test_prefix_index.py
        test_benchmarks.py
```

A top-level `README.md` and `requirements.txt` must also be created.

---

## 8. Data models

### 8.1 Region layout model

Implement a region layout model equivalent to:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class RegionLayout:
    region_id: int
    prefix_bits: str
    middle_variants: list[str]
    suffix_variants: list[str]
    route_length: int
    prefix_length: int
    middle_length: int
    suffix_length: int
```

Notes:
- bitstrings may initially be stored as Python strings of `'0'` and `'1'` for clarity
- later they may be optimized to packed bitarrays or bytes

### 8.2 Cube metadata model

Implement metadata with at least:

```python
from dataclasses import dataclass

@dataclass
class CubeMetadata:
    version: str
    region_count: int
    lanes_per_region: int
    positions_per_lane: int
    phrase_length: int
    middle_variants_per_region: int
    suffix_variants_per_region: int
```

### 8.3 Token models

Implement two token types.

#### Literal token

```python
@dataclass
class LiteralToken:
    token_type: str  # 'L'
    bit_length: int
    payload_bits: str
```

#### Route token

```python
@dataclass
class RouteToken:
    token_type: str  # 'R'
    region_id: int
    middle_id: int
    suffix_id: int
    emit_length: Optional[int] = None
```

### 8.4 Encoded stream model

Implement an encoded stream as an ordered sequence of tokens.

Version 1 must support:
- a debug-friendly JSON format
- a compact binary-packed format for benchmarking

---

## 9. Route semantics

For version 1, route reconstruction must be deterministic and defined as:

```text
output = prefix(region) + middle(region, middle_id) + suffix(region, suffix_id)
```

If `emit_length` is present, the output must be truncated to exactly that many bits.

The decoder must produce identical output for identical cube and token stream inputs.

---

## 10. Training pipeline requirements

### 10.1 Input

Training pipeline must accept one or more binary files.

### 10.2 Phrase extraction

Extract fixed-length phrases from the corpus.

Configurable parameters:
- `phrase_length`, default 64 bits
- `stride`, default equal to `phrase_length`, optionally smaller for overlap
- `min_frequency`

Output:
- phrase frequency table
- counts
- corpus statistics

### 10.3 Phrase selection

Select the top-N useful phrases for cube inclusion.

Version 1 selection criterion:
- descending frequency

Optional later criterion:
- weighted utility estimate based on route cost assumptions

### 10.4 Phrase clustering

Cluster phrases into phrase families that fit a trunk-middle-suffix structure.

Version 1 clustering can be greedy and deterministic.

Required clustering signals:
- shared prefix length
- middle similarity
- optional suffix grouping

Expected outputs for each cluster:
- common prefix
- set of middle variants
- set of suffix variants
- phrase membership

### 10.5 Region construction

For each selected cluster:
1. determine useful common prefix
2. extract middle variants
3. extract suffix variants
4. construct one `RegionLayout`
5. map the region into cube coordinates

---

## 11. Cube builder requirements

The cube builder must:

1. allocate cube dimensions based on selected regions
2. populate trunk prefix bits into lane 0 of each region
3. populate middle variants into deterministic middle lanes
4. populate suffix variants into deterministic suffix lanes or deterministic suffix coordinate tables
5. serialize cube bits and metadata to disk

Required output files:
- `cube.bin` or equivalent compact binary cube payload
- `cube_metadata.json`
- optional `cube_debug.json`

---

## 12. Serialization requirements

### 12.1 Cube serialization

Must support:
- save cube bits to binary
- save metadata to JSON
- load both back with exact fidelity

### 12.2 Encoded stream serialization

Must support:
- debug JSON token stream
- binary-packed token stream

Binary format may be simple and prototype-oriented, but must be deterministic and documented in the README.

---

## 13. Prefix index requirements

The encoder must build an index that maps route prefixes to route candidates.

### 13.1 Index key
- first `k` bits of the route output
- configurable `k`, default 12 or 16

### 13.2 Index value
A list of candidate routes:

```python
prefix -> [(region_id, middle_id, suffix_id)]
```

### 13.3 Index build source
Index must be generated automatically from cube and metadata.

### 13.4 Verification
Full route matches must always be verified against source bits before use.

---

## 14. Encoder requirements

### 14.1 General behavior

The encoder must encode an input bitstream into a minimum-cost sequence of route and literal tokens.

### 14.2 Candidate generation

At each input bit position:
1. read source prefix
2. query prefix index for candidate routes
3. reconstruct candidate route outputs
4. measure exact match length
5. compute token cost estimates
6. also include literal fallback candidate(s)

### 14.3 Matching rule

A route token is valid only if its emitted bits exactly match the source suffix for the emitted length.

### 14.4 Parsing algorithm

Version 1 must use dynamic programming.

Define `dp[i]` as the minimum estimated encoded cost from source bit position `i` to the end.

Required recurrence:

```text
dp[i] = min(cost(token) + dp[i + emitted_length(token)])
```

The encoder must recover the chosen token sequence.

### 14.5 Literal strategy

Version 1 must support fixed-size literal fallback blocks.

Configurable parameter:
- `literal_block_bits`, default 8 or 16

Optional later enhancement:
- variable-length literals

### 14.6 Cost model

Version 1 may use a simple fixed estimated bit cost model for parsing.

Example:
- route token cost estimated from field widths
- literal cost = token overhead + payload length

The code must isolate the cost model behind a replaceable abstraction so later entropy-based cost models can be added without rewriting encoder logic.

---

## 15. Decoder requirements

The decoder must:
1. load cube and metadata
2. parse encoded token stream
3. reconstruct the original bitstream exactly
4. write decoded output to disk

Exact reconstruction is mandatory.

---

## 16. CLI requirements

Implement a command-line interface with subcommands.

### Required commands

#### Train cube

```bash
python -m cube_codec.cli train \
  --config config.json \
  --input train_data.bin \
  --output-dir artifacts/
```

Outputs:
- cube artifacts
- metadata
- optional debug summaries

#### Encode file

```bash
python -m cube_codec.cli encode \
  --config config.json \
  --cube-dir artifacts/ \
  --input test_data.bin \
  --output encoded.bin
```

#### Decode file

```bash
python -m cube_codec.cli decode \
  --cube-dir artifacts/ \
  --input encoded.bin \
  --output decoded.bin
```

#### Benchmark

```bash
python -m cube_codec.cli benchmark \
  --config config.json \
  --train train_data.bin \
  --test test_data.bin \
  --output metrics.json
```

#### Inspect cube

```bash
python -m cube_codec.cli inspect-cube \
  --cube-dir artifacts/
```

This should print region summaries and cube metadata.

---

## 17. Configuration requirements

Implement a JSON or YAML configuration format.

Minimum supported fields:

```json
{
  "phrase_length": 64,
  "stride": 64,
  "min_frequency": 2,
  "max_regions": 64,
  "max_middle_variants": 8,
  "max_suffix_variants": 4,
  "prefix_index_bits": 16,
  "literal_block_bits": 8,
  "route_token_overhead_bits": 1,
  "literal_token_overhead_bits": 1,
  "debug": false
}
```

The configuration layer must validate values and fail clearly on invalid input.

---

## 18. Baseline implementations

Benchmark harness must compare prototype against:

### 18.1 Raw literal baseline
Encode full input as literals only.

### 18.2 Flat phrase dictionary baseline
Build a simple explicit dictionary of frequent fixed-length phrases and encode with explicit phrase identifiers plus literal fallback.

Purpose:
- determine whether the cube-based structure adds value beyond a flat dictionary

### 18.3 General-purpose codec baseline
Include at least one of:
- `zlib`
- `lzma`
- `zstandard` if available

Version 1 may use the Python standard library baseline first.

---

## 19. Benchmark harness requirements

The benchmark harness must:
- train or load a cube
- encode test data
- decode test data
- verify exact equality
- run baseline encoders
- produce metrics as JSON and readable console output

### Required benchmark datasets
- training corpus
- held-out validation or test corpus
- optional out-of-domain corpus if available

---

## 20. Metrics requirements

The system must report at minimum:

### Compression metrics
- original bits
- compressed bits
- compression ratio
- bits per source bit
- route token fraction
- literal token fraction

### Coverage metrics
- fraction of source bits covered by route tokens
- average route-emitted length
- number of unique routes used
- average routes per message

### Search metrics
- average candidate routes examined per source position
- encoder runtime
- decoder runtime
- index size

### Training and model metrics
- number of extracted phrases
- number of selected phrases
- number of clusters
- number of regions
- cube size in bits and bytes
- metadata size

### Quality metrics
- exact decode success/failure
- mismatch location on failure

---

## 21. Logging requirements

Support:
- verbose debug mode
- concise benchmark mode
- reproducible random seed for any stochastic steps

Debug logs should include:
- chosen route tokens
- literal fallbacks
- DP parse decisions
- cluster summaries
- cube region summaries

---

## 22. Correctness requirements

Automated tests must cover:

1. cube serialization round-trip
2. region reconstruction correctness
3. route token reconstruction correctness
4. literal token correctness
5. mixed token stream correctness
6. encoder-decoder round-trip on handcrafted examples
7. benchmark round-trip on larger samples
8. prefix index correctness
9. flat dictionary baseline correctness
10. CLI smoke tests if feasible

Any decode mismatch is a hard failure.

---

## 23. Test case requirements

CODEX 5.4 must generate both unit tests and integration tests.

### 23.1 Unit tests

#### Test: route reconstruction
- build one small region manually
- construct route token
- ensure route output equals expected bitstring

#### Test: literal round-trip
- encode literal token
- decode and verify exact bits

#### Test: cube serialization
- save and reload cube and metadata
- verify equality

#### Test: prefix index
- build index over a few routes
- verify correct candidate retrieval

### 23.2 Integration tests

#### Test: handcrafted corpus round-trip
- small training corpus with repeated designed phrases
- build cube automatically
- encode held-out message
- decode and verify exact equality

#### Test: flat dictionary baseline
- run baseline on same test corpus
- verify exact round-trip

#### Test: benchmark pipeline
- run full train/encode/decode/benchmark flow on a small corpus
- verify metrics file is created and contains required keys

---

## 24. Minimal handcrafted example requirement

Include a tiny, deterministic example corpus and test fixture that demonstrates the intended behavior.

Example concept:
- several 64-bit phrases sharing a 32-bit prefix
- a few middle variants
- a few suffix variants
- training should group them into at least one meaningful region

This fixture is required so the prototype has a known-good scenario in which route coding should clearly beat literals.

---

## 25. Acceptance criteria for milestone completion

### Milestone 1: deterministic toy route codec
Must support:
- hand-constructed cube
- manual route tokens
- exact decoding
- literal tokens

Acceptance:
- all unit tests pass
- handcrafted route example decodes correctly

### Milestone 2: automatic cube build from corpus
Must support:
- phrase extraction
- clustering
- region construction
- cube serialization

Acceptance:
- training pipeline runs end-to-end
- cube artifacts are loadable and valid

### Milestone 3: DP encoder
Must support:
- prefix index
- route candidate matching
- literal fallback
- optimal or near-optimal parse under fixed cost model

Acceptance:
- encode/decode round-trip passes on validation files

### Milestone 4: benchmarking and baselines
Must support:
- raw literal baseline
- flat phrase dictionary baseline
- one standard codec baseline
- metrics reporting

Acceptance:
- benchmark command produces reproducible metrics and exact decode verification

---

## 26. Coding requirements

Use clear, modular Python.

Requirements:
- type hints throughout
- docstrings on public functions/classes
- dataclasses where appropriate
- no hard-coded corpus-specific assumptions beyond configuration
- isolate parsing cost model behind an interface or helper module
- isolate serialization logic from core models

Optional but preferred:
- use `pytest`
- use `argparse` for CLI
- keep dependencies minimal

---

## 27. README requirements

CODEX 5.4 must generate a README containing:
- project overview
- conceptual explanation of route tokens and cube regions
- installation instructions
- CLI usage examples
- configuration explanation
- test instructions
- benchmark instructions
- limitations of v1

---

## 28. Documentation of limitations

The generated code and README must explicitly document:
- this is a proof-of-concept codec
- region geometry is simplified
- route semantics are structured and limited
- entropy coding is not yet implemented in v1
- performance on random data is expected to be poor
- domain-specific corpora are the intended target

---

## 29. Stretch goals if time permits

These are optional and should not block delivery of the required prototype.

1. variable-length literal blocks
2. binary-packed bitstream utilities for better efficiency
3. conditional cost model hooks for future entropy coding
4. continuation-token scaffold, disabled by default
5. simple cube visualization or region inspection utility

---

## 30. Final implementation objective

Deliver a working, testable, reproducible Python prototype that demonstrates the full experimental loop:

1. train cube from corpus
2. serialize cube
3. encode test data with route and literal tokens
4. decode exactly
5. benchmark against baselines
6. report metrics

The prototype must prioritize correctness, clarity, modularity, and experimental usefulness over raw performance.


---

# 26) Implementation guardrails and interpretation priorities

These requirements are updated to reflect the most important prototype execution principles.

## 26.1 Narrow prototype mandate
The implementation shall prioritize a narrow, interpretable proof-of-concept over breadth.

### Required constraint
Version 1 shall optimize for:
- exact lossless decode
- transparent tokenization behavior
- measurable route coverage
- manageable search cost
- clean comparison against a flat phrase dictionary baseline

### Explicit non-goals for version 1
The implementation shall **not** attempt to:
- beat modern production compressors on general data
- support multiple advanced path grammars at once
- optimize for maximum speed before correctness and observability are established
- introduce learned probabilistic models beyond simple configurable cost models
- broaden scope to arbitrary geometric traversal families

## 26.2 Fair baseline requirement
The benchmark suite shall include a flat explicit phrase dictionary baseline trained from the same training corpus and phrase extraction configuration as the cube-based codec.

### Baseline fairness requirements
The flat phrase dictionary baseline shall use:
- the same phrase length(s)
- the same training corpus
- the same train/validation/test split
- the same literal fallback policy where practical
- comparable token accounting rules where practical

### Interpretation requirement
If the cube-based codec fails to outperform the flat phrase dictionary baseline on the target in-domain corpus, this shall be treated as a significant negative result and clearly reported.

The benchmark report shall explicitly distinguish:
- cube codec vs raw literals
- cube codec vs flat phrase dictionary
- cube codec vs general-purpose compressor

The cube codec does **not** need to beat the general-purpose compressor in version 1 to be considered informative.

## 26.3 Instrumentation-first requirement
The implementation shall prioritize strong instrumentation from the first runnable version.

### Mandatory diagnostic metrics
In addition to aggregate compression ratio, the system shall report:
- route hit rate
- fraction of input bits covered by route tokens
- average profitable route length
- average route token cost
- average literal token cost
- average candidate routes examined per source position
- distribution of chosen token types
- fraction of phrases covered by one route vs literals
- top used regions and their utilization frequencies
- per-region coverage and savings contribution
- route match length histogram
- parse depth statistics
- benchmark wall-clock time for training, encoding, and decoding

### Failure-analysis requirement
If performance is weak, the metrics output shall make it possible to distinguish among at least these failure modes:
- poor phrase coverage
- route descriptors too expensive
- excessive search cost
- too many short unprofitable matches
- cube regions rarely used
- flat dictionary baseline capturing the same value more efficiently

## 26.4 Clarity, determinism, and observability priority
The generated software shall prioritize:
1. clarity
2. determinism
3. observability
4. extensibility
5. speed

### Code quality requirement
The implementation shall favor:
- readable module boundaries
- explicit data structures
- reproducible outputs
- clear debug logs
- testability of every major transformation stage

### Anti-cleverness requirement
Avoid opaque optimizations, compressed metaprogramming, or architecture choices that make experimental interpretation difficult.

## 26.5 Version 1 success definition
Version 1 shall be considered successful if it demonstrates all of the following on at least one narrow in-domain corpus:
- exact bit-for-bit reconstruction
- meaningful route usage rather than near-total literal fallback
- enough instrumentation to explain wins and losses
- manageable candidate search behavior
- measurable improvement over raw literals
- either a win over the flat phrase dictionary baseline in at least some conditions, or a clearly diagnosable reason why not

## 26.6 Reporting requirement
The benchmark runner shall produce a final summary report that includes:
- configuration used
- corpus split information
- cube size and metadata size
- baseline comparison table
- diagnostic metric table
- interpretation notes highlighting likely bottlenecks

The report may be emitted as markdown, JSON, or both, but markdown output is required.
