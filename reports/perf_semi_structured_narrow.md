# Performance Baseline

- test_bits: 204504
- peak_memory_bytes: 39903139
- base_encode_sec: 6.577823
- base_decode_sec: 0.003296

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 280752 | 0.014495 | 0.018409 | 14.109 | 11.109 |
| cube_fixed_length_actual | 82640 | 0.015109 | 0.017555 | 13.535 | 11.650 |
| cube_family_local_id_actual | 78408 | 0.017450 | 0.018454 | 11.720 | 11.082 |
| cube_entropy_coded_actual | 100464 | 0.015555 | 0.019409 | 13.147 | 10.537 |