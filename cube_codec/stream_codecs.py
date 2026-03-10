from __future__ import annotations

import heapq
import struct
import zlib
from collections import Counter

from .bitutils import bits_to_bytes, bytes_to_bits
from .cube_model import CubeModel, reconstruct_route
from .route_model import EncodedStream, LiteralToken, RouteToken

MAGIC = b"CCM2"
MAGIC_LITERAL = b"CCL1"
MAGIC_CHUNKED = b"CCM3"
FLAG_ROUTE_ONLY = 1
FLAG_LITERAL_ZLIB = 2
FLAG_FRAMED_PAYLOAD = 4
FLAG_TOKEN_ZLIB = 8
FLAG_LITERAL_ONLY_STREAM = 16

MODE_LEGACY = "cube_actual_legacy"
MODE_FIXED = "cube_fixed_length_actual"
MODE_LOCAL = "cube_family_local_id_actual"
MODE_ENTROPY = "cube_entropy_coded_actual"

MODE_IDS = {
    MODE_LEGACY: 0,
    MODE_FIXED: 1,
    MODE_LOCAL: 2,
    MODE_ENTROPY: 3,
}
ID_TO_MODE = {v: k for k, v in MODE_IDS.items()}


class BitWriter:
    def __init__(self) -> None:
        self.bits: list[str] = []

    def write_bits(self, value: int, width: int) -> None:
        if width <= 0:
            return
        self.bits.append(f"{value:0{width}b}")

    def write_bitstring(self, bits: str) -> None:
        if bits:
            self.bits.append(bits)

    def to_bytes(self) -> bytes:
        bitstring = "".join(self.bits)
        bitstring += "0" * ((-len(bitstring)) % 8)
        out = bytearray()
        for i in range(0, len(bitstring), 8):
            out.append(int(bitstring[i : i + 8], 2))
        return bytes(out)


class BitReader:
    def __init__(self, data: bytes) -> None:
        self.bits = "".join(f"{b:08b}" for b in data)
        self.pos = 0

    def read_bits(self, width: int) -> int:
        if width <= 0:
            return 0
        val = int(self.bits[self.pos : self.pos + width], 2)
        self.pos += width
        return val

    def read_bitstring(self, width: int) -> str:
        out = self.bits[self.pos : self.pos + width]
        self.pos += width
        return out

    def eof(self) -> bool:
        return self.pos >= len(self.bits)


def _bit_width(n: int) -> int:
    if n <= 1:
        return 0
    import math

    return int(math.ceil(math.log2(n)))


def _route_widths(cube: CubeModel) -> tuple[int, int, int]:
    region_bits = _bit_width(len(cube.regions))
    middle_max = max((len(r.middle_variants) for r in cube.regions), default=1)
    suffix_max = max((len(r.suffix_variants) for r in cube.regions), default=1)
    return region_bits, _bit_width(middle_max), _bit_width(suffix_max)


def _full_route_stream(stream: EncodedStream, cube: CubeModel) -> EncodedStream:
    regions = {r.region_id: r for r in cube.regions}
    tokens = []
    for token in stream.tokens:
        if isinstance(token, LiteralToken):
            tokens.append(token)
            continue
        if token.emit_length is None:
            tokens.append(token)
            continue
        region = regions[token.region_id]
        payload = reconstruct_route(region, token.middle_id, token.suffix_id, token.emit_length)
        tokens.append(LiteralToken(token_type="L", bit_length=len(payload), payload_bits=payload))
    return EncodedStream(tokens=tokens, original_bit_length=stream.original_bit_length)


def _local_maps(cube: CubeModel) -> tuple[dict[int, dict[tuple[int, int], int]], dict[int, list[tuple[int, int]]], dict[int, int]]:
    forward: dict[int, dict[tuple[int, int], int]] = {}
    reverse: dict[int, list[tuple[int, int]]] = {}
    widths: dict[int, int] = {}
    for region in cube.regions:
        pairs = [(m, s) for m in range(len(region.middle_variants)) for s in range(len(region.suffix_variants))]
        pairs.sort()
        reverse[region.region_id] = pairs
        forward[region.region_id] = {pair: i for i, pair in enumerate(pairs)}
        widths[region.region_id] = _bit_width(len(pairs))
    return forward, reverse, widths


