import pytest

from cube_codec.config import CodecConfig
from cube_codec.cube_model import RegionLayout
from cube_codec.decoder import decode_stream
from cube_codec.encoder import encode_bits
from cube_codec.region_builder import build_cube_model
from cube_codec.route_index import build_prefix_index
from cube_codec.cost_model import build_token_cost_model
from cube_codec.stream_codecs import MODE_ENTROPY, decode_mode_stream, encode_mode_stream


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
    return cube, stream


def test_decode_rejects_bad_magic() -> None:
    cube, _ = _simple_case()
    with pytest.raises(ValueError):
        decode_mode_stream(b"BAD!" + b"\x00" * 20, cube)


def test_decode_rejects_corrupt_entropy_payload() -> None:
    cube, stream = _simple_case()
    payload, _ = encode_mode_stream(stream, cube, MODE_ENTROPY)
    bad = payload[:-2]  # truncate
    with pytest.raises(Exception):
        decode_mode_stream(bad, cube)
