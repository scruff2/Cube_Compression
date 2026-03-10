# Performance Baseline (Multi-Corpus)

| corpus | test_bits | best_mode | bits | encode_mbps | decode_mbps | peak_memory_mb |
|---|---:|---|---:|---:|---:|---:|
| structured_synthetic | 2560 | cube_family_local_id_actual | 304 | 7.018 | 13.918 | 0.49 |
| semi_structured_narrow | 204504 | cube_fixed_length_actual | 58064 | 9.954 | 48.097 | 38.05 |
| mixed_general | 112744 | cube_fixed_length_actual | 31944 | 11.174 | 51.116 | 21.07 |