def _build_huffman(symbol_freq: Counter[tuple[int, int, int]]) -> dict[tuple[int, int, int], str]:
    if not symbol_freq:
        return {}
    if len(symbol_freq) == 1:
        sym = next(iter(symbol_freq))
        return {sym: "0"}
    heap: list[tuple[int, int, object]] = []
    order = 0
    for sym, freq in symbol_freq.items():
        heapq.heappush(heap, (freq, order, sym))
        order += 1
    while len(heap) > 1:
        f1, _, n1 = heapq.heappop(heap)
        f2, _, n2 = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, order, (n1, n2)))
        order += 1
    tree = heap[0][2]
    codes: dict[tuple[int, int, int], str] = {}

    def walk(node: object, prefix: str) -> None:
        if isinstance(node, tuple) and len(node) == 3 and all(isinstance(x, int) for x in node):
            codes[node] = prefix
            return
        left, right = node  # type: ignore[misc]
        walk(left, prefix + "0")
        walk(right, prefix + "1")

    walk(tree, "")
    return codes


def _canonical_from_lengths(lengths: dict[tuple[int, int, int], int]) -> dict[tuple[int, int, int], str]:
    items = sorted(lengths.items(), key=lambda kv: (kv[1], kv[0]))
    codes: dict[tuple[int, int, int], str] = {}
    code = 0
    prev_len = items[0][1] if items else 0
    for sym, length in items:
        if length > prev_len:
            code <<= (length - prev_len)
            prev_len = length
        codes[sym] = f"{code:0{length}b}" if length > 0 else ""
        code += 1
    return codes


def _encode_legacy(stream: EncodedStream, cube: CubeModel) -> bytes:
    writer = BitWriter()
    r_bits, m_bits, s_bits = _route_widths(cube)
    for token in stream.tokens:
        if isinstance(token, LiteralToken):
            writer.write_bits(0, 1)
            writer.write_bits(token.bit_length, 8)
            writer.write_bitstring(token.payload_bits[: token.bit_length])
        else:
            writer.write_bits(1, 1)
            writer.write_bits(token.region_id, r_bits)
            writer.write_bits(token.middle_id, m_bits)
            writer.write_bits(token.suffix_id, s_bits)
            emit = token.emit_length if token.emit_length is not None else 0
            writer.write_bits(emit, 8)
    return writer.to_bytes()


def _decode_legacy(payload: bytes, token_count: int, original_bit_length: int, cube: CubeModel) -> EncodedStream:
    reader = BitReader(payload)
    r_bits, m_bits, s_bits = _route_widths(cube)
    tokens = []
    for _ in range(token_count):
        t = reader.read_bits(1)
        if t == 0:
            n = reader.read_bits(8)
            bits = reader.read_bitstring(n)
            tokens.append(LiteralToken(token_type="L", bit_length=n, payload_bits=bits))
        else:
            region = reader.read_bits(r_bits)
            mid = reader.read_bits(m_bits)
            suf = reader.read_bits(s_bits)
            emit = reader.read_bits(8)
            tokens.append(RouteToken(token_type="R", region_id=region, middle_id=mid, suffix_id=suf, emit_length=(emit if emit > 0 else None)))
    return EncodedStream(tokens=tokens, original_bit_length=original_bit_length)


