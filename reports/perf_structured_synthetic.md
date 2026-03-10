# Performance Baseline

- test_bits: 2560
- peak_memory_bytes: 508827
- base_encode_sec: 0.013771
- base_decode_sec: 0.000038

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 424 | 0.000055 | 0.000062 | 46.377 | 41.180 |
| cube_fixed_length_actual | 376 | 0.000209 | 0.000058 | 12.239 | 44.316 |
| cube_family_local_id_actual | 320 | 0.000306 | 0.000179 | 8.360 | 14.318 |
| cube_entropy_coded_actual | 936 | 0.000169 | 0.000056 | 15.109 | 45.878 |