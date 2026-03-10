from __future__ import annotations

import json
import random
from pathlib import Path

from .bitutils import bits_to_bytes
from .config import CodecConfig


def _rand_bits(rng: random.Random, n: int) -> str:
    return "".join("1" if rng.random() > 0.5 else "0" for _ in range(n))


def _write_bits(path: Path, bits: str) -> None:
    path.write_bytes(bits_to_bytes(bits))


def _weighted_choice(rng: random.Random, families: list[str], weights: list[float]) -> str:
    total = sum(weights)
    x = rng.random() * total
    c = 0.0
    for fam, w in zip(families, weights):
        c += w
        if x <= c:
            return fam
    return families[-1]


def generate_corpus(
    mode: str,
    output_dir: str,
    config: CodecConfig,
    num_families: int = 4,
    num_variants: int = 4,
    train_phrases: int = 512,
    test_phrases: int = 128,
    family_frequencies: list[float] | None = None,
    seed: int | None = None,
) -> dict:
    rng = random.Random(config.random_seed if seed is None else seed)
    lengths = [config.phrase_length] if config.phrase_mode == "fixed" else sorted(config.phrase_lengths or [64, 128, 192, 256])
    phrase_len = max(lengths)

    if family_frequencies is None:
        family_frequencies = [1.0 for _ in range(num_families)]

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    families: list[dict] = []
    for _ in range(num_families):
        fam_lengths = lengths if config.phrase_mode == "variable" else [phrase_len]
        per_len = {}
        for L in fam_lengths:
            middle_len = L // 4
            prefix_len = L // 2
            suffix_len = L - prefix_len - middle_len
            prefix = _rand_bits(rng, prefix_len)
            suffix = _rand_bits(rng, suffix_len)
            middles = [_rand_bits(rng, middle_len) for _ in range(num_variants)]
            suffixes = [_rand_bits(rng, suffix_len) for _ in range(num_variants)]
            per_len[str(L)] = {"prefix": prefix, "suffix": suffix, "middles": middles, "suffixes": suffixes}
        families.append({"per_length": per_len})

    def make_phrase(fam: dict, index: int) -> str:
        L = lengths[index % len(lengths)] if config.phrase_mode == "variable" else phrase_len
        rec = fam["per_length"][str(L)]
        if mode == "exact-repeat":
            return rec["prefix"] + rec["middles"][0] + rec["suffix"]
        if mode == "prefix-variant":
            return rec["prefix"] + rec["middles"][index % num_variants] + rec["suffixes"][index % num_variants]
        if mode == "middle-variant":
            return rec["prefix"] + rec["middles"][index % num_variants] + rec["suffix"]
        if mode == "family-mixture":
            return rec["prefix"] + rec["middles"][index % num_variants] + rec["suffixes"][(index * 3) % num_variants]
        if mode == "shifted-overlap":
            base = rec["prefix"] + rec["middles"][index % num_variants] + rec["suffix"]
            shift = (index % max(1, (len(base) // 8)))
            return base[shift:] + base[:shift]
        raise ValueError(f"unsupported mode: {mode}")

    family_keys = [str(i) for i in range(num_families)]

    def build_stream(count: int) -> str:
        phrases: list[str] = []
        for i in range(count):
            fid = int(_weighted_choice(rng, family_keys, family_frequencies))
            phrases.append(make_phrase(families[fid], i))
        return "".join(phrases)

    train_bits = build_stream(train_phrases)
    test_bits = build_stream(test_phrases)

    train_path = out / "train.bin"
    test_path = out / "test.bin"
    manifest_path = out / "manifest.json"

    _write_bits(train_path, train_bits)
    _write_bits(test_path, test_bits)

    manifest = {
        "mode": mode,
        "phrase_mode": config.phrase_mode,
        "phrase_length": config.phrase_length,
        "phrase_lengths": lengths,
        "num_families": num_families,
        "num_variants": num_variants,
        "family_frequencies": family_frequencies,
        "train_phrases": train_phrases,
        "test_phrases": test_phrases,
        "seed": config.random_seed if seed is None else seed,
        "train_file": str(train_path),
        "test_file": str(test_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