def _encode_fixed(stream: EncodedStream, cube: CubeModel) -> tuple[bytes, EncodedStream, bool, dict]:
    fixed_stream = _full_route_stream(stream, cube)
    route_only = all(isinstance(t, RouteToken) for t in fixed_stream.tokens)
    writer = BitWriter()
    literal_writer = BitWriter()
    r_bits, m_bits, s_bits = _route_widths(cube)
    literal_count = 0
    for token in fixed_stream.tokens:
        if isinstance(token, LiteralToken):
            writer.write_bits(0, 1)
            writer.write_bits(token.bit_length, 8)
            literal_writer.write_bitstring(token.payload_bits[: token.bit_length])
            literal_count += 1
        else:
            if not route_only:
                writer.write_bits(1, 1)
            writer.write_bits(token.region_id, r_bits)
            writer.write_bits(token.middle_id, m_bits)
            writer.write_bits(token.suffix_id, s_bits)
    payload, frame_diag = _build_framed_payload(writer.to_bytes(), literal_writer, literal_count)
    return payload, fixed_stream, route_only, frame_diag


def _decode_fixed(payload: bytes, token_count: int, original_bit_length: int, cube: CubeModel, route_only: bool, flags: int) -> EncodedStream:
    token_payload, literal_source = _decode_framed_payload(payload, flags)
    reader = BitReader(token_payload)
    r_bits, m_bits, s_bits = _route_widths(cube)
    tokens = []
    for _ in range(token_count):
        if route_only:
            tokens.append(RouteToken(token_type="R", region_id=reader.read_bits(r_bits), middle_id=reader.read_bits(m_bits), suffix_id=reader.read_bits(s_bits), emit_length=None))
            continue
        t = reader.read_bits(1)
        if t == 0:
            n = reader.read_bits(8)
            bits = literal_source.read(n) if literal_source is not None else reader.read_bitstring(n)
            tokens.append(LiteralToken(token_type="L", bit_length=n, payload_bits=bits))
        else:
            tokens.append(RouteToken(token_type="R", region_id=reader.read_bits(r_bits), middle_id=reader.read_bits(m_bits), suffix_id=reader.read_bits(s_bits), emit_length=None))
    if literal_source is not None:
        literal_source.ensure_exhausted()
    return EncodedStream(tokens=tokens, original_bit_length=original_bit_length)


def _encode_local(stream: EncodedStream, cube: CubeModel) -> tuple[bytes, EncodedStream, dict, bool]:
    local_stream = _full_route_stream(stream, cube)
    route_only = all(isinstance(t, RouteToken) for t in local_stream.tokens)
    writer = BitWriter()
    literal_writer = BitWriter()
    r_bits, _, _ = _route_widths(cube)
    forward, _, widths = _local_maps(cube)
    literal_count = 0
    for token in local_stream.tokens:
        if isinstance(token, LiteralToken):
            writer.write_bits(0, 1)
            writer.write_bits(token.bit_length, 8)
            literal_writer.write_bitstring(token.payload_bits[: token.bit_length])
            literal_count += 1
        else:
            if not route_only:
                writer.write_bits(1, 1)
            writer.write_bits(token.region_id, r_bits)
            local_id = forward[token.region_id][(token.middle_id, token.suffix_id)]
            writer.write_bits(local_id, widths[token.region_id])
    payload, frame_diag = _build_framed_payload(writer.to_bytes(), literal_writer, literal_count)
    diagnostics = {
        "region_id_width": r_bits,
        "local_route_table_size_per_region": {str(k): len(v) for k, v in forward.items()},
        "max_local_id_width": max(widths.values()) if widths else 0,
        "avg_local_id_width": (sum(widths.values()) / max(1, len(widths))),
        "literal_count": literal_count,
        "token_payload_zlib": frame_diag["token_payload_zlib"],
    }
    return payload, local_stream, diagnostics, route_only


