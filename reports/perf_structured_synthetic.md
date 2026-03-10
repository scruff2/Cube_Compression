# Performance Baseline

- test_bits: 2560
- peak_memory_bytes: 508827
- base_encode_sec: 0.011245
- base_decode_sec: 0.000037

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 424 | 0.000056 | 0.000063 | 45.337 | 40.528 |
| cube_fixed_length_actual | 360 | 0.000268 | 0.000055 | 9.559 | 46.237 |
| cube_family_local_id_actual | 304 | 0.000365 | 0.000184 | 7.018 | 13.918 |
| cube_entropy_coded_actual | 920 | 0.000222 | 0.000054 | 11.525 | 47.001 |