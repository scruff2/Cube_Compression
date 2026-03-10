# Performance Baseline

- test_bits: 112744
- peak_memory_bytes: 22098236
- base_encode_sec: 28.850675
- base_decode_sec: 0.002810

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 135552 | 0.008552 | 0.013128 | 13.183 | 8.588 |
| cube_fixed_length_actual | 31864 | 0.017696 | 0.003239 | 6.371 | 34.808 |
| cube_family_local_id_actual | 31864 | 0.019993 | 0.003876 | 5.639 | 29.085 |
| cube_entropy_coded_actual | 31864 | 0.017920 | 0.002503 | 6.291 | 45.043 |