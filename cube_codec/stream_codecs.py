from __future__ import annotations

import heapq
import struct
from collections import Counter

from .cube_model import CubeModel, reconstruct_route
from .route_model import EncodedStream, LiteralToken, RouteToken

MAGIC = b"CCM2"
FLAG_ROUTE_ONLY = 1

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


def _encode_fixed(stream: EncodedStream, cube: CubeModel) -> tuple[bytes, EncodedStream, bool]:
    fixed_stream = _full_route_stream(stream, cube)
    route_only = all(isinstance(t, RouteToken) for t in fixed_stream.tokens)
    writer = BitWriter()
    r_bits, m_bits, s_bits = _route_widths(cube)
    for token in fixed_stream.tokens:
        if isinstance(token, LiteralToken):
            writer.write_bits(0, 1)
            writer.write_bits(token.bit_length, 8)
            writer.write_bitstring(token.payload_bits[: token.bit_length])
        else:
            if not route_only:
                writer.write_bits(1, 1)
            writer.write_bits(token.region_id, r_bits)
            writer.write_bits(token.middle_id, m_bits)
            writer.write_bits(token.suffix_id, s_bits)
    return writer.to_bytes(), fixed_stream, route_only


def _decode_fixed(payload: bytes, token_count: int, original_bit_length: int, cube: CubeModel, route_only: bool) -> EncodedStream:
    reader = BitReader(payload)
    r_bits, m_bits, s_bits = _route_widths(cube)
    tokens = []
    for _ in range(token_count):
        if route_only:
            tokens.append(RouteToken(token_type="R", region_id=reader.read_bits(r_bits), middle_id=reader.read_bits(m_bits), suffix_id=reader.read_bits(s_bits), emit_length=None))
            continue
        t = reader.read_bits(1)
        if t == 0:
            n = reader.read_bits(8)
            bits = reader.read_bitstring(n)
            tokens.append(LiteralToken(token_type="L", bit_length=n, payload_bits=bits))
        else:
            tokens.append(RouteToken(token_type="R", region_id=reader.read_bits(r_bits), middle_id=reader.read_bits(m_bits), suffix_id=reader.read_bits(s_bits), emit_length=None))
    return EncodedStream(tokens=tokens, original_bit_length=original_bit_length)


def _encode_local(stream: EncodedStream, cube: CubeModel) -> tuple[bytes, EncodedStream, dict, bool]:
    local_stream = _full_route_stream(stream, cube)
    route_only = all(isinstance(t, RouteToken) for t in local_stream.tokens)
    writer = BitWriter()
    r_bits, _, _ = _route_widths(cube)
    forward, _, widths = _local_maps(cube)
    for token in local_stream.tokens:
        if isinstance(token, LiteralToken):
            writer.write_bits(0, 1)
            writer.write_bits(token.bit_length, 8)
            writer.write_bitstring(token.payload_bits[: token.bit_length])
        else:
            if not route_only:
                writer.write_bits(1, 1)
            writer.write_bits(token.region_id, r_bits)
            local_id = forward[token.region_id][(token.middle_id, token.suffix_id)]
            writer.write_bits(local_id, widths[token.region_id])
    diagnostics = {
        "region_id_width": r_bits,
        "local_route_table_size_per_region": {str(k): len(v) for k, v in forward.items()},
        "max_local_id_width": max(widths.values()) if widths else 0,
        "avg_local_id_width": (sum(widths.values()) / max(1, len(widths))),
    }
    return writer.to_bytes(), local_stream, diagnostics, route_only


def _decode_local(payload: bytes, token_count: int, original_bit_length: int, cube: CubeModel, route_only: bool) -> EncodedStream:
    reader = BitReader(payload)
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
            bits = reader.read_bitstring(n)
            tokens.append(LiteralToken(token_type="L", bit_length=n, payload_bits=bits))
        else:
            region = reader.read_bits(r_bits)
            local_id = reader.read_bits(widths[region])
            mid, suf = reverse[region][local_id]
            tokens.append(RouteToken(token_type="R", region_id=region, middle_id=mid, suffix_id=suf, emit_length=None))
    return EncodedStream(tokens=tokens, original_bit_length=original_bit_length)


