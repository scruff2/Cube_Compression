from cube_codec.cube_model import RegionLayout, reconstruct_route
from cube_codec.route_model import RouteToken


def test_route_reconstruction() -> None:
    region = RegionLayout(
        region_id=0,
        prefix_bits="1111",
        middle_variants=["00", "01"],
        suffix_variants=["10", "11"],
        route_length=8,
        prefix_length=4,
        middle_length=2,
        suffix_length=2,
    )
    token = RouteToken(token_type="R", region_id=0, middle_id=1, suffix_id=0)
    out = reconstruct_route(region, token.middle_id, token.suffix_id)
    assert out == "11110110"
