from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any

from .config import CodecConfig
from .cube_model import CubeModel
from .route_model import LiteralToken, RouteToken


@dataclass
class RouteCostBreakdown:
    region_id_bits: int
    middle_id_bits: int
    suffix_id_bits: int
    token_type_overhead_bits: int
    optional_length_field_bits: int

    @property
    def total_bits(self) -> int:
        return (
            self.region_id_bits
            + self.middle_id_bits
            + self.suffix_id_bits
            + self.token_type_overhead_bits
            + self.optional_length_field_bits
        )


@dataclass
class TokenCostModel:
    config: CodecConfig
    route_breakdown: RouteCostBreakdown

    def route_cost(self, token: RouteToken) -> float:
        _ = token
        return float(self.route_breakdown.total_bits)

    def literal_cost(self, token: LiteralToken) -> float:
        return float(self.config.literal_token_overhead_bits + token.bit_length)


def _bit_width(cardinality: int) -> int:
    return max(1, math.ceil(math.log2(max(1, cardinality))))


def _bit_width_allow_zero(cardinality: int) -> int:
    if cardinality <= 1:
        return 0
    return math.ceil(math.log2(cardinality))


def empirical_entropy(counter: Counter[Any]) -> float:
    total = sum(counter.values())
    if total <= 0:
        return 0.0
    h = 0.0
    for count in counter.values():
        p = count / total
        h -= p * math.log2(p)
    return h


def route_symbol(token: RouteToken, phrase_length: int) -> tuple[int, int, int, int]:
    length = token.emit_length if token.emit_length is not None else phrase_length
    return (token.region_id, token.middle_id, token.suffix_id, length)