def _decode_local(payload: bytes, token_count: int, original_bit_length: int, cube: CubeModel, route_only: bool, flags: int) -> EncodedStream:
    token_payload, literal_source = _decode_framed_payload(payload, flags)
    reader = BitReader(token_payload)
    r_bits, _, _ = _route_widths(cube)
    _, reverse, widths = _local_maps(cube)
    tokens = []
    for _ in range(token_count):
        if route_only:
            region = reader.read_bits(r_bits)
            local_id = reader.read_bits(widths[region])
            mid, suf = reverse[region][local_id]
            tokens.append(RouteToken(token_type="R", region_id=region, middle_id=mid, suffix_id=suf, emit_length=None))
            continue
        t = reader.read_bits(1)
        if t == 0:
            n = reader.read_bits(8)
            bits = literal_source.read(n) if literal_source is not None else reader.read_bitstring(n)
            tokens.append(LiteralToken(token_type="L", bit_length=n, payload_bits=bits))
        else:
            region = reader.read_bits(r_bits)
            local_id = reader.read_bits(widths[region])
            mid, suf = reverse[region][local_id]
            tokens.append(RouteToken(token_type="R", region_id=region, middle_id=mid, suffix_id=suf, emit_length=None))
    if literal_source is not None:
        literal_source.ensure_exhausted()
    return EncodedStream(tokens=tokens, original_bit_length=original_bit_length)


def _encode_entropy(stream: EncodedStream, cube: CubeModel) -> tuple[bytes, EncodedStream, dict, bool]:
    entropy_stream = _full_route_stream(stream, cube)
    route_only = all(isinstance(t, RouteToken) for t in entropy_stream.tokens)
    route_freq = Counter((t.region_id, t.middle_id, t.suffix_id) for t in entropy_stream.tokens if isinstance(t, RouteToken))
    raw_codes = _build_huffman(route_freq)
    lengths = {sym: len(code) if len(code) > 0 else 1 for sym, code in raw_codes.items()}
    codes = _canonical_from_lengths(lengths)

    writer = BitWriter()
    literal_writer = BitWriter()
    literal_count = 0
    for token in entropy_stream.tokens:
        if isinstance(token, LiteralToken):
            writer.write_bits(0, 1)
            writer.write_bits(token.bit_length, 8)
            literal_writer.write_bitstring(token.payload_bits[: token.bit_length])
            literal_count += 1
        else:
            if not route_only:
                writer.write_bits(1, 1)
            writer.write_bitstring(codes[(token.region_id, token.middle_id, token.suffix_id)])

    table = bytearray()
    table += struct.pack("<H", len(codes))
    for sym in sorted(codes):
        r, m, s = sym
        table += struct.pack("<HHHB", r, m, s, lengths[sym])
    framed_payload, frame_diag = _build_framed_payload(writer.to_bytes(), literal_writer, literal_count)
    payload = bytes(table) + framed_payload

    entropy = 0.0
    total = sum(route_freq.values())
    for c in route_freq.values():
        p = c / max(1, total)
        import math

        entropy -= p * math.log2(p)
    diagnostics = {
        "coding_model": "whole_route_huffman_static_canonical",
        "symbol_alphabet_size": len(codes),
        "estimated_entropy_bits_per_route": entropy,
        "actual_coded_bits": len(payload) * 8,
        "literal_count": literal_count,
        "token_payload_zlib": frame_diag["token_payload_zlib"],
    }
    return payload, entropy_stream, diagnostics, route_only


