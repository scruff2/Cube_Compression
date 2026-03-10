# Performance Baseline (Multi-Corpus)

| corpus | test_bits | best_mode | bits | encode_mbps | decode_mbps | peak_memory_mb |
|---|---:|---|---:|---:|---:|---:|
| structured_synthetic | 2560 | cube_family_local_id_actual | 320 | 8.360 | 14.318 | 0.49 |
| semi_structured_narrow | 204504 | cube_fixed_length_actual | 57872 | 6.767 | 41.839 | 38.05 |
| mixed_general | 112744 | cube_fixed_length_actual | 31864 | 6.371 | 34.808 | 21.07 |