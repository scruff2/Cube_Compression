# Performance Baseline

- test_bits: 204504
- peak_memory_bytes: 39903139
- base_encode_sec: 6.603780
- base_decode_sec: 0.003276

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 280752 | 0.014901 | 0.017458 | 13.724 | 11.714 |
| cube_fixed_length_actual | 200416 | 0.015914 | 0.017622 | 12.850 | 11.605 |
| cube_family_local_id_actual | 190568 | 0.017056 | 0.018195 | 11.990 | 11.239 |
| cube_entropy_coded_actual | 210288 | 0.015685 | 0.019207 | 13.038 | 10.647 |