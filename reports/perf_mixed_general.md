# Performance Baseline

- test_bits: 112744
- peak_memory_bytes: 22098236
- base_encode_sec: 21.414514
- base_decode_sec: 0.001981

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 135552 | 0.006856 | 0.008092 | 16.444 | 13.932 |
| cube_fixed_length_actual | 130136 | 0.006643 | 0.008041 | 16.972 | 14.022 |
| cube_family_local_id_actual | 125160 | 0.011132 | 0.012249 | 10.128 | 9.204 |
| cube_entropy_coded_actual | 137056 | 0.006745 | 0.008911 | 16.714 | 12.652 |