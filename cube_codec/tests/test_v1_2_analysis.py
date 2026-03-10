from cube_codec.cost_model import RouteCostBreakdown, build_route_analysis, empirical_entropy
from cube_codec.route_model import RouteToken


def _tokens() -> list[RouteToken]:
    return [
        RouteToken(token_type="R", region_id=0, middle_id=0, suffix_id=0),
        RouteToken(token_type="R", region_id=0, middle_id=0, suffix_id=1),
        RouteToken(token_type="R", region_id=0, middle_id=0, suffix_id=1),
        RouteToken(token_type="R", region_id=1, middle_id=1, suffix_id=0),
    ]


def test_fixed_length_optimization_drops_length_cost() -> None:
    breakdown = RouteCostBreakdown(3, 2, 2, 1, 5)
    analysis = build_route_analysis(_tokens(), literal_total_bits=0.0, phrase_length=64, route_breakdown=breakdown, token_overhead_bits=1)
    assert analysis["cube_fixed_length_optimized"]["avg_bits_per_route_token"] <= analysis["cube_actual"]["avg_bits_per_route_token"] - 5


def test_entropy_estimate_sanity() -> None:
    from collections import Counter

    h = empirical_entropy(Counter({"a": 8, "b": 8}))
    assert 0.99 <= h <= 1.01


def test_family_local_id_not_worse_than_actual_for_small_support() -> None:
    breakdown = RouteCostBreakdown(3, 3, 3, 1, 4)
    analysis = build_route_analysis(_tokens(), literal_total_bits=0.0, phrase_length=64, route_breakdown=breakdown, token_overhead_bits=1)
    assert analysis["cube_family_local_id"]["avg_bits_per_route_token"] <= analysis["cube_actual"]["avg_bits_per_route_token"]


def test_oracle_modes_monotonic() -> None:
    breakdown = RouteCostBreakdown(4, 4, 4, 1, 5)
    analysis = build_route_analysis(_tokens(), literal_total_bits=0.0, phrase_length=64, route_breakdown=breakdown, token_overhead_bits=1)
    actual = analysis["cube_actual"]["avg_bits_per_route_token"]
    assert analysis["cube_oracle_used_route"]["avg_bits_per_route_token"] <= actual
    assert analysis["cube_oracle_region_local"]["avg_bits_per_route_token"] <= actual
    assert analysis["cube_oracle_factorized"]["avg_bits_per_route_token"] <= actual
