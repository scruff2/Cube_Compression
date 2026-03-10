# Cube Route Codec Benchmark Report

## Configuration Used
- phrase_length: 128
- stride: 32

## Cube Descriptor Idealization Table
| Mode | Total Bits | Bits/Source Bit | Compression Ratio | Avg Bits/Route | Delta vs cube_actual | Delta vs family_aware |
|---|---:|---:|---:|---:|---:|---:|
| cube_actual | 376.00 | 0.1836 | 5.4468 | 19.0000 | 0.00 | 67.00 |
| cube_fixed_length_optimized | 248.00 | 0.1211 | 8.2581 | 11.0000 | -128.00 | -61.00 |
| cube_entropy_estimated.whole_route | 136.00 | 0.0664 | 15.0588 | 4.0000 | -240.00 | -173.00 |
| cube_entropy_estimated.factorized | 136.00 | 0.0664 | 15.0588 | 4.0000 | -240.00 | -173.00 |
| cube_family_local_id | 149.00 | 0.0728 | 13.7450 | 4.8125 | -227.00 | -160.00 |
| cube_oracle_used_route | 136.00 | 0.0664 | 15.0588 | 4.0000 | -240.00 | -173.00 |
| cube_oracle_region_local | 136.00 | 0.0664 | 15.0588 | 4.0000 | -240.00 | -173.00 |
| cube_oracle_factorized | 136.00 | 0.0664 | 15.0588 | 4.0000 | -240.00 | -173.00 |

## Long-Phrase Regime Summary
- fixed 128 results: available
- fixed 256 results: not primary in this run
- variable-length results: not primary in this run

## Longer-Segment Utilization
- average emitted length: 128.00
- max emitted length: 128
- route coverage by length class: {'128': 2048}

## Scaling Summary
- scaling_train_bits: 8192
- scaling_cube_payload_bits: 6432
- scaling_region_count: 42

## Real Descriptor-Coding Modes
- cube_actual_legacy: bits=552, ratio=3.7101, decode_success=True
- cube_fixed_length_actual: bits=488, ratio=4.1967, decode_success=True
- cube_family_local_id_actual: bits=488, ratio=4.1967, decode_success=True
- cube_entropy_coded_actual: bits=848, ratio=2.4151, decode_success=True

## Comparative Baseline Table
| Mode | Bits | Ratio |
|---|---:|---:|
| cube_best_real (cube_fixed_length_actual) | 488.0 | 4.1967 |
| family_aware | 309 | 6.6278 |
| flat_dictionary | 249 | 8.2249 |
| zlib | 1072 | 1.9104 |

## Baseline Comparison
- raw_literals ratio: 0.8889
- flat_dictionary ratio: 8.2249
- family_aware ratio: 6.6278
- phrase_family_oracle ratio: 13.6533

## Decision
- target baseline: zlib (1072.0 bits)
- cube_fixed_length_actual beats target: True
- cube_family_local_id_actual beats target: True
- cube_entropy_coded_actual beats target: True
- best real cube mode: cube_fixed_length_actual
- best_real_cube_minus_target_bits: -584.0
- descriptor_redesign_verdict: descriptor_redesign_fails
- beats family-aware in any mode: True
- best cube mode: cube_entropy_estimated.whole_route
- final verdict: geometry_promising
- long_phrase_any_real_cube_beats_family_aware: False
- long_phrase_best_length_class: 128
- long_phrase_verdict: long_phrases_marginal
- scaling_any_real_cube_beats_target: True
- scaling_verdict: scaling_promising

## Recommendation
- continue cube investigation
- cube only worth pursuing if descriptor redesign is implemented
- continue cube investigation