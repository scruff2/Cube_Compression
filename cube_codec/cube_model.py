from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class RegionLayout:
    region_id: int
    prefix_bits: str
    middle_variants: list[str]
    suffix_variants: list[str]
    route_length: int
    prefix_length: int
    middle_length: int
    suffix_length: int


@dataclass
class CubeMetadata:
    version: str
    region_count: int
    lanes_per_region: int
    positions_per_lane: int
    phrase_length: int
    middle_variants_per_region: int
    suffix_variants_per_region: int


@dataclass
class CubeModel:
    metadata: CubeMetadata
    regions: list[RegionLayout]

    def to_dict(self) -> dict:
        return {
            "metadata": asdict(self.metadata),
            "regions": [asdict(region) for region in self.regions],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CubeModel":
        metadata = CubeMetadata(**data["metadata"])
        regions = [RegionLayout(**x) for x in data["regions"]]
        return cls(metadata=metadata, regions=regions)


def reconstruct_route(region: RegionLayout, middle_id: int, suffix_id: int, emit_length: int | None = None) -> str:
    if middle_id < 0 or middle_id >= len(region.middle_variants):
        raise IndexError("middle_id out of bounds")
    if suffix_id < 0 or suffix_id >= len(region.suffix_variants):
        raise IndexError("suffix_id out of bounds")

    output = region.prefix_bits + region.middle_variants[middle_id] + region.suffix_variants[suffix_id]
    if emit_length is not None:
        return output[:emit_length]
    return output
