import pytest

from cube_codec.config import CodecConfig
from cube_codec.cube_model import RegionLayout
from cube_codec.decoder import decode_stream
from cube_codec.encoder import encode_bits
from cube_codec.region_builder import build_cube_model
from cube_codec.route_index import build_prefix_index
from cube_codec.route_model import LiteralToken
from cube_codec.cost_model import build_token_cost_model
from cube_codec.stream_codecs import (
    FLAG_LITERAL_ONLY_STREAM,
    FLAG_TOKEN_ZLIB,
    MODE_ENTROPY,
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


def test_decode_rejects_corrupt_literal_payload() -> None:
    cube, stream = _simple_case()
    # Add a short literal tail to force literal-side payload encoding.
    stream.tokens.append(LiteralToken(token_type="L", bit_length=4, payload_bits="1010"))
    payload, _ = encode_mode_stream(stream, cube, MODE_LOCAL)
    bad = payload[:-1]
    with pytest.raises(Exception):
        decode_mode_stream(bad, cube)


def test_decode_rejects_invalid_token_zlib_flag() -> None:
    cube, stream = _simple_case()
    payload, _ = encode_mode_stream(stream, cube, MODE_LOCAL)
    bad = bytearray(payload)
    bad[13] = bad[13] | FLAG_TOKEN_ZLIB
    with pytest.raises(Exception):
        decode_mode_stream(bytes(bad), cube)


def test_decode_rejects_corrupt_literal_only_payload() -> None:
    cube, stream = _simple_case()
    source_bits = "0101" * 1024
    stream = stream.__class__(tokens=[LiteralToken(token_type="L", bit_length=len(source_bits), payload_bits=source_bits)], original_bit_length=len(source_bits))
    payload, _ = encode_mode_stream(stream, cube, MODE_LOCAL)
    bad = bytearray(payload)
    bad[13] = bad[13] | FLAG_LITERAL_ONLY_STREAM
    bad = bad[:-1]
    with pytest.raises(Exception):
        decode_mode_stream(bytes(bad), cube)
