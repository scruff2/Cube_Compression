# ZIP-Class Competition Results (Phase 6 Snapshot)

Date: 2026-03-10
Target baseline: `zlib`

## Compression Results (Best Real Cube Mode)

| Corpus family | Best mode | Cube bits | zlib bits | lzma bits | Cube vs zlib |
|---|---|---:|---:|---:|---:|
| structured_synthetic | cube_family_local_id_actual | 304 | 1,904 | 2,400 | **-84.034%** |
| semi_structured_narrow | cube_fixed_length_actual | 57,800 | 57,920 | 54,880 | **-0.207%** |
| mixed_general | cube_fixed_length_actual | 31,792 | 31,800 | 31,264 | **-0.025%** |

## Throughput and Memory (Best Real Cube Mode)

| Corpus family | Encode MB/s | Decode MB/s | Peak memory (MB) |
|---|---:|---:|---:|
| structured_synthetic | 7.852 | 14.165 | 0.49 |
| semi_structured_narrow | 8.344 | 42.998 | 38.05 |
| mixed_general | 8.521 | 43.780 | 21.07 |

## Gate C Status

- structured_synthetic: clear pass vs zlib
- semi_structured_narrow: pass by small margin (`-120` bits vs zlib)
- mixed_general: pass by very small margin (`-8` bits vs zlib)
- significance note: wins are small and below the roadmap meaningful-margin criterion (>=5%).