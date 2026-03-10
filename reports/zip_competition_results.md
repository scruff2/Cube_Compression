# ZIP-Class Competition Results (Chunk-Hybrid Snapshot)

Date: 2026-03-10
Target baseline: `zlib`

| Corpus | Best mode | Cube bits | zlib bits | lzma bits | Cube vs zlib |
|---|---|---:|---:|---:|---:|
| structured_synthetic | cube_family_local_id_actual | 320 | 1,904 | 2,400 | **-83.193%** |
| semi_structured_narrow | cube_fixed_length_actual | 57,872 | 57,920 | 54,880 | **-0.083%** |
| mixed_general | cube_fixed_length_actual | 31,864 | 31,800 | 31,264 | **+0.201%** |

Notes:
- CCM3 chunk-hybrid container enabled with per-chunk route vs literal-only choice.
- Current chunk target keeps context stable; wins are small and close to parity.
- Significant-margin criterion (>=5%) is still not met.