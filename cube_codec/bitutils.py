from __future__ import annotations

from pathlib import Path


def bytes_to_bits(data: bytes) -> str:
    return "".join(f"{b:08b}" for b in data)


def bits_to_bytes(bits: str) -> bytes:
    if not bits:
        return b""
    pad = (-len(bits)) % 8
    padded = bits + ("0" * pad)
    out = bytearray()
    for i in range(0, len(padded), 8):
        out.append(int(padded[i : i + 8], 2))
    return bytes(out)


def read_bits_file(path: str | Path) -> str:
    return bytes_to_bits(Path(path).read_bytes())


def write_bits_file(path: str | Path, bits: str, exact_bit_length: int | None = None) -> None:
    payload = bits
    if exact_bit_length is not None:
        payload = bits[:exact_bit_length]
    Path(path).write_bytes(bits_to_bytes(payload))


def bit_prefix(s: str, n: int) -> str:
    if n <= 0:
        return ""
    return s[:n]


def longest_match(a: str, b: str) -> int:
    m = min(len(a), len(b))
    i = 0
    while i < m and a[i] == b[i]:
        i += 1
    return i
