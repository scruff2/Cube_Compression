from cube_codec.config import CodecConfig
from cube_codec.cube_model import RegionLayout
from cube_codec.region_builder import build_cube_model
from cube_codec.route_index import build_prefix_index


def test_prefix_index() -> None:
    cfg = CodecConfig(phrase_length=8, prefix_index_bits=4)
    region = RegionLayout(
        region_id=0,
        prefix_bits="1111",
        middle_variants=["0", "1"],
        suffix_variants=["00", "11"],
        route_length=7,
        prefix_length=4,
        middle_length=1,
        suffix_length=2,
    )
    cube = build_cube_model([region], cfg)
    idx = build_prefix_index(cube, cfg.prefix_index_bits)
    cands = idx.query("1111000")
    assert len(cands) >= 1
