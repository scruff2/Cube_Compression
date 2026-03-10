# Performance Baseline

- test_bits: 204504
- peak_memory_bytes: 39903139
- base_encode_sec: 7.849234
- base_decode_sec: 0.004727

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 280752 | 0.023518 | 0.029978 | 8.696 | 6.822 |
| cube_fixed_length_actual | 271312 | 0.020759 | 0.022485 | 9.852 | 9.095 |
| cube_family_local_id_actual | 261464 | 0.019607 | 0.021625 | 10.430 | 9.457 |
| cube_entropy_coded_actual | 281184 | 0.019519 | 0.025233 | 10.477 | 8.105 |