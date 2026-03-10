from cube_codec.config import CodecConfig
from cube_codec.cost_model import build_token_cost_model
from cube_codec.cube_model import RegionLayout
from cube_codec.decoder import decode_stream
from cube_codec.encoder import encode_bits
from cube_codec.region_builder import build_cube_model
from cube_codec.route_index import build_prefix_index


def test_encoder_decoder_roundtrip() -> None:
    cfg = CodecConfig(phrase_length=16, prefix_index_bits=8, literal_block_bits=4)
    region = RegionLayout(
        region_id=0,
        prefix_bits="10101010",
        middle_variants=["1111", "0000"],
        suffix_variants=["00", "11"],
        route_length=14,
        prefix_length=8,
        middle_length=4,
        suffix_length=2,
    )
    cube = build_cube_model([region], cfg)
    idx = build_prefix_index(cube, cfg.prefix_index_bits)
    source = "10101010111100" * 2 + "0011"

    stream, _ = encode_bits(source, cube, idx, cfg, build_token_cost_model(cfg, cube))
    decoded = decode_stream(stream, cube)
    assert decoded == source
