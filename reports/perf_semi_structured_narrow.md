# Performance Baseline

- test_bits: 204504
- peak_memory_bytes: 39903139
- base_encode_sec: 6.573864
- base_decode_sec: 0.003098

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 280752 | 0.014590 | 0.018131 | 14.016 | 11.279 |
| cube_fixed_length_actual | 58064 | 0.020545 | 0.004252 | 9.954 | 48.097 |
| cube_family_local_id_actual | 58064 | 0.022117 | 0.003933 | 9.247 | 51.995 |
| cube_entropy_coded_actual | 58064 | 0.020050 | 0.003907 | 10.200 | 52.344 |