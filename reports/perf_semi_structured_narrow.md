# Performance Baseline

- test_bits: 204504
- peak_memory_bytes: 39903139
- base_encode_sec: 7.835575
- base_decode_sec: 0.004517

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 280752 | 0.024353 | 0.028791 | 8.397 | 7.103 |
| cube_fixed_length_actual | 57872 | 0.030223 | 0.004888 | 6.767 | 41.839 |
| cube_family_local_id_actual | 57872 | 0.032711 | 0.004544 | 6.252 | 45.008 |
| cube_entropy_coded_actual | 57872 | 0.027286 | 0.004415 | 7.495 | 46.323 |