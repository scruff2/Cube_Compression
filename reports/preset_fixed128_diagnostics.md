# Cube Route Codec Diagnostics

## Descriptor-Overhead Diagnosis
- route_count: 16
- used_route_count: 9
- region_local_route_support_sizes: {'0': 3, '1': 2, '4': 4}
- field_wise_route_cost_contribution: {'region_id_bits': 6, 'middle_id_bits': 2, 'suffix_id_bits': 2, 'token_type_overhead_bits': 1, 'optional_length_field_bits': 8}
- biggest_overhead_source: non-entropy-coded route usage

## Cube Viability Decision
- final_verdict: geometry_promising
- beats_family_aware_in_any_mode: True
- best_cube_mode: cube_entropy_estimated.whole_route
- descriptor_redesign_verdict: descriptor_redesign_fails

## Fixed-Length Mode Diagnostics
- {'length_field_present': False, 'decoded_mode': 'cube_fixed_length_actual'}

## Family-Local-ID Diagnostics
- {'region_id_width': 6, 'local_route_table_size_per_region': {'0': 16, '1': 16, '2': 9, '3': 3, '4': 9, '5': 2, '6': 2, '7': 4, '8': 4, '9': 2, '10': 4, '11': 4, '12': 1, '13': 1, '14': 1, '15': 1, '16': 1, '17': 1, '18': 1, '19': 1, '20': 1, '21': 1, '22': 1, '23': 1, '24': 1, '25': 1, '26': 1, '27': 1, '28': 1, '29': 1, '30': 1, '31': 1, '32': 1, '33': 1, '34': 1, '35': 1, '36': 1, '37': 1, '38': 1, '39': 1, '40': 1, '41': 1}, 'max_local_id_width': 4, 'avg_local_id_width': 0.6904761904761905, 'decoded_mode': 'cube_family_local_id_actual'}

## Entropy-Coded Diagnostics
- {'coding_model': 'whole_route_huffman_static', 'symbol_alphabet_size': 8, 'estimated_entropy_bits_per_route': 2.840223928941852, 'actual_coded_bits': 936, 'decoded_mode': 'cube_entropy_coded_actual'}

## Length-Aware Coverage Diagnostics
- {'route_coverage_by_length_class': {'128': 2048}, 'literal_fallback_by_length_class': {'literal': 8}, 'average_route_emitted_length': 128.0, 'max_route_emitted_length': 128, 'distribution_of_emitted_lengths': {128: 16}, 'descriptor_efficiency_by_length_class': {'128': {'average_descriptor_bits': 19.0, 'average_emitted_bits': 128.0, 'descriptor_bits_per_emitted_source_bit': 0.1484375}}}

## Scale-Aware Diagnostics
- {'cube_size_diagnostics': {'cube_payload_bits': 6432, 'cube_payload_bytes': 804, 'metadata_bytes': 181, 'total_shared_artifact_size': 985, 'region_count_built': 42, 'region_count_used': 3, 'selected_phrases': 61, 'selected_phrases_by_length_class': {'128': 61}, 'variants_by_region_statistics': {'avg_middle_variants': 1.3333333333333333, 'avg_suffix_variants': 1.4523809523809523}}, 'route_span_diagnostics': {'average_emitted_bits_per_route': 128.0, 'median_emitted_bits_per_route': 128.0, 'max_emitted_bits_per_route': 128, 'emitted_length_distribution': {128: 16}, 'coverage_by_length_class': {'128': 2048}}, 'descriptor_efficiency_diagnostics': {'average_descriptor_bits_per_route': 19.0, 'descriptor_bits_per_emitted_source_bit': 0.1484375, 'top_used_route_counts': [('4:0:0', 4), ('1:2:2', 2), ('0:0:0', 2), ('0:2:2', 2), ('4:1:1', 2), ('1:0:0', 1), ('4:1:0', 1), ('4:2:2', 1), ('0:3:3', 1)], 'unique_route_count': 9, 'descriptor_efficiency_degrades_with_scale': False}, 'larger_cube_utilization_diagnostics': {'fraction_regions_used': 0.07142857142857142, 'fraction_selected_phrases_exercised': 0.14754098360655737, 'longer_routes_from_larger_capacity': True}, 'comparative_diagnostics': {'best_real_cube_mode': 'cube_fixed_length_actual', 'best_real_cube_bits': 480.0, 'family_aware_bits': 309, 'flat_dictionary_bits': 249, 'general_purpose_bits': 1072}}

## Cube Modes (JSON)
{
  "cube_actual": {
    "avg_bits_per_route_token": 19.0,
    "route_bits": 304.0,
    "total_bits": 376.0
  },
  "cube_fixed_length_optimized": {
    "avg_bits_per_route_token": 11.0,
    "route_bits": 176,
    "total_bits": 248.0
  },
  "cube_entropy_estimated": {
    "whole_route": {
      "avg_bits_per_route_token": 4.0,
      "route_bits": 64.0,
      "total_bits": 136.0
    },
    "factorized": {
      "avg_bits_per_route_token": 4.0,
      "route_bits": 64.0,
      "total_bits": 136.0
    },
    "entropy_terms": {
      "H_route": 3.0,
      "H_region": 1.4772170014624826,
      "H_middle_given_region": 1.3506025296523005,
      "H_suffix_given_region_middle": 0.1721804688852168,
      "H_length_given_region_middle_suffix": 0.0
    }
  },
  "cube_family_local_id": {
    "avg_bits_per_route_token": 4.8125,
    "route_bits": 77.0,
    "total_bits": 149.0,
    "avg_local_id_width_per_region": {
      "1": 1,
      "4": 2,
      "0": 2
    }
  },
  "cube_oracle_used_route": {
    "avg_bits_per_route_token": 4.0,
    "route_bits": 64.0,
    "total_bits": 136.0
  },
  "cube_oracle_region_local": {
    "avg_bits_per_route_token": 4.0,
    "route_bits": 64.0,
    "total_bits": 136.0
  },
  "cube_oracle_factorized": {
    "avg_bits_per_route_token": 4.0,
    "route_bits": 64.0,
    "total_bits": 136.0
  }
}