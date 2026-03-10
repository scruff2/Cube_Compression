# Performance Baseline

- test_bits: 2560
- peak_memory_bytes: 508827
- base_encode_sec: 0.011293
- base_decode_sec: 0.000035

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 424 | 0.000055 | 0.000064 | 46.237 | 40.083 |
| cube_fixed_length_actual | 360 | 0.000050 | 0.000050 | 51.509 | 50.996 |
| cube_family_local_id_actual | 304 | 0.000211 | 0.000179 | 12.162 | 14.312 |
| cube_entropy_coded_actual | 920 | 0.000068 | 0.000051 | 37.740 | 49.935 |