def _encode_entropy(stream: EncodedStream, cube: CubeModel) -> tuple[bytes, EncodedStream, dict, bool]:
    entropy_stream = _full_route_stream(stream, cube)
    route_only = all(isinstance(t, RouteToken) for t in entropy_stream.tokens)
    route_freq = Counter((t.region_id, t.middle_id, t.suffix_id) for t in entropy_stream.tokens if isinstance(t, RouteToken))
    raw_codes = _build_huffman(route_freq)
    lengths = {sym: len(code) if len(code) > 0 else 1 for sym, code in raw_codes.items()}
    codes = _canonical_from_lengths(lengths)

    writer = BitWriter()
    for token in entropy_stream.tokens:
        if isinstance(token, LiteralToken):
            writer.write_bits(0, 1)
            writer.write_bits(token.bit_length, 8)
            writer.write_bitstring(token.payload_bits[: token.bit_length])
        else:
            if not route_only:
                writer.write_bits(1, 1)
            writer.write_bitstring(codes[(token.region_id, token.middle_id, token.suffix_id)])

    table = bytearray()
    table += struct.pack("<H", len(codes))
    for sym in sorted(codes):
        r, m, s = sym
        table += struct.pack("<HHHB", r, m, s, lengths[sym])
    payload = bytes(table) + writer.to_bytes()

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
    }
    return payload, entropy_stream, diagnostics, route_only


def _decode_entropy(payload: bytes, token_count: int, original_bit_length: int, cube: CubeModel, route_only: bool) -> EncodedStream:
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

    reader = BitReader(bytes(mv[off:]))
    tokens = []
    for _i in range(token_count):
        if not route_only:
            t = reader.read_bits(1)
            if t == 0:
                n = reader.read_bits(8)
                bits = reader.read_bitstring(n)
                tokens.append(LiteralToken(token_type="L", bit_length=n, payload_bits=bits))
                continue
        code = ""
        while code not in code_to_sym:
            if reader.eof():
                raise ValueError("corrupt entropy payload")
            code += str(reader.read_bits(1))
        r, m, s = code_to_sym[code]
        tokens.append(RouteToken(token_type="R", region_id=r, middle_id=m, suffix_id=s, emit_length=None))
    return EncodedStream(tokens=tokens, original_bit_length=original_bit_length)


def encode_mode_stream(stream: EncodedStream, cube: CubeModel, mode: str) -> tuple[bytes, dict]:
    if mode not in MODE_IDS:
        raise ValueError(f"unsupported mode: {mode}")

    flags = 0
    if mode == MODE_LEGACY:
        payload = _encode_legacy(stream, cube)
        normalized = stream
        diag = {"length_field_present": True, "route_only": False}
    elif mode == MODE_FIXED:
        payload, normalized, route_only = _encode_fixed(stream, cube)
        if route_only:
            flags |= FLAG_ROUTE_ONLY
        diag = {"length_field_present": False, "route_only": route_only}
    elif mode == MODE_LOCAL:
        payload, normalized, diag, route_only = _encode_local(stream, cube)
        if route_only:
            flags |= FLAG_ROUTE_ONLY
        diag = diag | {"route_only": route_only}
    else:
        payload, normalized, diag, route_only = _encode_entropy(stream, cube)
        if route_only:
            flags |= FLAG_ROUTE_ONLY
        diag = diag | {"route_only": route_only}

    header = bytearray()
    header += MAGIC
    header += struct.pack("<BIIB", MODE_IDS[mode], normalized.original_bit_length, len(normalized.tokens), flags)
    return bytes(header) + payload, diag


def decode_mode_stream(data: bytes, cube: CubeModel) -> tuple[EncodedStream, str]:
    mv = memoryview(data)
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
    if mode == MODE_LEGACY:
        return _decode_legacy(payload, token_count, original_bits, cube), mode
    if mode == MODE_FIXED:
        return _decode_fixed(payload, token_count, original_bits, cube, route_only), mode
    if mode == MODE_LOCAL:
        return _decode_local(payload, token_count, original_bits, cube, route_only), mode
    return _decode_entropy(payload, token_count, original_bits, cube, route_only), mode
