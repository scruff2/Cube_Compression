# Cube Route Codec Diagnostics

## Descriptor-Overhead Diagnosis
- route_count: 14
- used_route_count: 12
- region_local_route_support_sizes: {'224': 1, '226': 1, '69': 1, '172': 1, '237': 1, '219': 1, '239': 1, '16': 1, '211': 1, '27': 1, '254': 1, '95': 1}
- field_wise_route_cost_contribution: {'region_id_bits': 9, 'middle_id_bits': 2, 'suffix_id_bits': 2, 'token_type_overhead_bits': 1, 'optional_length_field_bits': 9}
- biggest_overhead_source: non-entropy-coded route usage

## Cube Viability Decision
- final_verdict: geometry_promising
- beats_family_aware_in_any_mode: True
- best_cube_mode: cube_entropy_estimated.whole_route
- descriptor_redesign_verdict: descriptor_redesign_fails

## Fixed-Length Mode Diagnostics
- {'length_field_present': False, 'route_only': True, 'decoded_mode': 'cube_fixed_length_actual'}

## Family-Local-ID Diagnostics
- {'region_id_width': 9, 'local_route_table_size_per_region': {'0': 9, '1': 4, '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1, '10': 1, '11': 1, '12': 1, '13': 1, '14': 1, '15': 1, '16': 1, '17': 1, '18': 1, '19': 1, '20': 1, '21': 1, '22': 1, '23': 1, '24': 1, '25': 1, '26': 1, '27': 1, '28': 1, '29': 1, '30': 1, '31': 1, '32': 1, '33': 1, '34': 1, '35': 1, '36': 1, '37': 1, '38': 1, '39': 1, '40': 1, '41': 1, '42': 1, '43': 1, '44': 1, '45': 1, '46': 1, '47': 1, '48': 1, '49': 1, '50': 1, '51': 1, '52': 1, '53': 1, '54': 1, '55': 1, '56': 1, '57': 1, '58': 1, '59': 1, '60': 1, '61': 1, '62': 1, '63': 1, '64': 1, '65': 1, '66': 1, '67': 1, '68': 1, '69': 1, '70': 1, '71': 1, '72': 1, '73': 1, '74': 1, '75': 1, '76': 9, '77': 2, '78': 4, '79': 1, '80': 1, '81': 1, '82': 1, '83': 1, '84': 1, '85': 1, '86': 1, '87': 1, '88': 1, '89': 1, '90': 1, '91': 1, '92': 1, '93': 1, '94': 1, '95': 1, '96': 1, '97': 1, '98': 1, '99': 1, '100': 1, '101': 1, '102': 1, '103': 1, '104': 1, '105': 1, '106': 1, '107': 1, '108': 1, '109': 1, '110': 1, '111': 1, '112': 1, '113': 1, '114': 1, '115': 1, '116': 1, '117': 1, '118': 1, '119': 1, '120': 1, '121': 1, '122': 1, '123': 1, '124': 1, '125': 1, '126': 1, '127': 1, '128': 1, '129': 1, '130': 1, '131': 1, '132': 1, '133': 1, '134': 1, '135': 1, '136': 1, '137': 1, '138': 1, '139': 1, '140': 1, '141': 1, '142': 1, '143': 1, '144': 1, '145': 1, '146': 1, '147': 1, '148': 1, '149': 1, '150': 4, '151': 4, '152': 1, '153': 1, '154': 1, '155': 1, '156': 1, '157': 1, '158': 1, '159': 1, '160': 1, '161': 1, '162': 1, '163': 1, '164': 1, '165': 1, '166': 1, '167': 1, '168': 1, '169': 1, '170': 1, '171': 1, '172': 1, '173': 1, '174': 1, '175': 1, '176': 1, '177': 1, '178': 1, '179': 1, '180': 1, '181': 1, '182': 1, '183': 1, '184': 1, '185': 1, '186': 1, '187': 1, '188': 1, '189': 1, '190': 1, '191': 1, '192': 1, '193': 1, '194': 1, '195': 1, '196': 1, '197': 1, '198': 1, '199': 1, '200': 1, '201': 1, '202': 1, '203': 1, '204': 1, '205': 1, '206': 1, '207': 1, '208': 1, '209': 1, '210': 1, '211': 1, '212': 1, '213': 1, '214': 1, '215': 1, '216': 1, '217': 4, '218': 1, '219': 1, '220': 1, '221': 1, '222': 1, '223': 1, '224': 1, '225': 1, '226': 1, '227': 1, '228': 1, '229': 1, '230': 1, '231': 1, '232': 1, '233': 1, '234': 1, '235': 1, '236': 1, '237': 1, '238': 1, '239': 1, '240': 1, '241': 1, '242': 1, '243': 1, '244': 1, '245': 1, '246': 1, '247': 1, '248': 1, '249': 1, '250': 1, '251': 1, '252': 1, '253': 1, '254': 1, '255': 1, '256': 1, '257': 1, '258': 1, '259': 1, '260': 1, '261': 1, '262': 1, '263': 1, '264': 1, '265': 1, '266': 1, '267': 1, '268': 1}, 'max_local_id_width': 4, 'avg_local_id_width': 0.07063197026022305, 'route_only': True, 'decoded_mode': 'cube_family_local_id_actual'}

## Entropy-Coded Diagnostics
- {'coding_model': 'whole_route_huffman_static_canonical', 'symbol_alphabet_size': 12, 'estimated_entropy_bits_per_route': 3.521640636343319, 'actual_coded_bits': 744, 'route_only': True, 'decoded_mode': 'cube_entropy_coded_actual'}

## Length-Aware Coverage Diagnostics
- {'route_coverage_by_length_class': {'192': 384, '256': 1792, '64': 256, '128': 128}, 'literal_fallback_by_length_class': {'literal': 0}, 'average_route_emitted_length': 182.85714285714286, 'max_route_emitted_length': 256, 'distribution_of_emitted_lengths': {192: 2, 256: 7, 64: 4, 128: 1}, 'descriptor_efficiency_by_length_class': {'64': {'average_descriptor_bits': 23.0, 'average_emitted_bits': 64.0, 'descriptor_bits_per_emitted_source_bit': 0.359375}, '128': {'average_descriptor_bits': 23.0, 'average_emitted_bits': 128.0, 'descriptor_bits_per_emitted_source_bit': 0.1796875}, '192': {'average_descriptor_bits': 23.0, 'average_emitted_bits': 192.0, 'descriptor_bits_per_emitted_source_bit': 0.11979166666666667}, '256': {'average_descriptor_bits': 23.0, 'average_emitted_bits': 256.0, 'descriptor_bits_per_emitted_source_bit': 0.08984375}}}

## Scale-Aware Diagnostics
- {'cube_size_diagnostics': {'cube_payload_bits': 41152, 'cube_payload_bytes': 5144, 'metadata_bytes': 180, 'total_shared_artifact_size': 5324, 'region_count_built': 269, 'region_count_used': 12, 'selected_phrases': 279, 'selected_phrases_by_length_class': {'64': 79, '128': 78, '192': 69, '256': 53}, 'variants_by_region_statistics': {'avg_middle_variants': 1.033457249070632, 'avg_suffix_variants': 1.037174721189591}}, 'route_span_diagnostics': {'average_emitted_bits_per_route': 182.85714285714286, 'median_emitted_bits_per_route': 224.0, 'max_emitted_bits_per_route': 256, 'emitted_length_distribution': {192: 2, 256: 7, 64: 4, 128: 1}, 'coverage_by_length_class': {'192': 384, '256': 1792, '64': 256, '128': 128}}, 'descriptor_efficiency_diagnostics': {'average_descriptor_bits_per_route': 23.0, 'descriptor_bits_per_emitted_source_bit': 0.12578125, 'top_used_route_counts': [('69:0:0', 2), ('226:0:0', 2), ('211:0:0', 1), ('172:0:0', 1), ('237:0:0', 1), ('95:0:0', 1), ('27:0:0', 1), ('224:0:0', 1), ('219:0:0', 1), ('239:0:0', 1)], 'unique_route_count': 12, 'descriptor_efficiency_degrades_with_scale': False}, 'larger_cube_utilization_diagnostics': {'fraction_regions_used': 0.04460966542750929, 'fraction_selected_phrases_exercised': 0.043010752688172046, 'longer_routes_from_larger_capacity': True}, 'comparative_diagnostics': {'best_real_cube_mode': 'cube_family_local_id_actual', 'best_real_cube_bits': 240.0, 'family_aware_bits': 182, 'flat_dictionary_bits': 140, 'general_purpose_bits': 1904}}

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