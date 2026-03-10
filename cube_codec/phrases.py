from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass
class PhraseExtractionResult:
    phrase_counts: dict[str, int]
    extracted_count: int
    unique_count: int


def extract_phrases(
    bits: str,
    phrase_length: int,
    stride: int,
    min_frequency: int,
    max_extracted_phrases: int | None = None,
) -> PhraseExtractionResult:
    if phrase_length <= 0 or stride <= 0:
        raise ValueError("phrase_length and stride must be positive")
    counts: Counter[str] = Counter()
    extracted = 0
    for i in range(0, max(0, len(bits) - phrase_length + 1), stride):
        if max_extracted_phrases is not None and extracted >= max_extracted_phrases:
            break
        phrase = bits[i : i + phrase_length]
        if len(phrase) == phrase_length:
            counts[phrase] += 1
            extracted += 1

    filtered = {k: v for k, v in counts.items() if v >= min_frequency}
    return PhraseExtractionResult(
        phrase_counts=filtered,
        extracted_count=extracted,
        unique_count=len(filtered),
    )


def select_top_phrases(phrase_counts: dict[str, int], top_n: int) -> list[tuple[str, int]]:
    ordered = sorted(phrase_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return ordered[:top_n]
