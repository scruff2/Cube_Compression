# Performance Baseline

- test_bits: 112744
- peak_memory_bytes: 22098236
- base_encode_sec: 27.945229
- base_decode_sec: 0.002618

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 135552 | 0.008313 | 0.009562 | 13.562 | 11.791 |
| cube_fixed_length_actual | 31792 | 0.013232 | 0.002575 | 8.521 | 43.780 |
| cube_family_local_id_actual | 31792 | 0.016930 | 0.003325 | 6.659 | 33.909 |
| cube_entropy_coded_actual | 31792 | 0.011216 | 0.002717 | 10.052 | 41.489 |