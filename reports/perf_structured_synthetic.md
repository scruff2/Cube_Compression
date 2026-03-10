# Performance Baseline

- test_bits: 2560
- peak_memory_bytes: 508827
- base_encode_sec: 0.011290
- base_decode_sec: 0.000036

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 424 | 0.000055 | 0.000064 | 46.630 | 39.772 |
| cube_fixed_length_actual | 360 | 0.000172 | 0.000055 | 14.866 | 46.517 |
| cube_family_local_id_actual | 304 | 0.000326 | 0.000181 | 7.852 | 14.165 |
| cube_entropy_coded_actual | 920 | 0.000175 | 0.000056 | 14.651 | 45.878 |