def build_route_analysis(
    route_tokens: list[RouteToken],
    literal_total_bits: float,
    phrase_length: int,
    route_breakdown: RouteCostBreakdown,
    token_overhead_bits: int,
) -> dict:
    route_count = len(route_tokens)
    if route_count == 0:
        zero = {
            "avg_bits_per_route_token": 0.0,
            "route_bits": 0.0,
            "total_bits": float(literal_total_bits),
        }
        return {
            "cube_actual": zero,
            "cube_fixed_length_optimized": zero,
            "cube_entropy_estimated": {"whole_route": zero, "factorized": zero, "entropy_terms": {}},
            "cube_family_local_id": zero | {"avg_local_id_width_per_region": {}},
            "cube_oracle_used_route": zero,
            "cube_oracle_region_local": zero,
            "cube_oracle_factorized": zero,
        }

    route_counter: Counter[tuple[int, int, int, int]] = Counter(route_symbol(t, phrase_length) for t in route_tokens)
    region_counter: Counter[int] = Counter(t.region_id for t in route_tokens)
    middle_given_region: dict[int, Counter[int]] = {}
    suffix_given_pair: dict[tuple[int, int], Counter[int]] = {}
    length_given_triplet: dict[tuple[int, int, int], Counter[int]] = {}
    route_given_region: dict[int, Counter[tuple[int, int, int, int]]] = {}
    for t in route_tokens:
        length = t.emit_length if t.emit_length is not None else phrase_length
        middle_given_region.setdefault(t.region_id, Counter())[t.middle_id] += 1
        suffix_given_pair.setdefault((t.region_id, t.middle_id), Counter())[t.suffix_id] += 1
        length_given_triplet.setdefault((t.region_id, t.middle_id, t.suffix_id), Counter())[length] += 1
        route_given_region.setdefault(t.region_id, Counter())[(t.region_id, t.middle_id, t.suffix_id, length)] += 1

    actual_avg = float(route_breakdown.total_bits)
    actual_bits = actual_avg * route_count

    fixed_breakdown = route_breakdown.total_bits - route_breakdown.optional_length_field_bits
    unique_regions = len(region_counter)
    unique_middles = len({(t.region_id, t.middle_id) for t in route_tokens})
    unique_suffixes = len({(t.region_id, t.middle_id, t.suffix_id) for t in route_tokens})
    if unique_regions <= 1:
        fixed_breakdown -= route_breakdown.region_id_bits
    if unique_middles <= 1:
        fixed_breakdown -= route_breakdown.middle_id_bits
    if unique_suffixes <= 1:
        fixed_breakdown -= route_breakdown.suffix_id_bits
    fixed_breakdown = max(token_overhead_bits, fixed_breakdown)
    fixed_bits = fixed_breakdown * route_count

    h_route = empirical_entropy(route_counter)
    whole_avg = token_overhead_bits + h_route
    whole_bits = whole_avg * route_count

    h_region = empirical_entropy(region_counter)
    h_mid = 0.0
    for c in middle_given_region.values():
        w = sum(c.values()) / route_count
        h_mid += w * empirical_entropy(c)
    h_suf = 0.0
    for c in suffix_given_pair.values():
        w = sum(c.values()) / route_count
        h_suf += w * empirical_entropy(c)
    h_len = 0.0
    for c in length_given_triplet.values():
        w = sum(c.values()) / route_count
        h_len += w * empirical_entropy(c)
    factorized_avg = token_overhead_bits + h_region + h_mid + h_suf + h_len
    factorized_bits = factorized_avg * route_count

    used_regions = len(route_given_region)
    region_bits = _bit_width_allow_zero(used_regions)
    local_widths: dict[str, int] = {}
    local_weighted = 0.0
    for rid, c in route_given_region.items():
        width = _bit_width_allow_zero(len(c))
        local_widths[str(rid)] = width
        local_weighted += (sum(c.values()) / route_count) * width
    family_local_avg = token_overhead_bits + region_bits + local_weighted
    family_local_bits = family_local_avg * route_count

    oracle_used_avg = token_overhead_bits + h_route
    oracle_used_bits = oracle_used_avg * route_count

    h_region_local = 0.0
    for c in route_given_region.values():
        w = sum(c.values()) / route_count
        h_region_local += w * empirical_entropy(c)
    oracle_region_local_avg = token_overhead_bits + h_region + h_region_local
    oracle_region_local_bits = oracle_region_local_avg * route_count

    oracle_factorized_avg = token_overhead_bits + h_region + h_mid + h_suf
    oracle_factorized_bits = oracle_factorized_avg * route_count

    def build(avg: float, route_bits: float) -> dict:
        return {
            "avg_bits_per_route_token": avg,
            "route_bits": route_bits,
            "total_bits": route_bits + float(literal_total_bits),
        }

    return {
        "cube_actual": build(actual_avg, actual_bits),
        "cube_fixed_length_optimized": build(float(fixed_breakdown), fixed_bits),
        "cube_entropy_estimated": {
            "whole_route": build(whole_avg, whole_bits),
            "factorized": build(factorized_avg, factorized_bits),
            "entropy_terms": {
                "H_route": h_route,
                "H_region": h_region,
                "H_middle_given_region": h_mid,
                "H_suffix_given_region_middle": h_suf,
                "H_length_given_region_middle_suffix": h_len,
            },
        },
        "cube_family_local_id": build(family_local_avg, family_local_bits)
        | {"avg_local_id_width_per_region": local_widths},
        "cube_oracle_used_route": build(oracle_used_avg, oracle_used_bits),
        "cube_oracle_region_local": build(oracle_region_local_avg, oracle_region_local_bits),
        "cube_oracle_factorized": build(oracle_factorized_avg, oracle_factorized_bits),
    }


def build_token_cost_model(config: CodecConfig, cube: CubeModel) -> TokenCostModel:
    middle_max = max((len(r.middle_variants) for r in cube.regions), default=1)
    suffix_max = max((len(r.suffix_variants) for r in cube.regions), default=1)
    region_bits = _bit_width(len(cube.regions))
    middle_bits = _bit_width(middle_max)
    suffix_bits = _bit_width(suffix_max)
    length_bits = _bit_width(config.phrase_length + 1)
    breakdown = RouteCostBreakdown(
        region_id_bits=region_bits,
        middle_id_bits=middle_bits,
        suffix_id_bits=suffix_bits,
        token_type_overhead_bits=config.route_token_overhead_bits,
        optional_length_field_bits=length_bits,
    )
    return TokenCostModel(config=config, route_breakdown=breakdown)
