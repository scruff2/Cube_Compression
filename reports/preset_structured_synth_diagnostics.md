# Cube Route Codec Diagnostics

## Descriptor-Overhead Diagnosis
- route_count: 14
- used_route_count: 12
- region_local_route_support_sizes: {'224': 1, '226': 1, '69': 1, '172': 1, '237': 1, '219': 1, '239': 1, '16': 1, '211': 1, '27': 1, '254': 1, '95': 1}
- field_wise_route_cost_contribution: {'region_id_bits': 9, 'middle_id_bits': 2, 'suffix_id_bits': 2, 'token_type_overhead_bits': 1, 'optional_length_field_bits': 9}
- biggest_overhead_source: non-entropy-coded route usage

## Cube Viability Decision
- final_verdict: geometry_promising
- target_baseline: zlib
- any_real_cube_beats_target: True
- best_cube_mode: cube_entropy_estimated.whole_route
- descriptor_redesign_verdict: descriptor_redesign_fails

## Fixed-Length Mode Diagnostics
- {'container': 'CCM3', 'chunk_count': 1, 'route_chunks': 1, 'literal_chunks': 0, 'literal_chunk_fraction': 0.0, 'decoded_mode': 'cube_fixed_length_actual'}

## Family-Local-ID Diagnostics
- {'container': 'CCM3', 'chunk_count': 1, 'route_chunks': 1, 'literal_chunks': 0, 'literal_chunk_fraction': 0.0, 'decoded_mode': 'cube_family_local_id_actual'}

## Entropy-Coded Diagnostics
- {'container': 'CCM3', 'chunk_count': 1, 'route_chunks': 1, 'literal_chunks': 0, 'literal_chunk_fraction': 0.0, 'decoded_mode': 'cube_entropy_coded_actual'}

## Length-Aware Coverage Diagnostics
- {'route_coverage_by_length_class': {'192': 384, '256': 1792, '64': 256, '128': 128}, 'literal_fallback_by_length_class': {'literal': 0}, 'average_route_emitted_length': 182.85714285714286, 'max_route_emitted_length': 256, 'distribution_of_emitted_lengths': {192: 2, 256: 7, 64: 4, 128: 1}, 'descriptor_efficiency_by_length_class': {'64': {'average_descriptor_bits': 23.0, 'average_emitted_bits': 64.0, 'descriptor_bits_per_emitted_source_bit': 0.359375}, '128': {'average_descriptor_bits': 23.0, 'average_emitted_bits': 128.0, 'descriptor_bits_per_emitted_source_bit': 0.1796875}, '192': {'average_descriptor_bits': 23.0, 'average_emitted_bits': 192.0, 'descriptor_bits_per_emitted_source_bit': 0.11979166666666667}, '256': {'average_descriptor_bits': 23.0, 'average_emitted_bits': 256.0, 'descriptor_bits_per_emitted_source_bit': 0.08984375}}}

## Scale-Aware Diagnostics
- {'cube_size_diagnostics': {'cube_payload_bits': 41152, 'cube_payload_bytes': 5144, 'metadata_bytes': 182, 'total_shared_artifact_size': 5326, 'region_count_built': 269, 'region_count_used': 12, 'selected_phrases': 279, 'selected_phrases_by_length_class': {'64': 79, '128': 78, '192': 69, '256': 53}, 'variants_by_region_statistics': {'avg_middle_variants': 1.033457249070632, 'avg_suffix_variants': 1.037174721189591}}, 'route_span_diagnostics': {'average_emitted_bits_per_route': 182.85714285714286, 'median_emitted_bits_per_route': 224.0, 'max_emitted_bits_per_route': 256, 'emitted_length_distribution': {192: 2, 256: 7, 64: 4, 128: 1}, 'coverage_by_length_class': {'192': 384, '256': 1792, '64': 256, '128': 128}}, 'descriptor_efficiency_diagnostics': {'average_descriptor_bits_per_route': 23.0, 'descriptor_bits_per_emitted_source_bit': 0.12578125, 'top_used_route_counts': [('69:0:0', 2), ('226:0:0', 2), ('211:0:0', 1), ('172:0:0', 1), ('237:0:0', 1), ('95:0:0', 1), ('27:0:0', 1), ('224:0:0', 1), ('219:0:0', 1), ('239:0:0', 1)], 'unique_route_count': 12, 'descriptor_efficiency_degrades_with_scale': False}, 'larger_cube_utilization_diagnostics': {'fraction_regions_used': 0.04460966542750929, 'fraction_selected_phrases_exercised': 0.043010752688172046, 'longer_routes_from_larger_capacity': True}, 'comparative_diagnostics': {'best_real_cube_mode': 'cube_family_local_id_actual', 'best_real_cube_bits': 320.0, 'family_aware_bits': 196, 'flat_dictionary_bits': 140, 'general_purpose_bits': 1904}}

## Cube Modes (JSON)
{
  "cube_actual": {
    "avg_bits_per_route_token": 23.0,
    "route_bits": 322.0,
    "total_bits": 322.0
  },
  "cube_fixed_length_optimized": {
    "avg_bits_per_route_token": 14.0,
    "route_bits": 196,
    "total_bits": 196.0
  },
  "cube_entropy_estimated": {
    "whole_route": {
      "avg_bits_per_route_token": 4.521640636343319,
      "route_bits": 63.30296890880646,
      "total_bits": 63.30296890880646
    },
    "factorized": {
      "avg_bits_per_route_token": 4.521640636343319,
      "route_bits": 63.30296890880646,
      "total_bits": 63.30296890880646
    },
    "entropy_terms": {
      "H_route": 3.521640636343319,
      "H_region": 3.521640636343319,
      "H_middle_given_region": 0.0,
      "H_suffix_given_region_middle": 0.0,
      "H_length_given_region_middle_suffix": 0.0
    }
  },
  "cube_family_local_id": {
    "avg_bits_per_route_token": 5.0,
    "route_bits": 70.0,
    "total_bits": 70.0,
    "avg_local_id_width_per_region": {
      "211": 0,
      "172": 0,
      "237": 0,
      "69": 0,
      "95": 0,
      "27": 0,
      "224": 0,
      "219": 0,
      "226": 0,
      "239": 0,
      "16": 0,
      "254": 0
    }
  },
  "cube_oracle_used_route": {
    "avg_bits_per_route_token": 4.521640636343319,
    "route_bits": 63.30296890880646,
    "total_bits": 63.30296890880646
  },
  "cube_oracle_region_local": {
    "avg_bits_per_route_token": 4.521640636343319,
    "route_bits": 63.30296890880646,
    "total_bits": 63.30296890880646
  },
  "cube_oracle_factorized": {
    "avg_bits_per_route_token": 4.521640636343319,
    "route_bits": 63.30296890880646,
    "total_bits": 63.30296890880646
  }
}