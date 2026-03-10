# Performance Baseline

- test_bits: 112744
- peak_memory_bytes: 22098236
- base_encode_sec: 21.332026
- base_decode_sec: 0.002156

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 135552 | 0.007094 | 0.007796 | 15.892 | 14.461 |
| cube_fixed_length_actual | 45336 | 0.007477 | 0.007937 | 15.078 | 14.205 |
| cube_family_local_id_actual | 42832 | 0.010759 | 0.011672 | 10.479 | 9.659 |
| cube_entropy_coded_actual | 56648 | 0.007384 | 0.009565 | 15.269 | 11.787 |