def _decode_entropy(payload: bytes, token_count: int, original_bit_length: int, cube: CubeModel, route_only: bool, flags: int) -> EncodedStream:
    _ = cube
    mv = memoryview(payload)
    off = 0
    (n_codes,) = struct.unpack_from("<H", mv, off)
    off += 2
    lengths: dict[tuple[int, int, int], int] = {}
    for _i in range(n_codes):
        r, m, s, n = struct.unpack_from("<HHHB", mv, off)
        off += 7
        lengths[(r, m, s)] = n
    code_to_sym = {code: sym for sym, code in _canonical_from_lengths(lengths).items()}
    token_payload, literal_source = _decode_framed_payload(bytes(mv[off:]), flags)
    reader = BitReader(token_payload)
    tokens = []
    for _i in range(token_count):
        if not route_only:
            t = reader.read_bits(1)
            if t == 0:
                n = reader.read_bits(8)
                bits = literal_source.read(n) if literal_source is not None else reader.read_bitstring(n)
                tokens.append(LiteralToken(token_type="L", bit_length=n, payload_bits=bits))
                continue
        code = ""
        while code not in code_to_sym:
            if reader.eof():
                raise ValueError("corrupt entropy payload")
            code += str(reader.read_bits(1))
        r, m, s = code_to_sym[code]
        tokens.append(RouteToken(token_type="R", region_id=r, middle_id=m, suffix_id=s, emit_length=None))
    if literal_source is not None:
        literal_source.ensure_exhausted()
    return EncodedStream(tokens=tokens, original_bit_length=original_bit_length)


class _LiteralSource:
    def __init__(self, bits: str) -> None:
        self.bits = bits
        self.pos = 0

    def read(self, n: int) -> str:
        out = self.bits[self.pos : self.pos + n]
        if len(out) != n:
            raise ValueError("corrupt literal payload")
        self.pos += n
        return out

    def ensure_exhausted(self) -> None:
        if self.pos != len(self.bits):
            raise ValueError("unused literal payload bits")


def _build_framed_payload(token_payload: bytes, literal_writer: BitWriter, literal_count: int) -> tuple[bytes, dict]:
    token_blob = token_payload
    token_payload_zlib = False
    token_compressed = zlib.compress(token_payload)
    if len(token_compressed) < len(token_payload):
        token_blob = token_compressed
        token_payload_zlib = True
    literal_bits = "".join(literal_writer.bits)
    if literal_count == 0:
        payload = struct.pack("<II", len(token_blob), 0) + token_blob
        return payload, {"token_payload_zlib": token_payload_zlib, "literal_payload_zlib": False}
    literal_bytes = literal_writer.to_bytes()
    literal_blob = struct.pack("<I", len(literal_bits)) + zlib.compress(literal_bytes)
    payload = struct.pack("<II", len(token_blob), len(literal_blob)) + token_blob + literal_blob
    return payload, {"token_payload_zlib": token_payload_zlib, "literal_payload_zlib": True}


def _decode_framed_payload(payload: bytes, flags: int) -> tuple[bytes, _LiteralSource | None]:
    if not (flags & FLAG_FRAMED_PAYLOAD):
        return payload, None
    mv = memoryview(payload)
    if len(mv) < 8:
        raise ValueError("corrupt framed payload")
    token_len, literal_len = struct.unpack_from("<II", mv, 0)
    if token_len + literal_len + 8 != len(mv):
        raise ValueError("corrupt framed payload sizes")
    off = 8
    token_blob = bytes(mv[off : off + token_len])
    off += token_len
    if flags & FLAG_TOKEN_ZLIB:
        try:
            token_payload = zlib.decompress(token_blob)
        except Exception as exc:
            raise ValueError("corrupt token payload") from exc
    else:
        token_payload = token_blob
    if literal_len == 0:
        return token_payload, None
    literal_blob = bytes(mv[off : off + literal_len])
    if len(literal_blob) < 4:
        raise ValueError("corrupt literal payload")
    bit_len = struct.unpack_from("<I", literal_blob, 0)[0]
    try:
        raw = zlib.decompress(literal_blob[4:])
    except Exception as exc:
        raise ValueError("corrupt literal payload") from exc
    literal_bits = "".join(f"{b:08b}" for b in raw)
    if bit_len > len(literal_bits):
        raise ValueError("corrupt literal payload")
    return token_payload, _LiteralSource(literal_bits[:bit_len])


def _encode_varint(n: int) -> bytes:
    out = bytearray()
    x = n
    while True:
        b = x & 0x7F
        x >>= 7
        if x:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def _decode_varint(data: memoryview, off: int) -> tuple[int, int]:
    shift = 0
    value = 0
    while True:
        if off >= len(data):
            raise ValueError("corrupt varint")
        b = int(data[off])
        off += 1
        value |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            return value, off
        shift += 7
        if shift > 28:
            raise ValueError("corrupt varint")


