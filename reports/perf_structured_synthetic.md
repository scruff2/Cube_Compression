# Performance Baseline

- test_bits: 2560
- peak_memory_bytes: 508827
- base_encode_sec: 0.011197
- base_decode_sec: 0.000042

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 424 | 0.000048 | 0.000071 | 52.849 | 35.965 |
| cube_fixed_length_actual | 296 | 0.000085 | 0.000086 | 29.970 | 29.740 |
| cube_family_local_id_actual | 240 | 0.000262 | 0.000217 | 9.755 | 11.814 |
| cube_entropy_coded_actual | 856 | 0.000059 | 0.000047 | 43.537 | 54.100 |