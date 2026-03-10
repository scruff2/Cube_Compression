# Cube Route Codec Diagnostics

## Descriptor-Overhead Diagnosis
- route_count: 21
- used_route_count: 3
- region_local_route_support_sizes: {'0': 1, '2': 1, '3': 1}
- field_wise_route_cost_contribution: {'region_id_bits': 2, 'middle_id_bits': 1, 'suffix_id_bits': 1, 'token_type_overhead_bits': 1, 'optional_length_field_bits': 7}
- biggest_overhead_source: non-entropy-coded route usage

## Cube Viability Decision
- final_verdict: geometry_promising
- target_baseline: zlib
- any_real_cube_beats_target: True
- best_cube_mode: cube_entropy_estimated.whole_route
- descriptor_redesign_verdict: descriptor_redesign_fails

## Fixed-Length Mode Diagnostics
- {'length_field_present': False, 'route_only': True, 'decoded_mode': 'cube_fixed_length_actual'}

## Family-Local-ID Diagnostics
- {'region_id_width': 2, 'local_route_table_size_per_region': {'0': 1, '1': 1, '2': 1, '3': 1}, 'max_local_id_width': 0, 'avg_local_id_width': 0.0, 'route_only': True, 'decoded_mode': 'cube_family_local_id_actual'}

## Entropy-Coded Diagnostics
- {'coding_model': 'whole_route_huffman_static_canonical', 'symbol_alphabet_size': 3, 'estimated_entropy_bits_per_route': 1.584962500721156, 'actual_coded_bits': 224, 'route_only': True, 'decoded_mode': 'cube_entropy_coded_actual'}

## Length-Aware Coverage Diagnostics
- {'route_coverage_by_length_class': {'64': 1344}, 'literal_fallback_by_length_class': {'literal': 0}, 'average_route_emitted_length': 64.0, 'max_route_emitted_length': 64, 'distribution_of_emitted_lengths': {64: 21}, 'descriptor_efficiency_by_length_class': {'64': {'average_descriptor_bits': 12.0, 'average_emitted_bits': 64.0, 'descriptor_bits_per_emitted_source_bit': 0.1875}}}

## Scale-Aware Diagnostics
- {'cube_size_diagnostics': {'cube_payload_bits': 256, 'cube_payload_bytes': 32, 'metadata_bytes': 176, 'total_shared_artifact_size': 208, 'region_count_built': 4, 'region_count_used': 3, 'selected_phrases': 4, 'selected_phrases_by_length_class': {'64': 4}, 'variants_by_region_statistics': {'avg_middle_variants': 1.0, 'avg_suffix_variants': 1.0}}, 'route_span_diagnostics': {'average_emitted_bits_per_route': 64.0, 'median_emitted_bits_per_route': 64, 'max_emitted_bits_per_route': 64, 'emitted_length_distribution': {64: 21}, 'coverage_by_length_class': {'64': 1344}}, 'descriptor_efficiency_diagnostics': {'average_descriptor_bits_per_route': 12.0, 'descriptor_bits_per_emitted_source_bit': 0.1875, 'top_used_route_counts': [('2:0:0', 7), ('0:0:0', 7), ('3:0:0', 7)], 'unique_route_count': 3, 'descriptor_efficiency_degrades_with_scale': False}, 'larger_cube_utilization_diagnostics': {'fraction_regions_used': 0.75, 'fraction_selected_phrases_exercised': 0.75, 'longer_routes_from_larger_capacity': False}, 'comparative_diagnostics': {'best_real_cube_mode': 'cube_fixed_length_actual', 'best_real_cube_bits': 160.0, 'family_aware_bits': 105, 'flat_dictionary_bits': 63, 'general_purpose_bits': 248}}

## Cube Modes (JSON)
{
  "cube_actual": {
    "avg_bits_per_route_token": 12.0,
    "route_bits": 252.0,
    "total_bits": 252.0
  },
  "cube_fixed_length_optimized": {
    "avg_bits_per_route_token": 5.0,
    "route_bits": 105,
    "total_bits": 105.0
  },
  "cube_entropy_estimated": {
    "whole_route": {
      "avg_bits_per_route_token": 2.584962500721156,
      "route_bits": 54.284212515144276,
      "total_bits": 54.284212515144276
    },
    "factorized": {
      "avg_bits_per_route_token": 2.584962500721156,
      "route_bits": 54.284212515144276,
      "total_bits": 54.284212515144276
    },
    "entropy_terms": {
      "H_route": 1.584962500721156,
      "H_region": 1.584962500721156,
      "H_middle_given_region": 0.0,
      "H_suffix_given_region_middle": 0.0,
      "H_length_given_region_middle_suffix": 0.0
    }
  },
  "cube_family_local_id": {
    "avg_bits_per_route_token": 3.0,
    "route_bits": 63.0,
    "total_bits": 63.0,
    "avg_local_id_width_per_region": {
      "2": 0,
      "0": 0,
      "3": 0
    }
  },
  "cube_oracle_used_route": {
    "avg_bits_per_route_token": 2.584962500721156,
    "route_bits": 54.284212515144276,
    "total_bits": 54.284212515144276
  },
  "cube_oracle_region_local": {
    "avg_bits_per_route_token": 2.584962500721156,
    "route_bits": 54.284212515144276,
    "total_bits": 54.284212515144276
  },
  "cube_oracle_factorized": {
    "avg_bits_per_route_token": 2.584962500721156,
    "route_bits": 54.284212515144276,
    "total_bits": 54.284212515144276
  }
}