def _build_literal_stream_payload(stream: EncodedStream, cube: CubeModel) -> tuple[bytes, int]:
    regions = {r.region_id: r for r in cube.regions}
    chunks: list[str] = []
    for token in stream.tokens:
        if isinstance(token, LiteralToken):
            chunks.append(token.payload_bits[: token.bit_length])
        else:
            region = regions[token.region_id]
            emit_len = token.emit_length if token.emit_length is not None else region.route_length
            chunks.append(reconstruct_route(region, token.middle_id, token.suffix_id, emit_len))
    bits = "".join(chunks)
    raw = bits_to_bytes(bits)
    zlib_payload = zlib.compress(raw)
    raw_payload = raw
    raw_co = zlib.compressobj(level=9, wbits=-15)
    raw_deflate = raw_co.compress(raw) + raw_co.flush()
    candidates = [(len(zlib_payload), 1, zlib_payload), (len(raw_deflate), 0, raw_deflate), (len(raw_payload), 2, raw_payload)]
    _, method, payload = min(candidates, key=lambda t: t[0])
    return payload, method


def _decode_literal_stream_payload(payload: bytes, original_bit_length: int, method: int) -> EncodedStream:
    if method == 1:
        try:
            raw = zlib.decompress(payload)
        except Exception as exc:
            raise ValueError("corrupt literal-only payload") from exc
    elif method == 0:
        try:
            raw = zlib.decompress(payload, wbits=-15)
        except Exception as exc:
            raise ValueError("corrupt literal-only payload") from exc
    elif method == 2:
        raw = payload
    else:
        raise ValueError("unsupported literal-only method")
    bits = bytes_to_bits(raw)
    if original_bit_length > len(bits):
        raise ValueError("corrupt literal-only payload length")
    out_bits = bits[:original_bit_length]
    return EncodedStream(tokens=[LiteralToken(token_type="L", bit_length=original_bit_length, payload_bits=out_bits)], original_bit_length=original_bit_length)


def _token_emitted_bits(token: LiteralToken | RouteToken, cube: CubeModel) -> int:
    if isinstance(token, LiteralToken):
        return token.bit_length
    if token.emit_length is not None:
        return token.emit_length
    region = cube.regions[token.region_id]
    return region.route_length


def _split_tokens_by_emitted_bits(tokens: list[LiteralToken | RouteToken], cube: CubeModel, target_bits: int = 524288) -> list[list[LiteralToken | RouteToken]]:
    chunks: list[list[LiteralToken | RouteToken]] = []
    cur: list[LiteralToken | RouteToken] = []
    cur_bits = 0
    for t in tokens:
        b = _token_emitted_bits(t, cube)
        if cur and cur_bits + b > target_bits:
            chunks.append(cur)
            cur = []
            cur_bits = 0
        cur.append(t)
        cur_bits += b
    if cur:
        chunks.append(cur)
    return chunks


