# Performance Baseline

- test_bits: 204504
- peak_memory_bytes: 39903139
- base_encode_sec: 7.549132
- base_decode_sec: 0.003783

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 280752 | 0.019285 | 0.019419 | 10.604 | 10.531 |
| cube_fixed_length_actual | 57800 | 0.024510 | 0.004756 | 8.344 | 42.998 |
| cube_family_local_id_actual | 57800 | 0.029386 | 0.004766 | 6.959 | 42.909 |
| cube_entropy_coded_actual | 57800 | 0.024507 | 0.004558 | 8.345 | 44.864 |