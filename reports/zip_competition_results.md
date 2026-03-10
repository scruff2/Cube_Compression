# ZIP-Class Competition Results (Phase 6 Snapshot)

Date: 2026-03-10
Target baseline: `zlib`

## Compression Results (Best Real Cube Mode)

| Corpus family | Best mode | Cube bits | zlib bits | lzma bits | Cube vs zlib |
|---|---|---:|---:|---:|---:|
| structured_synthetic | cube_family_local_id_actual | 304 | 1,904 | 2,400 | **-84.03%** |
| semi_structured_narrow | cube_fixed_length_actual | 58,064 | 57,920 | 54,880 | **+0.25%** |
| mixed_general | cube_fixed_length_actual | 31,944 | 31,800 | 31,264 | **+0.45%** |

## Throughput and Memory (Best Real Cube Mode)

| Corpus family | Encode MB/s | Decode MB/s | Peak memory (MB) |
|---|---:|---:|---:|
| structured_synthetic | 7.018 | 13.918 | 0.49 |
| semi_structured_narrow | 9.954 | 48.097 | 38.05 |
| mixed_general | 11.174 | 51.116 | 21.07 |

## Gate C Status

- structured_synthetic: pass vs zlib
- semi_structured_narrow: near-parity (still +0.25% bits vs zlib)
- mixed_general: near-parity (still +0.45% bits vs zlib)
- overall: not yet a strict ZIP-competitive pass, but gap is now marginal on two real corpora.