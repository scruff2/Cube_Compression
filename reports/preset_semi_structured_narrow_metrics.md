# Cube Route Codec Benchmark Report

## Configuration Used
- phrase_length: 256
- stride: 32

## Cube Descriptor Idealization Table
| Mode | Total Bits | Bits/Source Bit | Compression Ratio | Avg Bits/Route | Delta vs cube_actual | Delta vs target_baseline |
|---|---:|---:|---:|---:|---:|---:|
| cube_actual | 167211.00 | 0.8176 | 1.2230 | 31.0000 | 0.00 | 109291.00 |
| cube_fixed_length_optimized | 156114.00 | 0.7634 | 1.3100 | 22.0000 | -11097.00 | 98194.00 |
| cube_entropy_estimated.whole_route | 140560.09 | 0.6873 | 1.4549 | 9.3853 | -26650.91 | 82640.09 |
| cube_entropy_estimated.factorized | 140560.09 | 0.6873 | 1.4549 | 9.3853 | -26650.91 | 82640.09 |
| cube_family_local_id | 141952.00 | 0.6941 | 1.4407 | 10.5142 | -25259.00 | 84032.00 |
| cube_oracle_used_route | 140560.09 | 0.6873 | 1.4549 | 9.3853 | -26650.91 | 82640.09 |
| cube_oracle_region_local | 140560.09 | 0.6873 | 1.4549 | 9.3853 | -26650.91 | 82640.09 |
| cube_oracle_factorized | 140560.09 | 0.6873 | 1.4549 | 9.3853 | -26650.91 | 82640.09 |

## Long-Phrase Regime Summary
- fixed 128 results: available
- fixed 256 results: available
- variable-length results: available

## Longer-Segment Utilization
- average emitted length: 73.34
- max emitted length: 256
- route coverage by length class: {'64': 69760, '192': 6336, '128': 13824, '256': 512}

## Scaling Summary
- scaling_train_bits: 500728
- scaling_cube_payload_bits: 201744
- scaling_region_count: 1777

## Real Descriptor-Coding Modes
- cube_actual_legacy: bits=280752, ratio=0.7284, decode_success=True
- cube_fixed_length_actual: bits=58064, ratio=3.5220, decode_success=True
- cube_family_local_id_actual: bits=58064, ratio=3.5220, decode_success=True
- cube_entropy_coded_actual: bits=58064, ratio=3.5220, decode_success=True

## Comparative Baseline Table
| Mode | Bits | Ratio |
|---|---:|---:|
| cube_best_real (cube_fixed_length_actual) | 58064.0 | 3.5220 |
| family_aware | 164307 | 1.2446 |
| flat_dictionary | 143874 | 1.4214 |
| zlib | 57920 | 3.5308 |

## Baseline Comparison
- raw_literals ratio: 0.8889
- flat_dictionary ratio: 1.4214
- family_aware ratio: 1.2446
- phrase_family_oracle ratio: 8.3662

## Decision
- target baseline: zlib (57920.0 bits)
- cube_fixed_length_actual beats target: False
- cube_family_local_id_actual beats target: False
- cube_entropy_coded_actual beats target: False
- best real cube mode: cube_fixed_length_actual
- best_real_cube_minus_target_bits: 144.0
- descriptor_redesign_verdict: descriptor_redesign_succeeds
- any_real_cube_beats_target: False
- best cube mode: cube_entropy_estimated.whole_route
- final verdict: geometry_promising
- long_phrase_best_length_class: 64
- long_phrase_verdict: long_phrases_promising
- scaling_any_real_cube_beats_target: False
- scaling_verdict: scaling_not_helping

## Recommendation
- continue cube investigation
- continue cube investigation
- pivot away from cube descriptor path