from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .clustering import cluster_phrases_by_prefix
from .config import CodecConfig
from .cube_model import CubeMetadata, CubeModel, RegionLayout


@dataclass
class RegionBuildStats:
    selected_phrase_count: int
    cluster_count: int


def _split_lengths(phrase_length: int) -> tuple[int, int, int]:
    prefix = phrase_length // 2
    middle = phrase_length // 4
    suffix = phrase_length - prefix - middle
    return prefix, middle, suffix


def build_regions_from_phrases(selected_phrases: list[str], config: CodecConfig) -> tuple[list[RegionLayout], RegionBuildStats]:
    prefix_length, middle_length, suffix_length = _split_lengths(config.phrase_length)
    clusters = cluster_phrases_by_prefix(selected_phrases, prefix_length, middle_length, suffix_length)

    regions: list[RegionLayout] = []
    for idx, cluster in enumerate(clusters[: config.max_regions]):
        middle_counts: Counter[str] = Counter()
        suffix_counts: Counter[str] = Counter()
        for phrase in cluster.phrases:
            middle = phrase[prefix_length : prefix_length + middle_length]
            suffix = phrase[prefix_length + middle_length : prefix_length + middle_length + suffix_length]
            middle_counts[middle] += 1
            suffix_counts[suffix] += 1

        middle_variants = [m for m, _ in middle_counts.most_common(config.max_middle_variants)]
        suffix_variants = [s for s, _ in suffix_counts.most_common(config.max_suffix_variants)]
        if not middle_variants or not suffix_variants:
            continue

        route_length = len(cluster.prefix_bits) + len(middle_variants[0]) + len(suffix_variants[0])
        regions.append(
            RegionLayout(
                region_id=idx,
                prefix_bits=cluster.prefix_bits,
                middle_variants=middle_variants,
                suffix_variants=suffix_variants,
                route_length=route_length,
                prefix_length=prefix_length,
                middle_length=middle_length,
                suffix_length=suffix_length,
            )
        )

    stats = RegionBuildStats(selected_phrase_count=len(selected_phrases), cluster_count=len(clusters))
    return regions, stats


def build_cube_model(regions: list[RegionLayout], config: CodecConfig) -> CubeModel:
    lanes = 1 + config.max_middle_variants + config.max_suffix_variants
    metadata = CubeMetadata(
        version="0.1.0",
        region_count=len(regions),
        lanes_per_region=lanes,
        positions_per_lane=config.phrase_length,
        phrase_length=config.phrase_length,
        middle_variants_per_region=config.max_middle_variants,
        suffix_variants_per_region=config.max_suffix_variants,
    )
    return CubeModel(metadata=metadata, regions=regions)
