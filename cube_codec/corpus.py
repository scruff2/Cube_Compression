from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .bitutils import bytes_to_bits


@dataclass
class CorpusStats:
    file_count: int
    total_bytes: int
    total_bits: int


def load_corpus_bits(paths: list[str | Path]) -> tuple[str, CorpusStats]:
    chunks: list[bytes] = []
    total = 0
    for path in paths:
        data = Path(path).read_bytes()
        chunks.append(data)
        total += len(data)
    merged = b"".join(chunks)
    bits = bytes_to_bits(merged)
    return bits, CorpusStats(file_count=len(paths), total_bytes=total, total_bits=len(bits))
