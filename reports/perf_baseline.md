# Performance Baseline

- test_bits: 2560
- peak_memory_bytes: 508827
- base_encode_sec: 0.012437
- base_decode_sec: 0.000055

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 424 | 0.000055 | 0.000064 | 46.972 | 39.752 |
| cube_fixed_length_actual | 296 | 0.000047 | 0.000047 | 55.014 | 54.237 |
| cube_family_local_id_actual | 240 | 0.000208 | 0.000204 | 12.310 | 12.572 |
| cube_entropy_coded_actual | 856 | 0.000067 | 0.000052 | 38.057 | 49.676 |