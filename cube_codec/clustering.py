from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PhraseCluster:
    prefix_bits: str
    phrases: list[str]
    middle_length: int
    suffix_length: int


def cluster_phrases_by_prefix(
    phrases: list[str],
    prefix_length: int,
    middle_length: int,
    suffix_length: int,
) -> list[PhraseCluster]:
    groups: dict[str, list[str]] = {}
    for phrase in phrases:
        pfx = phrase[:prefix_length]
        groups.setdefault(pfx, []).append(phrase)

    clusters = [
        PhraseCluster(prefix_bits=pfx, phrases=sorted(items), middle_length=middle_length, suffix_length=suffix_length)
        for pfx, items in groups.items()
    ]
    clusters.sort(key=lambda c: (-len(c.phrases), c.prefix_bits))
    return clusters