def _encode_route_chunk_for_mode(mode: str, chunk_stream: EncodedStream, cube: CubeModel) -> tuple[bytes, int, int]:
    if mode == MODE_FIXED:
        payload, normalized, route_only, frame_diag = _encode_fixed(chunk_stream, cube)
        flags = FLAG_FRAMED_PAYLOAD
        if route_only:
            flags |= FLAG_ROUTE_ONLY
        if frame_diag.get("token_payload_zlib"):
            flags |= FLAG_TOKEN_ZLIB
        if any(isinstance(t, LiteralToken) for t in normalized.tokens):
            flags |= FLAG_LITERAL_ZLIB
        return payload, flags, len(normalized.tokens)
    if mode == MODE_LOCAL:
        payload, normalized, diag, route_only = _encode_local(chunk_stream, cube)
        flags = FLAG_FRAMED_PAYLOAD
        if route_only:
            flags |= FLAG_ROUTE_ONLY
        if diag.get("token_payload_zlib"):
            flags |= FLAG_TOKEN_ZLIB
        if any(isinstance(t, LiteralToken) for t in normalized.tokens):
            flags |= FLAG_LITERAL_ZLIB
        return payload, flags, len(normalized.tokens)
    payload, normalized, diag, route_only = _encode_entropy(chunk_stream, cube)
    flags = FLAG_FRAMED_PAYLOAD
    if route_only:
        flags |= FLAG_ROUTE_ONLY
    if diag.get("token_payload_zlib"):
        flags |= FLAG_TOKEN_ZLIB
    if any(isinstance(t, LiteralToken) for t in normalized.tokens):
        flags |= FLAG_LITERAL_ZLIB
    return payload, flags, len(normalized.tokens)


def _encode_chunked_hybrid(stream: EncodedStream, cube: CubeModel, mode: str) -> tuple[bytes, dict]:
    normalized = _full_route_stream(stream, cube)
    chunks = _split_tokens_by_emitted_bits(normalized.tokens, cube, target_bits=524288)
    out = bytearray()
    out += MAGIC_CHUNKED
    out += struct.pack("<BI", MODE_IDS[mode], normalized.original_bit_length)
    out += _encode_varint(len(chunks))

    route_chunks = 0
    literal_chunks = 0
    for tokens in chunks:
        chunk_bits = sum(_token_emitted_bits(t, cube) for t in tokens)
        chunk_stream = EncodedStream(tokens=tokens, original_bit_length=chunk_bits)

        route_payload, route_flags, route_token_count = _encode_route_chunk_for_mode(mode, chunk_stream, cube)
        route_record = bytearray()
        route_record += b"\x00"
        route_record += _encode_varint(chunk_bits)
        route_record += struct.pack("<B", route_flags)
        route_record += _encode_varint(route_token_count)
        route_record += _encode_varint(len(route_payload))
        route_record += route_payload

        literal_payload, literal_method = _build_literal_stream_payload(chunk_stream, cube)
        literal_record = bytearray()
        literal_record += b"\x01"
        literal_record += _encode_varint(chunk_bits)
        literal_record += struct.pack("<B", literal_method)
        literal_record += _encode_varint(len(literal_payload))
        literal_record += literal_payload

        if len(literal_record) < len(route_record):
            out += literal_record
            literal_chunks += 1
        else:
            out += route_record
            route_chunks += 1

    diag = {
        "container": "CCM3",
        "chunk_count": len(chunks),
        "route_chunks": route_chunks,
        "literal_chunks": literal_chunks,
        "literal_chunk_fraction": (literal_chunks / max(1, len(chunks))),
    }
    return bytes(out), diag


