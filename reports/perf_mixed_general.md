# Performance Baseline

- test_bits: 112744
- peak_memory_bytes: 22098236
- base_encode_sec: 21.469665
- base_decode_sec: 0.002040

| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |
|---|---:|---:|---:|---:|---:|
| cube_actual_legacy | 135552 | 0.006957 | 0.007818 | 16.205 | 14.420 |
| cube_fixed_length_actual | 31944 | 0.010090 | 0.002206 | 11.174 | 51.116 |
| cube_family_local_id_actual | 31944 | 0.013206 | 0.002226 | 8.537 | 50.658 |
| cube_entropy_coded_actual | 31944 | 0.009802 | 0.002308 | 11.503 | 48.845 |