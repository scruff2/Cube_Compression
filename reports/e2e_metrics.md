# Cube Route Codec Benchmark Report

## Configuration Used
- phrase_length: 64
- stride: 64

## Cube Descriptor Idealization Table
| Mode | Total Bits | Bits/Source Bit | Compression Ratio | Avg Bits/Route | Delta vs cube_actual | Delta vs target_baseline |
|---|---:|---:|---:|---:|---:|---:|
| cube_actual | 252.00 | 0.1875 | 5.3333 | 12.0000 | 0.00 | 4.00 |
| cube_fixed_length_optimized | 105.00 | 0.0781 | 12.8000 | 5.0000 | -147.00 | -143.00 |
| cube_entropy_estimated.whole_route | 54.28 | 0.0404 | 24.7586 | 2.5850 | -197.72 | -193.72 |
| cube_entropy_estimated.factorized | 54.28 | 0.0404 | 24.7586 | 2.5850 | -197.72 | -193.72 |
| cube_family_local_id | 63.00 | 0.0469 | 21.3333 | 3.0000 | -189.00 | -185.00 |
| cube_oracle_used_route | 54.28 | 0.0404 | 24.7586 | 2.5850 | -197.72 | -193.72 |
| cube_oracle_region_local | 54.28 | 0.0404 | 24.7586 | 2.5850 | -197.72 | -193.72 |
| cube_oracle_factorized | 54.28 | 0.0404 | 24.7586 | 2.5850 | -197.72 | -193.72 |

## Long-Phrase Regime Summary
- fixed 128 results: not primary in this run
- fixed 256 results: not primary in this run
- variable-length results: not primary in this run

## Longer-Segment Utilization
- average emitted length: 64.00
- max emitted length: 64
- route coverage by length class: {'64': 1344}

## Scaling Summary
- scaling_train_bits: 5120
- scaling_cube_payload_bits: 256
- scaling_region_count: 4

## Real Descriptor-Coding Modes
- cube_actual_legacy: bits=344, ratio=3.9070, decode_success=True
- cube_fixed_length_actual: bits=160, ratio=8.4000, decode_success=True
- cube_family_local_id_actual: bits=160, ratio=8.4000, decode_success=True
- cube_entropy_coded_actual: bits=336, ratio=4.0000, decode_success=True

## Comparative Baseline Table
| Mode | Bits | Ratio |
|---|---:|---:|
| cube_best_real (cube_fixed_length_actual) | 160.0 | 8.4000 |
| family_aware | 105 | 12.8000 |
| flat_dictionary | 63 | 21.3333 |
| zlib | 248 | 5.4194 |

## Baseline Comparison
- raw_literals ratio: 0.8889
- flat_dictionary ratio: 21.3333
- family_aware ratio: 12.8000
- phrase_family_oracle ratio: 16.0000

## Decision
- target baseline: zlib (248.0 bits)
- cube_fixed_length_actual beats target: True
- cube_family_local_id_actual beats target: True
- cube_entropy_coded_actual beats target: False
- best real cube mode: cube_fixed_length_actual
- best_real_cube_minus_target_bits: -88.0
- descriptor_redesign_verdict: descriptor_redesign_fails
- any_real_cube_beats_target: True
- best cube mode: cube_entropy_estimated.whole_route
- final verdict: geometry_promising
- long_phrase_best_length_class: 64
- long_phrase_verdict: long_phrases_not_helping
- scaling_any_real_cube_beats_target: True
- scaling_verdict: scaling_promising

## Recommendation
- continue cube investigation
- pivot away from cube descriptor path
- continue cube investigation