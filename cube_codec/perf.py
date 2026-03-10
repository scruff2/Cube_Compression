from __future__ import annotations

import json
import time
import tracemalloc
from pathlib import Path

from .benchmark import train_cube
from .bitutils import read_bits_file
from .config import CodecConfig
from .cost_model import build_token_cost_model
from .decoder import decode_stream
from .encoder import encode_bits
from .route_index import build_prefix_index
from .stream_codecs import MODE_ENTROPY, MODE_FIXED, MODE_LEGACY, MODE_LOCAL, decode_mode_stream, encode_mode_stream


def run_perf(config: CodecConfig, train_file: str, test_file: str, repeats: int = 3) -> dict:
    artifacts = train_cube(config, [train_file])
    cube = artifacts.cube
    bits = read_bits_file(test_file)
    index = build_prefix_index(cube, config.prefix_index_bits)
    model = build_token_cost_model(config, cube)

    tracemalloc.start()
    t0 = time.perf_counter()
    stream, _ = encode_bits(bits, cube, index, config, model)
    encode_base_sec = time.perf_counter() - t0
    t1 = time.perf_counter()
    decoded = decode_stream(stream, cube)
    decode_base_sec = time.perf_counter() - t1
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if decoded != bits:
        raise RuntimeError("base decode mismatch in perf run")

    mode_results = {}
    for mode in [MODE_LEGACY, MODE_FIXED, MODE_LOCAL, MODE_ENTROPY]:
        encode_times = []
        decode_times = []
        size_bits = 0
        for _ in range(max(1, repeats)):
            te = time.perf_counter()
            payload, _diag = encode_mode_stream(stream, cube, mode)
            encode_times.append(time.perf_counter() - te)

            td = time.perf_counter()
            ds, _ = decode_mode_stream(payload, cube)
            out = decode_stream(ds, cube)
            decode_times.append(time.perf_counter() - td)
            if out != bits:
                raise RuntimeError(f"mode decode mismatch: {mode}")
            size_bits = len(payload) * 8

        mode_results[mode] = {
            "compressed_bits": size_bits,
            "avg_encode_sec": sum(encode_times) / len(encode_times),
            "avg_decode_sec": sum(decode_times) / len(decode_times),
            "encode_mbps": (len(bits) / max(1e-9, sum(encode_times) / len(encode_times))) / 1_000_000,
            "decode_mbps": (len(bits) / max(1e-9, sum(decode_times) / len(decode_times))) / 1_000_000,
        }

    return {
        "config": config.to_dict(),
        "train_file": train_file,
        "test_file": test_file,
        "test_bits": len(bits),
        "base_encode_sec": encode_base_sec,
        "base_decode_sec": decode_base_sec,
        "peak_memory_bytes": int(peak),
        "mode_results": mode_results,
    }


def write_perf_report(output_json: str, perf: dict) -> None:
    p = Path(output_json)
    p.write_text(json.dumps(perf, indent=2), encoding="utf-8")

    lines = [
        "# Performance Baseline",
        "",
        f"- test_bits: {perf['test_bits']}",
        f"- peak_memory_bytes: {perf['peak_memory_bytes']}",
        f"- base_encode_sec: {perf['base_encode_sec']:.6f}",
        f"- base_decode_sec: {perf['base_decode_sec']:.6f}",
        "",
        "| mode | bits | avg_encode_sec | avg_decode_sec | encode_mbps | decode_mbps |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for mode, row in perf["mode_results"].items():
        lines.append(
            f"| {mode} | {row['compressed_bits']} | {row['avg_encode_sec']:.6f} | {row['avg_decode_sec']:.6f} | {row['encode_mbps']:.3f} | {row['decode_mbps']:.3f} |"
        )

    p.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
