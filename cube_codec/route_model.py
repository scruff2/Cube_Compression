from __future__ import annotations

import json
import struct
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

TOKEN_LITERAL = 0
TOKEN_ROUTE = 1
MAGIC = b"CRCS1"


@dataclass
class LiteralToken:
    token_type: str
    bit_length: int
    payload_bits: str


@dataclass
class RouteToken:
    token_type: str
    region_id: int
    middle_id: int
    suffix_id: int
    emit_length: Optional[int] = None


Token = LiteralToken | RouteToken


@dataclass
class EncodedStream:
    tokens: list[Token]
    original_bit_length: int

    def to_debug_dict(self) -> dict:
        serialized = []
        for token in self.tokens:
            serialized.append(asdict(token))
        return {"original_bit_length": self.original_bit_length, "tokens": serialized}

    @classmethod
    def from_debug_dict(cls, data: dict) -> "EncodedStream":
        tokens: list[Token] = []
        for item in data["tokens"]:
            if item["token_type"] == "L":
                tokens.append(LiteralToken(**item))
            else:
                tokens.append(RouteToken(**item))
        return cls(tokens=tokens, original_bit_length=int(data["original_bit_length"]))


def save_debug_stream(path: str | Path, stream: EncodedStream) -> None:
    Path(path).write_text(json.dumps(stream.to_debug_dict(), indent=2), encoding="utf-8")


def load_debug_stream(path: str | Path) -> EncodedStream:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return EncodedStream.from_debug_dict(data)


def save_binary_stream(path: str | Path, stream: EncodedStream) -> None:
    out = bytearray()
    out += MAGIC
    out += struct.pack("<Q", stream.original_bit_length)
    out += struct.pack("<I", len(stream.tokens))
    for token in stream.tokens:
        if isinstance(token, LiteralToken):
            out += bytes([TOKEN_LITERAL])
            payload_bytes = token.payload_bits.encode("ascii")
            out += struct.pack("<I", token.bit_length)
            out += struct.pack("<I", len(payload_bytes))
            out += payload_bytes
        else:
            out += bytes([TOKEN_ROUTE])
            emit_len = token.emit_length if token.emit_length is not None else 0
            out += struct.pack("<IHHI", token.region_id, token.middle_id, token.suffix_id, emit_len)
    Path(path).write_bytes(bytes(out))


def load_binary_stream(path: str | Path) -> EncodedStream:
    data = memoryview(Path(path).read_bytes())
    off = 0
    magic = bytes(data[off : off + 5])
    if magic != MAGIC:
        raise ValueError("invalid encoded stream magic")
    off += 5
    (original_bit_length,) = struct.unpack_from("<Q", data, off)
    off += 8
    (token_count,) = struct.unpack_from("<I", data, off)
    off += 4

    tokens: list[Token] = []
    for _ in range(token_count):
        token_type = int(data[off])
        off += 1
        if token_type == TOKEN_LITERAL:
            bit_length, payload_len = struct.unpack_from("<II", data, off)
            off += 8
            payload_bits = bytes(data[off : off + payload_len]).decode("ascii")
            off += payload_len
            tokens.append(LiteralToken(token_type="L", bit_length=bit_length, payload_bits=payload_bits))
        elif token_type == TOKEN_ROUTE:
            region_id, middle_id, suffix_id, emit_len = struct.unpack_from("<IHHI", data, off)
            off += 12
            tokens.append(
                RouteToken(
                    token_type="R",
                    region_id=region_id,
                    middle_id=middle_id,
                    suffix_id=suffix_id,
                    emit_length=(emit_len if emit_len > 0 else None),
                )
            )
        else:
            raise ValueError(f"unknown token type: {token_type}")

    return EncodedStream(tokens=tokens, original_bit_length=int(original_bit_length))