def _decode_chunked_hybrid(data: bytes, cube: CubeModel) -> tuple[EncodedStream, str]:
    mv = memoryview(data)
    off = 4
    mode_id, original_bits = struct.unpack_from("<BI", mv, off)
    off += 5
    if mode_id not in ID_TO_MODE:
        raise ValueError("unsupported chunked mode id")
    mode = ID_TO_MODE[mode_id]
    chunk_count, off = _decode_varint(mv, off)

    tokens: list[LiteralToken | RouteToken] = []
    total_bits = 0
    for _ in range(chunk_count):
        if off >= len(mv):
            raise ValueError("corrupt chunked payload")
        tag = int(mv[off])
        off += 1
        chunk_bits, off = _decode_varint(mv, off)
        total_bits += chunk_bits
        if tag == 0:
            if off >= len(mv):
                raise ValueError("corrupt route chunk")
            flags = int(mv[off])
            off += 1
            token_count, off = _decode_varint(mv, off)
            payload_len, off = _decode_varint(mv, off)
            if off + payload_len > len(mv):
                raise ValueError("corrupt route chunk length")
            payload = bytes(mv[off : off + payload_len])
            off += payload_len
            route_only = bool(flags & FLAG_ROUTE_ONLY)
            if mode == MODE_FIXED:
                chunk_stream = _decode_fixed(payload, token_count, chunk_bits, cube, route_only, flags)
            elif mode == MODE_LOCAL:
                chunk_stream = _decode_local(payload, token_count, chunk_bits, cube, route_only, flags)
            else:
                chunk_stream = _decode_entropy(payload, token_count, chunk_bits, cube, route_only, flags)
            tokens.extend(chunk_stream.tokens)
        elif tag == 1:
            if off >= len(mv):
                raise ValueError("corrupt literal chunk")
            method = int(mv[off])
            off += 1
            payload_len, off = _decode_varint(mv, off)
            if off + payload_len > len(mv):
                raise ValueError("corrupt literal chunk length")
            payload = bytes(mv[off : off + payload_len])
            off += payload_len
            chunk_stream = _decode_literal_stream_payload(payload, chunk_bits, method)
            tokens.extend(chunk_stream.tokens)
        else:
            raise ValueError("unsupported chunk tag")

    if total_bits != original_bits:
        raise ValueError("chunk bit length mismatch")
    return EncodedStream(tokens=tokens, original_bit_length=original_bits), mode


def encode_mode_stream(stream: EncodedStream, cube: CubeModel, mode: str) -> tuple[bytes, dict]:
    if mode not in MODE_IDS:
        raise ValueError(f"unsupported mode: {mode}")

    if mode == MODE_LEGACY:
        payload = _encode_legacy(stream, cube)
        normalized = stream
        diag = {"length_field_present": True, "route_only": False}
        flags = 0
        header = bytearray()
        header += MAGIC
        header += struct.pack("<BIIB", MODE_IDS[mode], normalized.original_bit_length, len(normalized.tokens), flags)
        return bytes(header) + payload, diag

    return _encode_chunked_hybrid(stream, cube, mode)


def decode_mode_stream(data: bytes, cube: CubeModel) -> tuple[EncodedStream, str]:
    mv = memoryview(data)
    if bytes(mv[:4]) == MAGIC_CHUNKED:
        return _decode_chunked_hybrid(data, cube)

    if bytes(mv[:4]) == MAGIC_LITERAL:
        if len(mv) < 5:
            raise ValueError("corrupt literal-only header")
        meta = int(mv[4])
        mode_id = meta & 0x03
        method = (meta >> 2) & 0x03
        if mode_id not in ID_TO_MODE:
            raise ValueError("unsupported literal-only mode id")
        mode = ID_TO_MODE[mode_id]
        original_bits, off = _decode_varint(mv, 5)
        stream = _decode_literal_stream_payload(bytes(mv[off:]), original_bit_length=original_bits, method=method)
        return stream, mode

    if bytes(mv[:4]) != MAGIC:
        raise ValueError("unsupported stream magic")
    off = 4
    mode_id, original_bits, token_count, flags = struct.unpack_from("<BIIB", mv, off)
    off += 10
    if mode_id not in ID_TO_MODE:
        raise ValueError(f"unsupported mode id: {mode_id}")
    mode = ID_TO_MODE[mode_id]
    payload = bytes(mv[off:])
    route_only = bool(flags & FLAG_ROUTE_ONLY)
    if flags & FLAG_LITERAL_ONLY_STREAM:
        return _decode_literal_stream_payload(payload, original_bits, method=1), mode
    if mode == MODE_LEGACY:
        return _decode_legacy(payload, token_count, original_bits, cube), mode
    if mode == MODE_FIXED:
        return _decode_fixed(payload, token_count, original_bits, cube, route_only, flags), mode
    if mode == MODE_LOCAL:
        return _decode_local(payload, token_count, original_bits, cube, route_only, flags), mode
    return _decode_entropy(payload, token_count, original_bits, cube, route_only, flags), mode
