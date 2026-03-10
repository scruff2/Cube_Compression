from __future__ import annotations

from dataclasses import dataclass

from .cube_model import CubeModel, reconstruct_route


@dataclass
class RouteCandidate:
    region_id: int
    middle_id: int
    suffix_id: int
    output_bits: str


class PrefixRouteIndex:
    def __init__(self, prefix_bits: int) -> None:
        self.prefix_bits = prefix_bits
        self._index: dict[str, list[RouteCandidate]] = {}

    def add(self, candidate: RouteCandidate) -> None:
        key = candidate.output_bits[: self.prefix_bits]
        self._index.setdefault(key, []).append(candidate)

    def query(self, source_bits: str) -> list[RouteCandidate]:
        key = source_bits[: self.prefix_bits]
        return self._index.get(key, [])

    def size(self) -> int:
        return sum(len(v) for v in self._index.values())


def build_prefix_index(cube: CubeModel, prefix_bits: int) -> PrefixRouteIndex:
    index = PrefixRouteIndex(prefix_bits=prefix_bits)
    for region in cube.regions:
        for mid in range(len(region.middle_variants)):
            for suf in range(len(region.suffix_variants)):
                output_bits = reconstruct_route(region, mid, suf)
                index.add(RouteCandidate(region.region_id, mid, suf, output_bits))
    return index
