from __future__ import annotations

import math
import lzma
import zlib
from collections import Counter
from dataclasses import dataclass

from .bitutils import bits_to_bytes
from .config import CodecConfig
from .route_model import EncodedStream, LiteralToken


@dataclass
class FlatDictModel:
    phrases: list[str]


@dataclass
class FlatDictEncoded:
    tokens: list[tuple[str, int | str]]
    original_bits: int


@dataclass
class FamilyAwareModel:
    families: list[dict]


@dataclass
class FamilyAwareEncoded:
    tokens: list[tuple[str, tuple[int, int, int] | str]]
    original_bits: int


def encode_raw_literal(bits: str, literal_block_bits: int) -> EncodedStream:
    tokens: list[LiteralToken] = []
    for i in range(0, len(bits), literal_block_bits):
        chunk = bits[i : i + literal_block_bits]
        tokens.append(LiteralToken(token_type="L", bit_length=len(chunk), payload_bits=chunk))
    return EncodedStream(tokens=tokens, original_bit_length=len(bits))


def train_flat_dictionary(phrase_counts: dict[str, int], max_phrases: int) -> FlatDictModel:
    phrases = [p for p, _ in sorted(phrase_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:max_phrases]]
    return FlatDictModel(phrases=phrases)


def encode_flat_dictionary(bits: str, model: FlatDictModel, config: CodecConfig) -> FlatDictEncoded:
    n = len(bits)
    phrase_lens = sorted({len(p) for p in model.phrases}, reverse=True)
    index: dict[int, list[tuple[int, str]]] = {}
    for pid, phrase in enumerate(model.phrases):
        index.setdefault(len(phrase), []).append((pid, phrase))

    tokens: list[tuple[str, int | str]] = []
    i = 0
    while i < n:
        best_pid = -1
        best_len = 0
        for plen in phrase_lens:
            if i + plen > n:
                continue
            chunk = bits[i : i + plen]
            for pid, phrase in index.get(plen, []):
                if chunk == phrase:
                    best_pid = pid
                    best_len = plen
                    break
            if best_pid >= 0:
                break

        if best_pid >= 0:
            tokens.append(("P", best_pid))
            i += best_len
        else:
            lit = bits[i : i + config.literal_block_bits]
            tokens.append(("L", lit))
            i += len(lit)

    return FlatDictEncoded(tokens=tokens, original_bits=n)


def decode_flat_dictionary(encoded: FlatDictEncoded, model: FlatDictModel) -> str:
    out: list[str] = []
    for t, v in encoded.tokens:
        if t == "P":
            out.append(model.phrases[int(v)])
        else:
            out.append(str(v))
    return "".join(out)[: encoded.original_bits]


def estimate_flat_dictionary_bits(encoded: FlatDictEncoded, model: FlatDictModel, config: CodecConfig) -> int:
    _ = config
    pid_bits = max(1, math.ceil(math.log2(max(1, len(model.phrases)))))
    total = 0
    for t, v in encoded.tokens:
        if t == "P":
            _ = v
            total += 1 + pid_bits
        else:
            total += 1 + len(str(v))
    return total


def flat_dictionary_breakdown(encoded: FlatDictEncoded, model: FlatDictModel, config: CodecConfig) -> dict:
    pid_bits = max(1, math.ceil(math.log2(max(1, len(model.phrases)))))
    phrase_tokens = [(t, int(v)) for t, v in encoded.tokens if t == "P"]
    literal_tokens = [(t, str(v)) for t, v in encoded.tokens if t == "L"]
    phrase_use = Counter(pid for _, pid in phrase_tokens)
    covered_bits = sum(len(model.phrases[pid]) for _, pid in phrase_tokens)
    phrase_count = len(phrase_tokens)

    return {
        "dictionary_size": len(model.phrases),
        "phrase_id_width_bits": pid_bits,
        "literal_usage_fraction": len(literal_tokens) / max(1, len(encoded.tokens)),
        "avg_phrase_length_covered": covered_bits / max(1, phrase_count),
        "avg_code_length_per_covered_phrase": 1 + pid_bits,
        "unique_dictionary_entries_used": len(phrase_use),
        "top_10_dictionary_entries": [
            {"phrase_id": pid, "count": count, "phrase_prefix": model.phrases[pid][:32]}
            for pid, count in phrase_use.most_common(10)
        ],
    }


