from __future__ import annotations

import math
from dataclasses import dataclass

from .bitutils import longest_match
from .config import CodecConfig
from .cost_model import TokenCostModel
from .cube_model import CubeModel
from .route_index import PrefixRouteIndex
from .route_model import EncodedStream, LiteralToken, RouteToken, Token


@dataclass
class EncodeStats:
    candidate_checks: int = 0
    positions_visited: int = 0
    route_tokens: int = 0
    literal_tokens: int = 0
    route_bits_covered: int = 0
    route_match_histogram: dict[int, int] | None = None
    top_region_use: dict[int, int] | None = None
    route_descriptor_use: dict[str, int] | None = None
    per_region_emitted_bits: dict[int, int] | None = None
    per_region_route_cost_sum: dict[int, float] | None = None

    def __post_init__(self) -> None:
        if self.route_match_histogram is None:
            self.route_match_histogram = {}
        if self.top_region_use is None:
            self.top_region_use = {}
        if self.route_descriptor_use is None:
            self.route_descriptor_use = {}
        if self.per_region_emitted_bits is None:
            self.per_region_emitted_bits = {}
        if self.per_region_route_cost_sum is None:
            self.per_region_route_cost_sum = {}


def encode_bits(
    source_bits: str,
    cube: CubeModel,
    index: PrefixRouteIndex,
    config: CodecConfig,
    cost_model: TokenCostModel,
) -> tuple[EncodedStream, EncodeStats]:
    model = cost_model
    n = len(source_bits)
    dp = [math.inf] * (n + 1)
    choice: list[Token | None] = [None] * (n + 1)
    emit_len = [0] * (n + 1)
    stats = EncodeStats()
    dp[n] = 0.0

    region_lookup = {r.region_id: r for r in cube.regions}

    for i in range(n - 1, -1, -1):
        stats.positions_visited += 1
        suffix = source_bits[i:]

        literal_length = min(config.literal_block_bits, n - i)
        literal_bits = source_bits[i : i + literal_length]
        lit_token = LiteralToken(token_type="L", bit_length=literal_length, payload_bits=literal_bits)
        lit_cost = model.literal_cost(lit_token) + dp[i + literal_length]
        best_cost = lit_cost
        best_token: Token = lit_token
        best_emit = literal_length

        candidates = index.query(suffix)
        stats.candidate_checks += len(candidates)
        for candidate in candidates:
            match_len = longest_match(candidate.output_bits, suffix)
            if match_len <= 0:
                continue
            route_token = RouteToken(
                token_type="R",
                region_id=candidate.region_id,
                middle_id=candidate.middle_id,
                suffix_id=candidate.suffix_id,
                emit_length=(match_len if match_len < len(candidate.output_bits) else None),
            )
            cost = model.route_cost(route_token) + dp[i + match_len]
            if cost < best_cost:
                best_cost = cost
                best_token = route_token
                best_emit = match_len

        dp[i] = best_cost
        choice[i] = best_token
        emit_len[i] = best_emit

    tokens: list[Token] = []
    i = 0
    while i < n:
        token = choice[i]
        if token is None:
            raise RuntimeError("DP decode failure: missing choice")
        e = emit_len[i]
        if isinstance(token, RouteToken):
            region = region_lookup[token.region_id]
            route_out = region.prefix_bits + region.middle_variants[token.middle_id] + region.suffix_variants[token.suffix_id]
            matched = token.emit_length if token.emit_length is not None else len(route_out)
            stats.route_tokens += 1
            stats.route_bits_covered += matched
            stats.route_match_histogram[matched] = stats.route_match_histogram.get(matched, 0) + 1
            stats.top_region_use[token.region_id] = stats.top_region_use.get(token.region_id, 0) + 1
            descriptor = f"{token.region_id}:{token.middle_id}:{token.suffix_id}"
            stats.route_descriptor_use[descriptor] = stats.route_descriptor_use.get(descriptor, 0) + 1
            stats.per_region_emitted_bits[token.region_id] = stats.per_region_emitted_bits.get(token.region_id, 0) + matched
            stats.per_region_route_cost_sum[token.region_id] = (
                stats.per_region_route_cost_sum.get(token.region_id, 0.0) + model.route_cost(token)
            )
        else:
            stats.literal_tokens += 1
        tokens.append(token)
        i += e

    return EncodedStream(tokens=tokens, original_bit_length=n), stats
