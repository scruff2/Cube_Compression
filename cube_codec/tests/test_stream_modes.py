from cube_codec.config import CodecConfig
from cube_codec.cube_model import RegionLayout
from cube_codec.decoder import decode_stream
from cube_codec.encoder import encode_bits
from cube_codec.region_builder import build_cube_model
from cube_codec.route_index import build_prefix_index
from cube_codec.cost_model import build_token_cost_model
from cube_codec.stream_codecs import (
    MODE_ENTROPY,
    MODE_FIXED,
    MODE_LEGACY,
    MODE_LOCAL,
    decode_mode_stream,
    encode_mode_stream,
)


def _simple_case():
    cfg = CodecConfig(phrase_length=16, prefix_index_bits=8, literal_block_bits=4)
    region = RegionLayout(
        region_id=0,
        prefix_bits="10101010",
        middle_variants=["1111"],
        suffix_variants=["00"],
        route_length=14,
        prefix_length=8,
        middle_length=4,
        suffix_length=2,
    )
    cube = build_cube_model([region], cfg)
    idx = build_prefix_index(cube, cfg.prefix_index_bits)
    source = "10101010111100" * 2
    stream, _ = encode_bits(source, cube, idx, cfg, build_token_cost_model(cfg, cube))
    return cfg, cube, source, stream


def test_fixed_length_stream_omits_length_and_roundtrips() -> None:
    cfg, cube, source, stream = _simple_case()
    fixed_payload, _ = encode_mode_stream(stream, cube, MODE_FIXED)
    legacy_payload, _ = encode_mode_stream(stream, cube, MODE_LEGACY)
    assert len(fixed_payload) < len(legacy_payload)

    decoded_stream, mode = decode_mode_stream(fixed_payload, cube)
    assert mode == MODE_FIXED
    assert decode_stream(decoded_stream, cube) == source


def test_family_local_id_stream_deterministic_and_roundtrip() -> None:
    cfg, cube, source, stream = _simple_case()
    p1, _ = encode_mode_stream(stream, cube, MODE_LOCAL)
    p2, _ = encode_mode_stream(stream, cube, MODE_LOCAL)
    assert p1 == p2

    decoded_stream, mode = decode_mode_stream(p1, cube)
    assert mode == MODE_LOCAL
    assert decode_stream(decoded_stream, cube) == source


def test_entropy_stream_roundtrip_deterministic() -> None:
    cfg, cube, source, stream = _simple_case()
    p1, _ = encode_mode_stream(stream, cube, MODE_ENTROPY)
    p2, _ = encode_mode_stream(stream, cube, MODE_ENTROPY)
    assert p1 == p2

    decoded_stream, mode = decode_mode_stream(p1, cube)
    assert mode == MODE_ENTROPY
    assert decode_stream(decoded_stream, cube) == source
