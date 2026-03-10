from cube_codec.config import CodecConfig
from cube_codec.cube_io import load_cube, save_cube
from cube_codec.region_builder import build_cube_model
from cube_codec.cube_model import RegionLayout


def test_cube_io_roundtrip(tmp_path) -> None:
    config = CodecConfig()
    region = RegionLayout(
        region_id=0,
        prefix_bits="0" * 32,
        middle_variants=["1010101010101010"],
        suffix_variants=["1111000011110000"],
        route_length=64,
        prefix_length=32,
        middle_length=16,
        suffix_length=16,
    )
    cube = build_cube_model([region], config)
    save_cube(cube, tmp_path)
    loaded = load_cube(tmp_path)

    assert loaded.metadata.region_count == 1
    assert loaded.regions[0].prefix_bits == region.prefix_bits
