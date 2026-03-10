# Cube Route Codec Benchmark Report

## Configuration Used
- phrase_length: 256
- stride: 32

## Cube Descriptor Idealization Table
| Mode | Total Bits | Bits/Source Bit | Compression Ratio | Avg Bits/Route | Delta vs cube_actual | Delta vs family_aware |
|---|---:|---:|---:|---:|---:|---:|
| cube_actual | 322.00 | 0.1258 | 7.9503 | 23.0000 | 0.00 | 140.00 |
| cube_fixed_length_optimized | 196.00 | 0.0766 | 13.0612 | 14.0000 | -126.00 | 14.00 |
| cube_entropy_estimated.whole_route | 63.30 | 0.0247 | 40.4404 | 4.5216 | -258.70 | -118.70 |
| cube_entropy_estimated.factorized | 63.30 | 0.0247 | 40.4404 | 4.5216 | -258.70 | -118.70 |
| cube_family_local_id | 70.00 | 0.0273 | 36.5714 | 5.0000 | -252.00 | -112.00 |
| cube_oracle_used_route | 63.30 | 0.0247 | 40.4404 | 4.5216 | -258.70 | -118.70 |
| cube_oracle_region_local | 63.30 | 0.0247 | 40.4404 | 4.5216 | -258.70 | -118.70 |
| cube_oracle_factorized | 63.30 | 0.0247 | 40.4404 | 4.5216 | -258.70 | -118.70 |

## Long-Phrase Regime Summary
- fixed 128 results: available
- fixed 256 results: available
- variable-length results: available

## Longer-Segment Utilization
- average emitted length: 182.86
- max emitted length: 256
- route coverage by length class: {'192': 384, '256': 1792, '64': 256, '128': 128}

## Scaling Summary
- scaling_train_bits: 10240
- scaling_cube_payload_bits: 41152
- scaling_region_count: 269

## Real Descriptor-Coding Modes
- cube_actual_legacy: bits=424, ratio=6.0377, decode_success=True
- cube_fixed_length_actual: bits=296, ratio=8.6486, decode_success=True
- cube_family_local_id_actual: bits=240, ratio=10.6667, decode_success=True
- cube_entropy_coded_actual: bits=856, ratio=2.9907, decode_success=True

## Comparative Baseline Table
| Mode | Bits | Ratio |
|---|---:|---:|
| cube_best_real (cube_family_local_id_actual) | 240.0 | 10.6667 |
| family_aware | 182 | 14.0659 |
| flat_dictionary | 140 | 18.2857 |
| zlib | 1904 | 1.3445 |

## Baseline Comparison
- raw_literals ratio: 0.8889
- flat_dictionary ratio: 18.2857
- family_aware ratio: 14.0659
- phrase_family_oracle ratio: 15.2381

## Decision
- target baseline: zlib (1904.0 bits)
- cube_fixed_length_actual beats target: True
- cube_family_local_id_actual beats target: True
- cube_entropy_coded_actual beats target: True
- best real cube mode: cube_family_local_id_actual
- best_real_cube_minus_target_bits: -1664.0
- descriptor_redesign_verdict: descriptor_redesign_fails
- beats family-aware in any mode: True
- best cube mode: cube_entropy_estimated.whole_route
- final verdict: geometry_promising
- long_phrase_any_real_cube_beats_family_aware: False
- long_phrase_best_length_class: 256
- long_phrase_verdict: long_phrases_marginal
- scaling_any_real_cube_beats_target: True
- scaling_verdict: scaling_promising

## Recommendation
- continue cube investigation
- cube only worth pursuing if descriptor redesign is implemented
- continue cube investigation