# Performance Baseline

- test_bits: 2560
- peak_memory_bytes: 508827
- base_encode_sec: 0.011845
- base_decode_sec: 0.000038

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 424 | 0.000051 | 0.000059 | 50.633 | 43.083 |
| cube_fixed_length_actual | 296 | 0.000046 | 0.000047 | 55.555 | 53.917 |
| cube_family_local_id_actual | 240 | 0.000204 | 0.000172 | 12.564 | 14.903 |
| cube_entropy_coded_actual | 856 | 0.000057 | 0.000049 | 45.214 | 51.864 |