def train_family_aware_baseline(phrase_counts: dict[str, int], config: CodecConfig) -> FamilyAwareModel:
    lengths = [config.phrase_length] if config.phrase_mode == "fixed" else sorted(config.phrase_lengths or [64, 128, 192, 256])
    groups: dict[str, dict[str, Counter[str]]] = {}
    for phrase, freq in phrase_counts.items():
        if len(phrase) not in lengths:
            continue
        prefix_len = len(phrase) // 2
        middle_len = len(phrase) // 4
        prefix = phrase[:prefix_len]
        middle = phrase[prefix_len : prefix_len + middle_len]
        suffix = phrase[prefix_len + middle_len :]
        key = f"{len(phrase)}:{prefix}"
        bucket = groups.setdefault(key, {})
        bucket.setdefault(middle, Counter())[suffix] += freq

    families: list[dict] = []
    for key, middle_map in sorted(groups.items(), key=lambda kv: (-sum(sum(c.values()) for c in kv[1].values()), kv[0])):
        length_s, prefix = key.split(":", 1)
        middles = sorted(middle_map.keys())
        suffixes = sorted({s for c in middle_map.values() for s in c.keys()})
        families.append({"length": int(length_s), "prefix": prefix, "middles": middles, "suffixes": suffixes})
        if len(families) >= config.max_regions:
            break
    return FamilyAwareModel(families=families)


def encode_family_aware(bits: str, model: FamilyAwareModel, config: CodecConfig) -> FamilyAwareEncoded:
    n = len(bits)
    lengths = sorted({f["length"] for f in model.families}, reverse=True)
    families_by_length: dict[int, list[tuple[int, dict]]] = {}
    for fid, fam in enumerate(model.families):
        families_by_length.setdefault(fam["length"], []).append((fid, fam))
    tokens: list[tuple[str, tuple[int, int, int] | str]] = []
    i = 0
    while i < n:
        matched = False
        for phrase_len in lengths:
            if i + phrase_len > n:
                continue
            phrase = bits[i : i + phrase_len]
            for fid, fam in families_by_length.get(phrase_len, []):
                prefix = fam["prefix"]
                if not phrase.startswith(prefix):
                    continue
                middle_len = phrase_len // 4
                mid = phrase[len(prefix) : len(prefix) + middle_len]
                suf = phrase[len(prefix) + middle_len :]
                if mid in fam["middles"] and suf in fam["suffixes"]:
                    tokens.append(("F", (fid, fam["middles"].index(mid), fam["suffixes"].index(suf))))
                    i += phrase_len
                    matched = True
                    break
            if matched:
                break
        if matched:
            continue

        lit = bits[i : i + config.literal_block_bits]
        tokens.append(("L", lit))
        i += len(lit)

    return FamilyAwareEncoded(tokens=tokens, original_bits=n)


def decode_family_aware(encoded: FamilyAwareEncoded, model: FamilyAwareModel, config: CodecConfig) -> str:
    out: list[str] = []
    for t, v in encoded.tokens:
        if t == "L":
            out.append(str(v))
            continue
        fid, mid_id, suf_id = v  # type: ignore[misc]
        fam = model.families[fid]
        middle_len = fam["length"] // 4
        out.append(fam["prefix"] + fam["middles"][mid_id] + fam["suffixes"][suf_id])
    return "".join(out)[: encoded.original_bits]


def estimate_family_aware_bits(encoded: FamilyAwareEncoded, model: FamilyAwareModel, config: CodecConfig) -> int:
    fam_bits = max(1, math.ceil(math.log2(max(1, len(model.families)))))
    max_mid = max((len(f["middles"]) for f in model.families), default=1)
    max_suf = max((len(f["suffixes"]) for f in model.families), default=1)
    mid_bits = max(1, math.ceil(math.log2(max_mid)))
    suf_bits = max(1, math.ceil(math.log2(max_suf)))

    total = 0
    for t, v in encoded.tokens:
        if t == "F":
            _ = v
            total += 1 + fam_bits + mid_bits + suf_bits
        else:
            total += 1 + len(str(v))
    return total


def oracle_phrase_family_bits(covered_phrases: int, family_count: int, middle_variants: int, suffix_variants: int) -> int:
    fam_bits = max(1, math.ceil(math.log2(max(1, family_count))))
    mid_bits = max(1, math.ceil(math.log2(max(1, middle_variants))))
    suf_bits = max(1, math.ceil(math.log2(max(1, suffix_variants))))
    return covered_phrases * (fam_bits + mid_bits + suf_bits)


def compress_zlib_bits(bits: str) -> int:
    payload = bits_to_bytes(bits)
    return len(zlib.compress(payload)) * 8


def compress_lzma_bits(bits: str) -> int:
    payload = bits_to_bytes(bits)
    return len(lzma.compress(payload)) * 8


def compression_ratio(original_bits: int, compressed_bits: int) -> float:
    if compressed_bits == 0:
        return 0.0
    return float(original_bits) / float(compressed_bits)
