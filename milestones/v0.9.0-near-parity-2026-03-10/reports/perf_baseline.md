# Performance Baseline (Multi-Corpus)

| corpus | test_bits | best_mode | bits | encode_mbps | decode_mbps | peak_memory_mb |
|---|---:|---|---:|---:|---:|---:|
| structured_synthetic | 2560 | cube_family_local_id_actual | 304 | 7.852 | 14.165 | 0.49 |
| semi_structured_narrow | 204504 | cube_fixed_length_actual | 57800 | 8.344 | 42.998 | 38.05 |
| mixed_general | 112744 | cube_fixed_length_actual | 31792 | 8.521 | 43.780 | 21.07 |