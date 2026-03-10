# Cube Route Codec Benchmark Report

## Configuration Used
- phrase_length: 256
- stride: 32

## Cube Descriptor Idealization Table
| Mode | Total Bits | Bits/Source Bit | Compression Ratio | Avg Bits/Route | Delta vs cube_actual | Delta vs target_baseline |
|---|---:|---:|---:|---:|---:|---:|
| cube_actual | 83004.00 | 0.7362 | 1.3583 | 32.0000 | 0.00 | 51204.00 |
| cube_fixed_length_optimized | 76479.00 | 0.6783 | 1.4742 | 23.0000 | -6525.00 | 44679.00 |
| cube_entropy_estimated.whole_route | 65965.88 | 0.5851 | 1.7091 | 8.4991 | -17038.12 | 34165.88 |
| cube_entropy_estimated.factorized | 65965.88 | 0.5851 | 1.7091 | 8.4991 | -17038.12 | 34165.88 |
| cube_family_local_id | 66846.00 | 0.5929 | 1.6866 | 9.7131 | -16158.00 | 35046.00 |
| cube_oracle_used_route | 65965.88 | 0.5851 | 1.7091 | 8.4991 | -17038.12 | 34165.88 |
| cube_oracle_region_local | 65965.88 | 0.5851 | 1.7091 | 8.4991 | -17038.12 | 34165.88 |
| cube_oracle_factorized | 65965.88 | 0.5851 | 1.7091 | 8.4991 | -17038.12 | 34165.88 |

## Long-Phrase Regime Summary
- fixed 128 results: available
- fixed 256 results: available
- variable-length results: available

## Longer-Segment Utilization
- average emitted length: 86.07
- max emitted length: 256
- route coverage by length class: {'256': 5120, '64': 36160, '192': 9600, '128': 11520}

## Scaling Summary
- scaling_train_bits: 640200
- scaling_cube_payload_bits: 678944
- scaling_region_count: 3940

## Real Descriptor-Coding Modes
- cube_actual_legacy: bits=135552, ratio=0.8317, decode_success=True
- cube_fixed_length_actual: bits=31792, ratio=3.5463, decode_success=True
- cube_family_local_id_actual: bits=31792, ratio=3.5463, decode_success=True
- cube_entropy_coded_actual: bits=31792, ratio=3.5463, decode_success=True

## Comparative Baseline Table
| Mode | Bits | Ratio |
|---|---:|---:|
| cube_best_real (cube_fixed_length_actual) | 31792.0 | 3.5463 |
| family_aware | 84044 | 1.3415 |
| flat_dictionary | 68263 | 1.6516 |
| zlib | 31800 | 3.5454 |

## Baseline Comparison
- raw_literals ratio: 0.8889
- flat_dictionary ratio: 1.6516
- family_aware ratio: 1.3415
- phrase_family_oracle ratio: 5.9389

## Decision
- target baseline: zlib (31800.0 bits)
- cube_fixed_length_actual beats target: True
- cube_family_local_id_actual beats target: True
- cube_entropy_coded_actual beats target: True
- best real cube mode: cube_fixed_length_actual
- best_real_cube_minus_target_bits: -8.0
- descriptor_redesign_verdict: descriptor_redesign_succeeds
- any_real_cube_beats_target: True
- best cube mode: cube_entropy_estimated.whole_route
- final verdict: geometry_promising
- long_phrase_best_length_class: 64
- long_phrase_verdict: long_phrases_promising
- scaling_any_real_cube_beats_target: True
- scaling_verdict: scaling_promising

## Recommendation
- continue cube investigation
- continue cube investigation
- continue cube investigation