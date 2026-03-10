from __future__ import annotations

import json
import math
import statistics
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from .baselines import (
    compress_lzma_bits,
    compress_zlib_bits,
    decode_family_aware,
    decode_flat_dictionary,
    encode_family_aware,
    encode_flat_dictionary,
    encode_raw_literal,
    estimate_family_aware_bits,
    estimate_flat_dictionary_bits,
    flat_dictionary_breakdown,
    oracle_phrase_family_bits,
    train_family_aware_baseline,
    train_flat_dictionary,
)
from .config import CodecConfig
from .corpus import load_corpus_bits
from .cost_model import TokenCostModel, build_route_analysis, build_token_cost_model
from .cube_io import load_cube, save_cube
from .cube_model import CubeModel
from .decoder import decode_stream
from .encoder import encode_bits
from .metrics import compute_compression_metrics
from .phrases import extract_phrases, select_top_phrases
from .region_builder import build_cube_model, build_regions_from_phrases
from .route_index import build_prefix_index
from .route_model import EncodedStream, LiteralToken, RouteToken
from .stream_codecs import (
    MODE_ENTROPY,
    MODE_FIXED,
    MODE_LEGACY,
    MODE_LOCAL,
    decode_mode_stream,
    encode_mode_stream,
)


REQUIRED_METRIC_KEYS = ["compression", "coverage", "search", "training", "quality", "baselines"]


@dataclass
class TrainArtifacts:
    cube: CubeModel
    phrase_counts: dict[str, int]
    training_metrics: dict
    training_diagnostics: dict


@dataclass
class BenchmarkResult:
    metrics: dict
    diagnostics: dict


def estimate_stream_bits(stream: EncodedStream, cost_model: TokenCostModel) -> int:
    total = 0.0
    for token in stream.tokens:
        if isinstance(token, RouteToken):
            total += cost_model.route_cost(token)
        else:
            total += cost_model.literal_cost(token)
    return int(total)


def _phrase_histogram(phrase_counts: dict[str, int]) -> dict[str, int]:
    hist: Counter[int] = Counter(phrase_counts.values())
    return {str(k): v for k, v in sorted(hist.items())}


def _selected_coverage(phrase_counts: dict[str, int], selected: list[tuple[str, int]]) -> float:
    total = sum(phrase_counts.values())
    selected_total = sum(freq for _, freq in selected)
    return selected_total / max(1, total)


