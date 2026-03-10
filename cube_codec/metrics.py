from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CompressionMetrics:
    original_bits: int
    compressed_bits: int
    compression_ratio: float
    bits_per_source_bit: float


@dataclass
class CoverageMetrics:
    route_bit_fraction: float
    avg_route_length: float
    unique_routes_used: int
    routes_per_message: float


@dataclass
class SearchMetrics:
    avg_candidates_per_position: float
    index_size: int


def compute_compression_metrics(original_bits: int, compressed_bits: int) -> CompressionMetrics:
    ratio = (float(original_bits) / float(compressed_bits)) if compressed_bits else 0.0
    bps = (float(compressed_bits) / float(original_bits)) if original_bits else 0.0
    return CompressionMetrics(
        original_bits=original_bits,
        compressed_bits=compressed_bits,
        compression_ratio=ratio,
        bits_per_source_bit=bps,
    )
