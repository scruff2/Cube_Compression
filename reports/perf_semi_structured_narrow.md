# Performance Baseline

- test_bits: 204504
- peak_memory_bytes: 39903139
- base_encode_sec: 6.556859
- base_decode_sec: 0.003187

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 280752 | 0.015235 | 0.018060 | 13.423 | 11.324 |
| cube_fixed_length_actual | 271312 | 0.016002 | 0.016566 | 12.780 | 12.345 |
| cube_family_local_id_actual | 261464 | 0.018928 | 0.022178 | 10.804 | 9.221 |
| cube_entropy_coded_actual | 281184 | 0.014895 | 0.020089 | 13.730 | 10.180 |