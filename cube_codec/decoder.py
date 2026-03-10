from __future__ import annotations

from .cube_model import CubeModel, reconstruct_route
from .route_model import EncodedStream, LiteralToken, RouteToken


def decode_stream(stream: EncodedStream, cube: CubeModel) -> str:
    regions = {r.region_id: r for r in cube.regions}
    out: list[str] = []
    for token in stream.tokens:
        if isinstance(token, LiteralToken):
            out.append(token.payload_bits[: token.bit_length])
        elif isinstance(token, RouteToken):
            region = regions[token.region_id]
            bits = reconstruct_route(region, token.middle_id, token.suffix_id, token.emit_length)
            out.append(bits)
        else:
            raise TypeError("unknown token class")
    joined = "".join(out)
    return joined[: stream.original_bit_length]