def train_cube(config: CodecConfig, input_files: list[str], output_dir: str | None = None) -> TrainArtifacts:
    train_start = time.perf_counter()
    bits, corpus_stats = load_corpus_bits(input_files)
    if config.max_training_bytes is not None:
        max_bits = config.max_training_bytes * 8
        if len(bits) > max_bits:
            import random

            rng = random.Random(config.train_sampling_seed)
            start = rng.randint(0, len(bits) - max_bits)
            bits = bits[start : start + max_bits]
    phrase_counts: dict[str, int] = {}
    extracted_by_length: dict[str, int] = {}
    selected_by_length: dict[str, int] = {}
    source_mass_by_length: dict[str, int] = {}
    regions_by_length: dict[str, int] = {}
    all_regions = []
    next_region_id = 0

    lengths = [config.phrase_length] if config.phrase_mode == "fixed" else sorted(config.phrase_lengths or [64, 128, 192, 256])
    for phrase_len in lengths:
        min_freq = config.min_frequency_by_length.get(str(phrase_len), config.min_frequency) if config.min_frequency_by_length else config.min_frequency
        phrase_result = extract_phrases(
            bits,
            phrase_len,
            config.stride,
            min_freq,
            max_extracted_phrases=config.max_extracted_phrases,
        )
        selected_cap = (
            config.max_selected_phrases_by_length.get(str(phrase_len), config.max_selected_phrases)
            if config.max_selected_phrases_by_length
            else config.max_selected_phrases
        )
        top_phrases = select_top_phrases(phrase_result.phrase_counts, selected_cap)

        cfg_data = config.to_dict()
        cfg_data["phrase_mode"] = "fixed"
        cfg_data["phrase_length"] = phrase_len
        cfg_data["phrase_lengths"] = None
        cfg_l = CodecConfig.from_dict(cfg_data)
        regions, _ = build_regions_from_phrases([p for p, _ in top_phrases], cfg_l)
        for r in regions:
            r.region_id = next_region_id
            next_region_id += 1
            all_regions.append(r)

        phrase_counts.update(phrase_result.phrase_counts)
        extracted_by_length[str(phrase_len)] = phrase_result.extracted_count
        selected_by_length[str(phrase_len)] = len(top_phrases)
        source_mass_by_length[str(phrase_len)] = sum(freq for _, freq in top_phrases)
        regions_by_length[str(phrase_len)] = len(regions)

    build_cfg = config
    if config.phrase_mode == "variable":
        cfg_data = config.to_dict()
        cfg_data["phrase_length"] = max(lengths)
        cfg_data["phrase_mode"] = "fixed"
        cfg_data["phrase_lengths"] = None
        build_cfg = CodecConfig.from_dict(cfg_data)
    cube = build_cube_model(all_regions, build_cfg)
    train_time = time.perf_counter() - train_start

    cube_size_bits = sum(
        len(r.prefix_bits) + sum(len(m) for m in r.middle_variants) + sum(len(s) for s in r.suffix_variants)
        for r in cube.regions
    )

    training_metrics = {
        "corpus_file_count": corpus_stats.file_count,
        "corpus_bits": corpus_stats.total_bits,
        "ingested_train_bits": len(bits),
        "extracted_phrases": sum(extracted_by_length.values()),
        "selected_phrases": sum(selected_by_length.values()),
        "selected_phrases_by_length": selected_by_length,
        "selected_source_mass_by_length": source_mass_by_length,
        "clusters": len(cube.regions),
        "regions": len(cube.regions),
        "regions_by_length": regions_by_length,
        "cube_size_bits": cube_size_bits,
        "cube_size_bytes": (cube_size_bits + 7) // 8,
        "metadata_size_bytes": len(json.dumps(cube.metadata.__dict__).encode("utf-8")),
        "total_shared_artifact_size_bytes": ((cube_size_bits + 7) // 8) + len(json.dumps(cube.metadata.__dict__).encode("utf-8")),
        "train_wall_time_sec": train_time,
    }

    training_diagnostics = {
        "phrase_extraction": {
            "total_extracted_phrases": sum(extracted_by_length.values()),
            "total_extracted_phrases_by_length": extracted_by_length,
            "selected_phrases_by_length": selected_by_length,
            "selected_source_mass_by_length": source_mass_by_length,
            "phrase_frequency_histogram": _phrase_histogram(phrase_counts),
        }
    }

    if output_dir is not None:
        save_cube(cube, output_dir, save_debug=True)

    return TrainArtifacts(cube=cube, phrase_counts=phrase_counts, training_metrics=training_metrics, training_diagnostics=training_diagnostics)


def _bits_view(total_bits: float, source_bits: int, avg_route_bits: float) -> dict:
    return {
        "total_estimated_compressed_bits": float(total_bits),
        "bits_per_source_bit": float(total_bits) / max(1, source_bits),
        "compression_ratio": float(source_bits) / max(1.0, float(total_bits)),
        "average_bits_per_route_token": float(avg_route_bits),
    }


def _cube_mode_rows(cube_modes: dict, source_bits: int) -> dict[str, dict]:
    rows = {
        "cube_actual": _bits_view(
            cube_modes["cube_actual"]["total_bits"],
            source_bits,
            cube_modes["cube_actual"]["avg_bits_per_route_token"],
        ),
        "cube_fixed_length_optimized": _bits_view(
            cube_modes["cube_fixed_length_optimized"]["total_bits"],
            source_bits,
            cube_modes["cube_fixed_length_optimized"]["avg_bits_per_route_token"],
        ),
        "cube_entropy_estimated.whole_route": _bits_view(
            cube_modes["cube_entropy_estimated"]["whole_route"]["total_bits"],
            source_bits,
            cube_modes["cube_entropy_estimated"]["whole_route"]["avg_bits_per_route_token"],
        ),
        "cube_entropy_estimated.factorized": _bits_view(
            cube_modes["cube_entropy_estimated"]["factorized"]["total_bits"],
            source_bits,
            cube_modes["cube_entropy_estimated"]["factorized"]["avg_bits_per_route_token"],
        ),
        "cube_family_local_id": _bits_view(
            cube_modes["cube_family_local_id"]["total_bits"],
            source_bits,
            cube_modes["cube_family_local_id"]["avg_bits_per_route_token"],
        ),
        "cube_oracle_used_route": _bits_view(
            cube_modes["cube_oracle_used_route"]["total_bits"],
            source_bits,
            cube_modes["cube_oracle_used_route"]["avg_bits_per_route_token"],
        ),
        "cube_oracle_region_local": _bits_view(
            cube_modes["cube_oracle_region_local"]["total_bits"],
            source_bits,
            cube_modes["cube_oracle_region_local"]["avg_bits_per_route_token"],
        ),
        "cube_oracle_factorized": _bits_view(
            cube_modes["cube_oracle_factorized"]["total_bits"],
            source_bits,
            cube_modes["cube_oracle_factorized"]["avg_bits_per_route_token"],
        ),
    }
    return rows


def _final_verdict(beats_any_realistic: bool, best_mode_bits: float, family_bits: float, decode_ok: bool) -> str:
    if not decode_ok:
        return "inconclusive"
    margin = family_bits - best_mode_bits
    if beats_any_realistic and margin > 0.03 * family_bits:
        return "geometry_promising"
    if beats_any_realistic:
        return "geometry_marginal"
    if best_mode_bits > family_bits:
        return "geometry_unnecessary"
    return "inconclusive"


def _recommendation(verdict: str) -> str:
    if verdict == "geometry_promising":
        return "continue cube investigation"
    if verdict == "geometry_marginal":
        return "cube only worth pursuing if descriptor redesign is implemented"
    if verdict == "geometry_unnecessary":
        return "pivot to family-aware structured coding"
    return "insufficient evidence, rerun on stronger corpus"


def benchmark(config: CodecConfig, train_files: list[str], test_files: list[str], output_json: str | None = None) -> dict:
    result = run_benchmark(config, train_files, test_files)
    if output_json:
        Path(output_json).write_text(json.dumps(result.metrics, indent=2), encoding="utf-8")
    return result.metrics


def run_benchmark(config: CodecConfig, train_files: list[str], test_files: list[str]) -> BenchmarkResult:
    artifacts = train_cube(config, train_files)
    cube = artifacts.cube

    index = build_prefix_index(cube, config.prefix_index_bits)
    model = build_token_cost_model(config, cube)

    test_bits, _ = load_corpus_bits(test_files)

    encode_start = time.perf_counter()
    encoded, encode_stats = encode_bits(test_bits, cube, index, config, model)
    encode_sec = time.perf_counter() - encode_start

    decode_start = time.perf_counter()
    decoded = decode_stream(encoded, cube)
    decode_sec = time.perf_counter() - decode_start

    decode_ok = decoded == test_bits

    route_tokens = [t for t in encoded.tokens if isinstance(t, RouteToken)]
    literal_tokens = [t for t in encoded.tokens if isinstance(t, LiteralToken)]
    literal_total_bits = sum(model.literal_cost(t) for t in literal_tokens)

    cube_modes = build_route_analysis(
        route_tokens=route_tokens,
        literal_total_bits=literal_total_bits,
        phrase_length=config.phrase_length,
        route_breakdown=model.route_breakdown,
        token_overhead_bits=config.route_token_overhead_bits,
    )

    cube_rows = _cube_mode_rows(cube_modes, len(test_bits))
    cube_actual_bits = cube_rows["cube_actual"]["total_estimated_compressed_bits"]
    comp = compute_compression_metrics(len(test_bits), int(cube_actual_bits))

    flat_model = train_flat_dictionary(artifacts.phrase_counts, config.max_regions * 16)
    flat_enc = encode_flat_dictionary(test_bits, flat_model, config)
    flat_dec = decode_flat_dictionary(flat_enc, flat_model)
    flat_ok = flat_dec == test_bits
    flat_bits = estimate_flat_dictionary_bits(flat_enc, flat_model, config)
    flat_diag = flat_dictionary_breakdown(flat_enc, flat_model, config)

    fam_model = train_family_aware_baseline(artifacts.phrase_counts, config)
    fam_enc = encode_family_aware(test_bits, fam_model, config)
    fam_dec = decode_family_aware(fam_enc, fam_model, config)
    fam_ok = fam_dec == test_bits
    family_bits = estimate_family_aware_bits(fam_enc, fam_model, config)

    covered_phrases = sum(1 for t, _ in fam_enc.tokens if t == "F")
    max_middle = max((len(f["middles"]) for f in fam_model.families), default=1)
    max_suffix = max((len(f["suffixes"]) for f in fam_model.families), default=1)
    phrase_oracle_bits = oracle_phrase_family_bits(covered_phrases, len(fam_model.families), max_middle, max_suffix)

    raw_stream = encode_raw_literal(test_bits, config.literal_block_bits)
    raw_bits = estimate_stream_bits(raw_stream, model)
    zlib_bits = compress_zlib_bits(test_bits)
    lzma_bits = compress_lzma_bits(test_bits)

    route_descriptor_counter = Counter(f"{t.region_id}:{t.middle_id}:{t.suffix_id}" for t in route_tokens)
    region_len_map = {r.region_id: r.route_length for r in cube.regions}
    route_lengths = [region_len_map.get(t.region_id, config.phrase_length) for t in route_tokens]
    route_descriptor_bits = [model.route_cost(t) for t in route_tokens]
    avg_descriptor_bits = sum(route_descriptor_bits) / max(1, len(route_descriptor_bits))
    descriptor_bits_per_emitted = sum(route_descriptor_bits) / max(1, sum(route_lengths))
    route_coverage_by_length: dict[str, int] = {}
    for t in route_tokens:
        l = region_len_map.get(t.region_id, config.phrase_length)
        route_coverage_by_length[str(l)] = route_coverage_by_length.get(str(l), 0) + l
    region_support_sizes = {
        str(rid): len({f"{t.middle_id}:{t.suffix_id}" for t in route_tokens if t.region_id == rid})
        for rid in {t.region_id for t in route_tokens}
    }

    family_aware_row = _bits_view(family_bits, len(test_bits), 0.0)
    cube_rows_with_delta = {}
    for mode_name, row in cube_rows.items():
        row = dict(row)
        row["delta_vs_cube_actual_bits"] = row["total_estimated_compressed_bits"] - cube_rows["cube_actual"]["total_estimated_compressed_bits"]
        row["delta_vs_family_aware_bits"] = row["total_estimated_compressed_bits"] - family_bits
        cube_rows_with_delta[mode_name] = row

    real_modes: dict[str, dict] = {}
    real_mode_diagnostics: dict[str, dict] = {}
    for mode in [MODE_LEGACY, MODE_FIXED, MODE_LOCAL, MODE_ENTROPY]:
        try:
            payload, mode_diag = encode_mode_stream(encoded, cube, mode)
            decoded_stream, decoded_mode = decode_mode_stream(payload, cube)
            decoded_bits_mode = decode_stream(decoded_stream, cube)
            ok = decoded_bits_mode == test_bits
            real_modes[mode] = {
                "implemented": True,
                "compressed_bits": len(payload) * 8,
                "compression_ratio": len(test_bits) / max(1, len(payload) * 8),
                "decode_success": ok,
            }
            real_mode_diagnostics[mode] = mode_diag | {"decoded_mode": decoded_mode}
        except Exception as exc:
            real_modes[mode] = {
                "implemented": False,
                "status": "not_implemented",
                "error": str(exc),
            }
            real_mode_diagnostics[mode] = {"status": "not_implemented", "error": str(exc)}

    realistic_modes = [
        "cube_fixed_length_optimized",
        "cube_entropy_estimated.factorized",
        "cube_family_local_id",
    ]
    beats_realistic = [m for m in realistic_modes if cube_rows_with_delta[m]["total_estimated_compressed_bits"] < family_bits]

    best_mode = min(cube_rows_with_delta.items(), key=lambda kv: kv[1]["total_estimated_compressed_bits"])
    best_mode_name = best_mode[0]
    best_mode_bits = best_mode[1]["total_estimated_compressed_bits"]

    verdict = _final_verdict(bool(beats_realistic), best_mode_bits, float(family_bits), decode_ok)
    recommendation = _recommendation(verdict)

    real_candidates = {
        k: v for k, v in real_modes.items() if v.get("implemented") and v.get("decode_success")
    }
    if real_candidates:
        best_real_name, best_real = min(real_candidates.items(), key=lambda kv: kv[1]["compressed_bits"])
        best_real_bits = float(best_real["compressed_bits"])
    else:
        best_real_name = "none"
        best_real_bits = float("inf")

    if not real_candidates:
        redesign_verdict = "inconclusive"
    elif best_real_bits < family_bits:
        redesign_verdict = "descriptor_redesign_succeeds"
    elif best_real_bits <= family_bits * 1.05:
        redesign_verdict = "descriptor_redesign_partially_succeeds"
    else:
        redesign_verdict = "descriptor_redesign_fails"

    long_phrase_best_class = max(route_coverage_by_length.items(), key=lambda kv: kv[1])[0] if route_coverage_by_length else "none"
    long_phrase_any_beats = bool(real_candidates and best_real_bits < family_bits)
    if long_phrase_any_beats:
        long_phrase_verdict = "long_phrases_promising"
    elif (sum(route_lengths) / max(1, len(route_lengths))) > 96:
        long_phrase_verdict = "long_phrases_marginal"
    elif len(route_tokens) > 0:
        long_phrase_verdict = "long_phrases_not_helping"
    else:
        long_phrase_verdict = "inconclusive"
    if long_phrase_verdict == "long_phrases_promising":
        long_phrase_reco = "continue cube investigation"
    elif long_phrase_verdict == "long_phrases_marginal":
        long_phrase_reco = "cube only worth pursuing if descriptor redesign is implemented"
    elif long_phrase_verdict == "long_phrases_not_helping":
        long_phrase_reco = "pivot to family-aware structured coding"
    else:
        long_phrase_reco = "insufficient evidence, rerun on stronger corpus"

    target_key = config.competition_target
    target_bits = {
        "zlib": float(zlib_bits),
        "lzma": float(lzma_bits),
        "flat_dictionary": float(flat_bits),
    }[target_key]
    target_any_real = bool(real_candidates and best_real_bits < target_bits)

    scaling_any_real = target_any_real
    region_used_fraction = len(region_support_sizes) / max(1, len(cube.regions))
    if scaling_any_real:
        scaling_verdict = "scaling_promising"
    elif region_used_fraction > 0.4 and (sum(route_lengths) / max(1, len(route_lengths))) >= 128:
        scaling_verdict = "scaling_marginal"
    elif len(cube.regions) > 0:
        scaling_verdict = "scaling_not_helping"
    else:
        scaling_verdict = "inconclusive"
    if scaling_verdict == "scaling_promising":
        scaling_reco = "continue cube investigation"
    elif scaling_verdict == "scaling_marginal":
        scaling_reco = "cube only worth pursuing if descriptor redesign is implemented"
    elif scaling_verdict == "scaling_not_helping":
        scaling_reco = "pivot to family-aware structured coding"
    else:
        scaling_reco = "insufficient evidence, rerun on stronger corpus"

    metrics = {
        "config": config.to_dict(),
        "corpus_split": {"train_files": train_files, "test_files": test_files},
        "compression": asdict(comp)
        | {
            "route_token_fraction": len(route_tokens) / max(1, len(encoded.tokens)),
            "literal_token_fraction": len(literal_tokens) / max(1, len(encoded.tokens)),
        },
        "coverage": {
            "route_hit_rate": len(route_tokens) / max(1, len(encoded.tokens)),
            "route_bit_fraction": sum(route_lengths) / max(1, len(test_bits)),
            "unique_routes_used": len(route_descriptor_counter),
            "route_coverage_by_length_class": route_coverage_by_length,
            "average_route_emitted_length": (sum(route_lengths) / max(1, len(route_lengths))),
            "max_route_emitted_length": (max(route_lengths) if route_lengths else 0),
            "emitted_length_distribution": dict(Counter(route_lengths)),
        },
        "search": {
            "avg_candidate_routes_examined_per_position": encode_stats.candidate_checks / max(1, encode_stats.positions_visited),
            "index_size": index.size(),
        },
        "training": artifacts.training_metrics,
        "runtime": {"encode_wall_time_sec": encode_sec, "decode_wall_time_sec": decode_sec},
        "quality": {
            "decode_success": decode_ok,
            "mismatch_location": (-1 if decode_ok else next(i for i in range(min(len(decoded), len(test_bits))) if decoded[i] != test_bits[i])),
        },
        "baselines": {
            "raw_literals": {"compressed_bits": raw_bits, "compression_ratio": len(test_bits) / max(1, raw_bits)},
            "flat_dictionary": {"compressed_bits": flat_bits, "compression_ratio": len(test_bits) / max(1, flat_bits), "decode_success": flat_ok},
            "family_aware": {
                "compressed_bits": family_bits,
                "compression_ratio": len(test_bits) / max(1, family_bits),
                "decode_success": fam_ok,
            },
            "phrase_family_oracle": {
                "estimated_bits": phrase_oracle_bits,
                "estimated_ratio": len(test_bits) / max(1, phrase_oracle_bits),
            },
            "zlib": {"compressed_bits": zlib_bits, "compression_ratio": len(test_bits) / max(1, zlib_bits)},
            "lzma": {"compressed_bits": lzma_bits, "compression_ratio": len(test_bits) / max(1, lzma_bits)},
        },
        "real_descriptor_coding_modes": real_modes,
        "cube_descriptor_idealization": cube_rows_with_delta,
        "decision": {
            "beats_family_aware_in_any_mode": any(
                row["total_estimated_compressed_bits"] < family_bits for row in cube_rows_with_delta.values()
            ),
            "beats_family_aware_in_realistic_mode": bool(beats_realistic),
            "best_cube_mode": best_mode_name,
            "best_cube_bits": best_mode_bits,
            "best_cube_minus_family_aware": best_mode_bits - family_bits,
            "final_verdict": verdict,
            "recommendation": recommendation,
            "best_real_cube_mode": best_real_name,
            "best_real_cube_minus_family_aware_bits": best_real_bits - family_bits if math.isfinite(best_real_bits) else None,
            "descriptor_redesign_verdict": redesign_verdict,
            "long_phrase_best_real_cube_mode": best_real_name,
            "long_phrase_best_real_cube_bits": best_real_bits if math.isfinite(best_real_bits) else None,
            "long_phrase_best_real_cube_minus_family_aware_bits": (best_real_bits - family_bits if math.isfinite(best_real_bits) else None),
            "long_phrase_any_real_cube_beats_family_aware": long_phrase_any_beats,
            "long_phrase_best_length_class": long_phrase_best_class,
            "long_phrase_verdict": long_phrase_verdict,
            "long_phrase_recommendation": long_phrase_reco,
            "scaling_train_bits": artifacts.training_metrics["ingested_train_bits"],
            "scaling_cube_payload_bits": artifacts.training_metrics["cube_size_bits"],
            "scaling_region_count": artifacts.training_metrics["regions"],
            "scaling_best_real_cube_mode": best_real_name,
            "scaling_best_real_cube_bits": best_real_bits if math.isfinite(best_real_bits) else None,
            "scaling_best_real_cube_minus_family_aware_bits": (best_real_bits - family_bits if math.isfinite(best_real_bits) else None),
            "scaling_any_real_cube_beats_family_aware": bool(real_candidates and best_real_bits < family_bits),
            "target_baseline": target_key,
            "target_baseline_bits": target_bits,
            "best_real_cube_minus_target_bits": (best_real_bits - target_bits if math.isfinite(best_real_bits) else None),
            "any_real_cube_beats_target": target_any_real,
            "scaling_any_real_cube_beats_target": target_any_real,
            "scaling_average_route_emitted_bits": (sum(route_lengths) / max(1, len(route_lengths))),
            "scaling_verdict": scaling_verdict,
            "scaling_recommendation": scaling_reco,
        },
    }

    diagnostics = {
        "cube_modes": {
            "cube_actual": cube_modes["cube_actual"],
            "cube_fixed_length_optimized": cube_modes["cube_fixed_length_optimized"],
            "cube_entropy_estimated": cube_modes["cube_entropy_estimated"],
            "cube_family_local_id": cube_modes["cube_family_local_id"],
            "cube_oracle_used_route": cube_modes["cube_oracle_used_route"],
            "cube_oracle_region_local": cube_modes["cube_oracle_region_local"],
            "cube_oracle_factorized": cube_modes["cube_oracle_factorized"],
        },
        "descriptor_overhead_diagnosis": {
            "route_count": len(route_tokens),
            "used_route_count": len(route_descriptor_counter),
            "used_route_frequency_distribution": dict(route_descriptor_counter),
            "region_local_route_support_sizes": region_support_sizes,
            "field_wise_route_cost_contribution": asdict(model.route_breakdown),
            "idealized_route_cost_estimates": cube_rows_with_delta,
            "biggest_overhead_source": (
                "non-entropy-coded route usage"
                if cube_rows_with_delta["cube_entropy_estimated.factorized"]["delta_vs_cube_actual_bits"]
                < cube_rows_with_delta["cube_fixed_length_optimized"]["delta_vs_cube_actual_bits"]
                else "fixed length and fixed-field overhead"
            ),
            "gap_attribution": {
                "actual_cube_avg_bits_per_phrase": cube_rows_with_delta["cube_actual"]["bits_per_source_bit"] * config.phrase_length,
                "fixed_length_optimized_avg_bits_per_phrase": cube_rows_with_delta["cube_fixed_length_optimized"]["bits_per_source_bit"] * config.phrase_length,
                "entropy_factorized_avg_bits_per_phrase": cube_rows_with_delta["cube_entropy_estimated.factorized"]["bits_per_source_bit"] * config.phrase_length,
                "family_local_id_avg_bits_per_phrase": cube_rows_with_delta["cube_family_local_id"]["bits_per_source_bit"] * config.phrase_length,
                "family_aware_avg_bits_per_phrase": family_aware_row["bits_per_source_bit"] * config.phrase_length,
                "remaining_gap_after_idealization": best_mode_bits - family_bits,
            },
        },
        "real_mode_diagnostics": {
            "cube_fixed_length_actual": real_mode_diagnostics.get(MODE_FIXED, {"status": "not_implemented"}),
            "cube_family_local_id_actual": real_mode_diagnostics.get(MODE_LOCAL, {"status": "not_implemented"}),
            "cube_entropy_coded_actual": real_mode_diagnostics.get(MODE_ENTROPY, {"status": "not_implemented"}),
            "bits_saved_vs_legacy_fixed": (
                real_modes.get(MODE_LEGACY, {}).get("compressed_bits", 0)
                - real_modes.get(MODE_FIXED, {}).get("compressed_bits", 0)
                if real_modes.get(MODE_LEGACY, {}).get("implemented") and real_modes.get(MODE_FIXED, {}).get("implemented")
                else None
            ),
            "mode_vs_v12_estimate_gap": {
                "cube_fixed_length_actual_minus_v12": (
                    real_modes.get(MODE_FIXED, {}).get("compressed_bits", 0)
                    - cube_rows_with_delta["cube_fixed_length_optimized"]["total_estimated_compressed_bits"]
                    if real_modes.get(MODE_FIXED, {}).get("implemented")
                    else None
                ),
                "cube_entropy_coded_actual_minus_v12_factorized": (
                    real_modes.get(MODE_ENTROPY, {}).get("compressed_bits", 0)
                    - cube_rows_with_delta["cube_entropy_estimated.factorized"]["total_estimated_compressed_bits"]
                    if real_modes.get(MODE_ENTROPY, {}).get("implemented")
                    else None
                ),
            },
        },
        "length_aware_diagnostics": {
            "route_coverage_by_length_class": route_coverage_by_length,
            "literal_fallback_by_length_class": {"literal": len(literal_tokens)},
            "average_route_emitted_length": (sum(route_lengths) / max(1, len(route_lengths))),
            "max_route_emitted_length": (max(route_lengths) if route_lengths else 0),
            "distribution_of_emitted_lengths": dict(Counter(route_lengths)),
            "descriptor_efficiency_by_length_class": {
                str(length): {
                    "average_descriptor_bits": (
                        sum(model.route_cost(t) for t in route_tokens if region_len_map.get(t.region_id, config.phrase_length) == length)
                        / max(1, sum(1 for t in route_tokens if region_len_map.get(t.region_id, config.phrase_length) == length))
                    ),
                    "average_emitted_bits": float(length),
                    "descriptor_bits_per_emitted_source_bit": (
                        sum(model.route_cost(t) for t in route_tokens if region_len_map.get(t.region_id, config.phrase_length) == length)
                        / max(1, length * sum(1 for t in route_tokens if region_len_map.get(t.region_id, config.phrase_length) == length))
                    ),
                }
                for length in sorted(set(route_lengths))
            },
        },
        "larger_cube_utilization": {
            "cube_payload_size_bits": artifacts.training_metrics["cube_size_bits"],
            "metadata_size_bytes": artifacts.training_metrics["metadata_size_bytes"],
            "regions_built": artifacts.training_metrics["regions"],
            "regions_used": len(region_support_sizes),
            "per_region_emitted_bits": {
                str(rid): sum(region_len_map.get(t.region_id, config.phrase_length) for t in route_tokens if t.region_id == rid)
                for rid in region_support_sizes
            },
            "larger_capacity_exercised": len(region_support_sizes) > 1,
        },
        "scaling_diagnostics": {
            "cube_size_diagnostics": {
                "cube_payload_bits": artifacts.training_metrics["cube_size_bits"],
                "cube_payload_bytes": artifacts.training_metrics["cube_size_bytes"],
                "metadata_bytes": artifacts.training_metrics["metadata_size_bytes"],
                "total_shared_artifact_size": artifacts.training_metrics["total_shared_artifact_size_bytes"],
                "region_count_built": artifacts.training_metrics["regions"],
                "region_count_used": len(region_support_sizes),
                "selected_phrases": artifacts.training_metrics["selected_phrases"],
                "selected_phrases_by_length_class": artifacts.training_metrics.get("selected_phrases_by_length"),
                "variants_by_region_statistics": {
                    "avg_middle_variants": sum(len(r.middle_variants) for r in cube.regions) / max(1, len(cube.regions)),
                    "avg_suffix_variants": sum(len(r.suffix_variants) for r in cube.regions) / max(1, len(cube.regions)),
                },
            },
            "route_span_diagnostics": {
                "average_emitted_bits_per_route": (sum(route_lengths) / max(1, len(route_lengths))),
                "median_emitted_bits_per_route": (statistics.median(route_lengths) if route_lengths else 0.0),
                "max_emitted_bits_per_route": (max(route_lengths) if route_lengths else 0),
                "emitted_length_distribution": dict(Counter(route_lengths)),
                "coverage_by_length_class": route_coverage_by_length,
            },
            "descriptor_efficiency_diagnostics": {
                "average_descriptor_bits_per_route": avg_descriptor_bits,
                "descriptor_bits_per_emitted_source_bit": descriptor_bits_per_emitted,
                "top_used_route_counts": route_descriptor_counter.most_common(10),
                "unique_route_count": len(route_descriptor_counter),
                "descriptor_efficiency_degrades_with_scale": (avg_descriptor_bits > 24),
            },
            "larger_cube_utilization_diagnostics": {
                "fraction_regions_used": len(region_support_sizes) / max(1, len(cube.regions)),
                "fraction_selected_phrases_exercised": len(route_descriptor_counter) / max(1, artifacts.training_metrics["selected_phrases"]),
                "longer_routes_from_larger_capacity": (sum(route_lengths) / max(1, len(route_lengths))) >= 128,
            },
            "comparative_diagnostics": {
                "best_real_cube_mode": best_real_name,
                "best_real_cube_bits": best_real_bits if math.isfinite(best_real_bits) else None,
                "family_aware_bits": family_bits,
                "flat_dictionary_bits": flat_bits,
                "general_purpose_bits": zlib_bits,
            },
        },
        "training_diagnostics": artifacts.training_diagnostics,
        "decision": metrics["decision"],
    }

    return BenchmarkResult(metrics=metrics, diagnostics=diagnostics)


def markdown_report(metrics: dict, diagnostics: dict | None = None) -> str:
    lines = [
        "# Cube Route Codec Benchmark Report",
        "",
        "## Configuration Used",
        f"- phrase_length: {metrics['config']['phrase_length']}",
        f"- stride: {metrics['config']['stride']}",
        "",
        "## Cube Descriptor Idealization Table",
        "| Mode | Total Bits | Bits/Source Bit | Compression Ratio | Avg Bits/Route | Delta vs cube_actual | Delta vs family_aware |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    table = metrics["cube_descriptor_idealization"]
    for mode in [
        "cube_actual",
        "cube_fixed_length_optimized",
        "cube_entropy_estimated.whole_route",
        "cube_entropy_estimated.factorized",
        "cube_family_local_id",
        "cube_oracle_used_route",
        "cube_oracle_region_local",
        "cube_oracle_factorized",
    ]:
        row = table[mode]
        lines.append(
            f"| {mode} | {row['total_estimated_compressed_bits']:.2f} | {row['bits_per_source_bit']:.4f} | {row['compression_ratio']:.4f} | {row['average_bits_per_route_token']:.4f} | {row['delta_vs_cube_actual_bits']:.2f} | {row['delta_vs_family_aware_bits']:.2f} |"
        )

    lines += [
        "",
        "## Long-Phrase Regime Summary",
        f"- fixed 128 results: {'available' if metrics['config'].get('phrase_length') == 128 or metrics['config'].get('phrase_mode') == 'variable' else 'not primary in this run'}",
        f"- fixed 256 results: {'available' if metrics['config'].get('phrase_length') == 256 or metrics['config'].get('phrase_mode') == 'variable' else 'not primary in this run'}",
        f"- variable-length results: {'available' if metrics['config'].get('phrase_mode') == 'variable' else 'not primary in this run'}",
        "",
        "## Longer-Segment Utilization",
        f"- average emitted length: {metrics['coverage']['average_route_emitted_length']:.2f}",
        f"- max emitted length: {metrics['coverage']['max_route_emitted_length']}",
        f"- route coverage by length class: {metrics['coverage']['route_coverage_by_length_class']}",
        "",
        "## Scaling Summary",
        f"- scaling_train_bits: {metrics['decision']['scaling_train_bits']}",
        f"- scaling_cube_payload_bits: {metrics['decision']['scaling_cube_payload_bits']}",
        f"- scaling_region_count: {metrics['decision']['scaling_region_count']}",
        "",
        "## Real Descriptor-Coding Modes",
    ]
    for mode in [MODE_LEGACY, MODE_FIXED, MODE_LOCAL, MODE_ENTROPY]:
        item = metrics["real_descriptor_coding_modes"].get(mode, {"implemented": False, "status": "not_implemented"})
        if item.get("implemented"):
            lines.append(
                f"- {mode}: bits={item['compressed_bits']}, ratio={item['compression_ratio']:.4f}, decode_success={item['decode_success']}"
            )
        else:
            lines.append(f"- {mode}: not_implemented")

    lines += [
        "",
        "## Comparative Baseline Table",
        "| Mode | Bits | Ratio |",
        "|---|---:|---:|",
        f"| cube_best_real ({metrics['decision']['best_real_cube_mode']}) | {metrics['decision']['long_phrase_best_real_cube_bits'] if metrics['decision']['long_phrase_best_real_cube_bits'] is not None else 'n/a'} | {metrics['real_descriptor_coding_modes'].get(metrics['decision']['best_real_cube_mode'], {}).get('compression_ratio', 0):.4f} |",
        f"| family_aware | {metrics['baselines']['family_aware']['compressed_bits']} | {metrics['baselines']['family_aware']['compression_ratio']:.4f} |",
        f"| flat_dictionary | {metrics['baselines']['flat_dictionary']['compressed_bits']} | {metrics['baselines']['flat_dictionary']['compression_ratio']:.4f} |",
        f"| zlib | {metrics['baselines']['zlib']['compressed_bits']} | {metrics['baselines']['zlib']['compression_ratio']:.4f} |",
        "",
        "## Baseline Comparison",
        f"- raw_literals ratio: {metrics['baselines']['raw_literals']['compression_ratio']:.4f}",
        f"- flat_dictionary ratio: {metrics['baselines']['flat_dictionary']['compression_ratio']:.4f}",
        f"- family_aware ratio: {metrics['baselines']['family_aware']['compression_ratio']:.4f}",
        f"- phrase_family_oracle ratio: {metrics['baselines']['phrase_family_oracle']['estimated_ratio']:.4f}",
        "",
        "## Decision",
        f"- target baseline: {metrics['decision']['target_baseline']} ({metrics['decision']['target_baseline_bits']} bits)",
        f"- cube_fixed_length_actual beats target: {metrics['real_descriptor_coding_modes'].get(MODE_FIXED, {}).get('compressed_bits', float('inf')) < metrics['decision']['target_baseline_bits'] if metrics['real_descriptor_coding_modes'].get(MODE_FIXED, {}).get('implemented') else False}",
        f"- cube_family_local_id_actual beats target: {metrics['real_descriptor_coding_modes'].get(MODE_LOCAL, {}).get('compressed_bits', float('inf')) < metrics['decision']['target_baseline_bits'] if metrics['real_descriptor_coding_modes'].get(MODE_LOCAL, {}).get('implemented') else False}",
        f"- cube_entropy_coded_actual beats target: {metrics['real_descriptor_coding_modes'].get(MODE_ENTROPY, {}).get('compressed_bits', float('inf')) < metrics['decision']['target_baseline_bits'] if metrics['real_descriptor_coding_modes'].get(MODE_ENTROPY, {}).get('implemented') else False}",
        f"- best real cube mode: {metrics['decision']['best_real_cube_mode']}",
        f"- best_real_cube_minus_target_bits: {metrics['decision']['best_real_cube_minus_target_bits']}",
        f"- descriptor_redesign_verdict: {metrics['decision']['descriptor_redesign_verdict']}",
        f"- beats family-aware in any mode: {metrics['decision']['beats_family_aware_in_any_mode']}",
        f"- best cube mode: {metrics['decision']['best_cube_mode']}",
        f"- final verdict: {metrics['decision']['final_verdict']}",
        f"- long_phrase_any_real_cube_beats_family_aware: {metrics['decision']['long_phrase_any_real_cube_beats_family_aware']}",
        f"- long_phrase_best_length_class: {metrics['decision']['long_phrase_best_length_class']}",
        f"- long_phrase_verdict: {metrics['decision']['long_phrase_verdict']}",
        f"- scaling_any_real_cube_beats_target: {metrics['decision']['scaling_any_real_cube_beats_target']}",
        f"- scaling_verdict: {metrics['decision']['scaling_verdict']}",
        "",
        "## Recommendation",
        f"- {metrics['decision']['recommendation']}",
        f"- {metrics['decision']['long_phrase_recommendation']}",
        f"- {metrics['decision']['scaling_recommendation']}",
    ]

    return "\n".join(lines)


def diagnostics_markdown(metrics: dict, diagnostics: dict) -> str:
    d = diagnostics["descriptor_overhead_diagnosis"]
    real = diagnostics.get("real_mode_diagnostics", {})
    length_diag = diagnostics.get("length_aware_diagnostics", {})
    scaling_diag = diagnostics.get("scaling_diagnostics", {})
    lines = [
        "# Cube Route Codec Diagnostics",
        "",
        "## Descriptor-Overhead Diagnosis",
        f"- route_count: {d['route_count']}",
        f"- used_route_count: {d['used_route_count']}",
        f"- region_local_route_support_sizes: {d['region_local_route_support_sizes']}",
        f"- field_wise_route_cost_contribution: {d['field_wise_route_cost_contribution']}",
        f"- biggest_overhead_source: {d['biggest_overhead_source']}",
        "",
        "## Cube Viability Decision",
        f"- final_verdict: {diagnostics['decision']['final_verdict']}",
        f"- beats_family_aware_in_any_mode: {diagnostics['decision']['beats_family_aware_in_any_mode']}",
        f"- best_cube_mode: {diagnostics['decision']['best_cube_mode']}",
        f"- descriptor_redesign_verdict: {diagnostics['decision']['descriptor_redesign_verdict']}",
        "",
        "## Fixed-Length Mode Diagnostics",
        f"- {real.get('cube_fixed_length_actual', {})}",
        "",
        "## Family-Local-ID Diagnostics",
        f"- {real.get('cube_family_local_id_actual', {})}",
        "",
        "## Entropy-Coded Diagnostics",
        f"- {real.get('cube_entropy_coded_actual', {})}",
        "",
        "## Length-Aware Coverage Diagnostics",
        f"- {length_diag}",
        "",
        "## Scale-Aware Diagnostics",
        f"- {scaling_diag}",
        "",
        "## Cube Modes (JSON)",
        json.dumps(diagnostics["cube_modes"], indent=2),
    ]
    return "\n".join(lines)


def write_benchmark_outputs(output_metrics_json: str, result: BenchmarkResult) -> None:
    metrics_path = Path(output_metrics_json)
    stem = metrics_path.stem
    if stem.endswith("_metrics"):
        base = stem[:-8]
        diagnostics_path = metrics_path.with_name(f"{base}_diagnostics.json")
        metrics_md_path = metrics_path.with_name(f"{stem}.md")
        diagnostics_md_path = metrics_path.with_name(f"{base}_diagnostics.md")
    else:
        diagnostics_path = metrics_path.with_name("diagnostics.json")
        metrics_md_path = metrics_path.with_suffix(".md")
        diagnostics_md_path = metrics_path.with_name("diagnostics.md")

    metrics_path.write_text(json.dumps(result.metrics, indent=2), encoding="utf-8")
    diagnostics_path.write_text(json.dumps(result.diagnostics, indent=2), encoding="utf-8")
    metrics_md_path.write_text(markdown_report(result.metrics, result.diagnostics), encoding="utf-8")
    diagnostics_md_path.write_text(diagnostics_markdown(result.metrics, result.diagnostics), encoding="utf-8")


def load_cube_from_dir(cube_dir: str) -> CubeModel:
    return load_cube(cube_dir)
