# Performance Baseline

- test_bits: 112744
- peak_memory_bytes: 22098236
- base_encode_sec: 21.388055
- base_decode_sec: 0.002051

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 135552 | 0.006767 | 0.007778 | 16.662 | 14.496 |
| cube_fixed_length_actual | 99928 | 0.008355 | 0.008887 | 13.494 | 12.686 |
| cube_family_local_id_actual | 94952 | 0.010598 | 0.011825 | 10.638 | 9.534 |
| cube_entropy_coded_actual | 106848 | 0.007126 | 0.009222 | 15.821 | 12.226 |