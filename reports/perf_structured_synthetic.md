# Performance Baseline

- test_bits: 2560
- peak_memory_bytes: 508827
- base_encode_sec: 0.011656
- base_decode_sec: 0.000037

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 424 | 0.000057 | 0.000064 | 44.651 | 39.917 |
| cube_fixed_length_actual | 360 | 0.000078 | 0.000054 | 32.625 | 47.731 |
| cube_family_local_id_actual | 304 | 0.000250 | 0.000182 | 10.248 | 14.081 |
| cube_entropy_coded_actual | 920 | 0.000076 | 0.000052 | 33.493 | 48.793 |