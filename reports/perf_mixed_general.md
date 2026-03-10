# Performance Baseline

- test_bits: 112744
- peak_memory_bytes: 22098236
- base_encode_sec: 28.786388
- base_decode_sec: 0.002406

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 135552 | 0.012547 | 0.012874 | 8.985 | 8.758 |
| cube_fixed_length_actual | 130136 | 0.010183 | 0.009723 | 11.072 | 11.596 |
| cube_family_local_id_actual | 125160 | 0.015608 | 0.015330 | 7.223 | 7.354 |
| cube_entropy_coded_actual | 137056 | 0.009043 | 0.011813 | 12.468 | 9.544 |