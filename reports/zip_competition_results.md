# ZIP-Class Competition Results (Phase 6 Snapshot)

Date: 2026-03-10
Target baseline: `zlib`

## Test Description

Three locked corpus families were benchmarked with identical config class (`sample_config_scaling_variable.json`) and deterministic splits:

1. `structured_synthetic` (`v1_4_variable`)
2. `semi_structured_narrow` (`corpora/phase1/semi_structured_narrow`)
3. `mixed_general` (`corpora/phase1/mixed_general`)

For each family:
- train cube on train split
- encode test split with all real modes
- decode and verify exact equality
- compare best real cube mode against zlib and lzma
- measure runtime and memory using `perf` (3 repeats)

## Correctness Outcome

All evaluated runs had exact lossless decode success (`decode_success=true`).

## Compression Results (Best Real Cube Mode)

| Corpus family | Original bits | Best real cube bits | zlib bits | lzma bits | Cube vs zlib |
|---|---:|---:|---:|---:|---:|
| structured_synthetic | 2,560 | 304 | 1,904 | 2,400 | **-84.0% bits** |
| semi_structured_narrow | 204,504 | 78,408 | 57,920 | 54,880 | **+35.4% bits** |
| mixed_general | 112,744 | 42,832 | 31,800 | 31,264 | **+34.7% bits** |

Interpretation:
- Synthetic run still beats zlib strongly.
- Non-synthetic gaps narrowed substantially after framed token/literal compression.
- Still not beating zlib/lzma on semi-structured or mixed-general corpora.

## Throughput and Memory (Best Real Cube Mode)

| Corpus family | Encode MB/s | Decode MB/s | Peak memory (MB) |
|---|---:|---:|---:|
| structured_synthetic | 10.248 | 14.081 | 0.49 |
| semi_structured_narrow | 11.720 | 11.082 | 38.05 |
| mixed_general | 10.479 | 9.659 | 21.07 |

## Gate C Decision (ZIP-class positioning)

- Snapshot status: improved but still fail.
- Keep iterating toward real-corpus wins before ZIP-competitive claim.