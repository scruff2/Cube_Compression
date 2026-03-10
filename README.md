# Cube Compression (Route-Descriptor Codec)

This repository contains a deterministic Python prototype for testing whether a shared cube-style structured codebook can compress phrase-family data competitively.

## Mathematical Approach

### 1) Region/Route model

A region represents a phrase family:

- `prefix` (shared trunk)
- `middle` variant id
- `suffix` variant id

Route reconstruction:

\[
\hat{x} = P_r \oplus M_{r,m} \oplus S_{r,m,s}
\]

where `r` is region id, `m` is middle id, `s` is suffix id.

### 2) Encoding objective (DP parsing)

For bitstream `x[0:n]`, minimize estimated coded size:

\[
DP[i] = \min_{t \in \mathcal{T}(i)} \left(C(t) + DP[i + \ell(t)]\right)
\]

- `t` is a candidate token at position `i`
- `C(t)` is token cost estimate
- `\ell(t)` is emitted length

Candidates come from prefix index route lookup + literal fallback.

### 3) Prefix-index candidate search

For key length `k`, index:

\[
\pi = x[i:i+k] \rightarrow \{(r,m,s)\}
\]

Each candidate route is reconstructed and exact-match checked.

### 4) Descriptor analysis modes

The benchmark computes both measured and idealized descriptor costs:

- actual fixed-field route coding
- fixed-length optimized (omit unnecessary length field)
- entropy-estimated whole-route and factorized descriptors
- family-local id model
- oracle variants

Core entropy terms:

\[
H(R),\quad H(Region) + H(Middle\mid Region) + H(Suffix\mid Region,Middle)
\]

### 5) Real stream modes

Implemented binary stream modes:

- `cube_actual_legacy`
- `cube_fixed_length_actual`
- `cube_family_local_id_actual`
- `cube_entropy_coded_actual` (static whole-route Huffman)

All modes include exact decode support.

### 6) Long-phrase and scaling regimes

Supports:

- fixed 128-bit
- fixed 256-bit
- variable `[64,128,192,256]`

Scaling controls include training-byte caps, region/variant caps, phrase caps, and overlap-aware stride.

## CLI

Train:

```bash
python -m cube_codec.cli train --config sample_config_scaling_fixed_128.json --input train.bin --output-dir artifacts
```

Encode (choose mode):

```bash
python -m cube_codec.cli encode --config sample_config_scaling_fixed_128.json --cube-dir artifacts --input test.bin --output out.bin --mode cube_family_local_id_actual
```

Decode:

```bash
python -m cube_codec.cli decode --cube-dir artifacts --input out.bin --output decoded.bin
```

Benchmark:

```bash
python -m cube_codec.cli benchmark --config sample_config_scaling_variable.json --train train.bin --test test.bin --output metrics.json
```

Matrix:

```bash
python -m cube_codec.cli benchmark-matrix --config sample_config_scaling_variable.json --train train.bin --test test.bin --sweep sweep_v1_5.json --output-dir v1_5_matrix
```

## Test Results

### Unit/integration tests

- Command: `pytest -q`
- Result: `21 passed`

### Latest v1.5 scaling benchmark snapshot

From `v1_5_metrics.json`:

- `scaling_best_real_cube_mode`: `cube_family_local_id_actual`
- `scaling_best_real_cube_bits`: `248`
- `family_aware_bits`: `196`
- `scaling_average_route_emitted_bits`: `182.8571`
- `scaling_cube_payload_bits`: `41152`
- `scaling_verdict`: `scaling_not_helping`

Interpretation: scaling increased route span substantially, but in this run the best real cube stream still did not beat family-aware.

## Repository Contents

- `cube_codec/`: implementation
- `cube_codec/tests/`: automated tests
- sample configs:
  - `sample_config_scaling_fixed_128.json`
  - `sample_config_scaling_variable.json`

## Notes

- This project is an experimental codec prototype, not a production compressor.
- Emphasis is on deterministic diagnostics and fair baseline comparisons.
