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
- measure runtime and memory using `perf` (5 repeats)

## Correctness Outcome

All evaluated runs had exact lossless decode success (`decode_success=true`).

Why successful:
- stream codecs reject malformed mode/magic paths and preserve deterministic headers
- decode path reconstructs original bit length exactly from stored metadata

## Compression Results (Best Real Cube Mode)

| Corpus family | Original bits | Best real cube bits | zlib bits | lzma bits | Cube vs zlib |
|---|---:|---:|---:|---:|---:|
| structured_synthetic | 2,560 | 240 | 1,904 | 2,400 | **-87.4% bits** |
| semi_structured_narrow | 204,504 | 261,464 | 57,920 | 54,880 | **+351.4% bits** |
| mixed_general | 112,744 | 125,160 | 31,800 | 31,264 | **+293.6% bits** |

Interpretation:
- Success only on the synthetic niche.
- Failure on both broader non-synthetic corpora.

## Throughput and Memory (Best Real Cube Mode)

| Corpus family | Encode MB/s | Decode MB/s | Peak memory (MB) |
|---|---:|---:|---:|
| structured_synthetic | 12.564 | 14.903 | 0.49 |
| semi_structured_narrow | 10.804 | 9.221 | 38.05 |
| mixed_general | 10.128 | 9.204 | 21.07 |

## Charts

```mermaid
xychart-beta
    title "Best Real Mode Bits vs zlib (Lower is Better)"
    x-axis [synthetic, semi_structured, mixed_general]
    y-axis "bits" 0 --> 280000
    bar [240, 261464, 125160]
    bar [1904, 57920, 31800]
```

```mermaid
xychart-beta
    title "Best Real Mode Compression Ratio vs zlib (Higher is Better)"
    x-axis [synthetic, semi_structured, mixed_general]
    y-axis "ratio" 0 --> 12
    line [10.6667, 0.7821, 0.9008]
    line [1.3445, 3.5308, 3.5454]
```

```mermaid
xychart-beta
    title "Best Real Mode Throughput by Corpus"
    x-axis [synthetic, semi_structured, mixed_general]
    y-axis "MB/s" 0 --> 20
    bar [12.564, 10.804, 10.128]
    bar [14.903, 9.221, 9.204]
```

## Gate C Decision (ZIP-class positioning)

Roadmap Gate C criterion:
- beat zlib by meaningful margin on at least one meaningful data niche while staying practical on speed/memory.

Current result:
- Synthetic-only win exists, but general and semi-structured corpora are far behind zlib/lzma.
- Therefore this snapshot does **not** support ZIP-competitive positioning.

## Recommendation

- Do not market as ZIP competitor yet.
- Treat current cube method as a structured-data research codec with a narrow synthetic win.
- Next technical focus should be route-descriptor overhead collapse on non-synthetic corpora before any new ZIP claims.