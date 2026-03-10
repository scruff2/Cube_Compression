from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import load_cube_from_dir, run_benchmark, train_cube, write_benchmark_outputs
from .bitutils import read_bits_file, write_bits_file
from .config import CodecConfig
from .cost_model import build_token_cost_model
from .cube_io import save_cube
from .decoder import decode_stream
from .encoder import encode_bits
from .matrix import run_benchmark_matrix
from .route_index import build_prefix_index
from .route_model import load_binary_stream, save_binary_stream, save_debug_stream
from .stream_codecs import (
    MODE_ENTROPY,
    MODE_FIXED,
    MODE_LEGACY,
    MODE_LOCAL,
    decode_mode_stream,
    encode_mode_stream,
)
from .synthetic import generate_corpus


def _load_config(path: str) -> CodecConfig:
    return CodecConfig.from_file(path)


def cmd_train(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    artifacts = train_cube(config, [args.input], output_dir=args.output_dir)
    save_cube(artifacts.cube, args.output_dir, save_debug=config.debug)
    print(f"trained regions: {len(artifacts.cube.regions)}")


def cmd_encode(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    cube = load_cube_from_dir(args.cube_dir)
    bits = read_bits_file(args.input)
    index = build_prefix_index(cube, config.prefix_index_bits)
    stream, stats = encode_bits(bits, cube, index, config, build_token_cost_model(config, cube))
    if args.mode == MODE_LEGACY:
        save_binary_stream(args.output, stream)
    else:
        payload, _ = encode_mode_stream(stream, cube, args.mode)
        Path(args.output).write_bytes(payload)
    if args.debug_json:
        save_debug_stream(args.debug_json, stream)
    print(
        f"mode={args.mode} encoded tokens: {len(stream.tokens)}, route={stats.route_tokens}, literal={stats.literal_tokens}"
    )


def cmd_decode(args: argparse.Namespace) -> None:
    cube = load_cube_from_dir(args.cube_dir)
    data = Path(args.input).read_bytes()
    try:
        stream, mode = decode_mode_stream(data, cube)
    except Exception:
        stream = load_binary_stream(args.input)
        mode = MODE_LEGACY
    bits = decode_stream(stream, cube)
    write_bits_file(args.output, bits, exact_bit_length=stream.original_bit_length)
    print(f"mode={mode} decoded bits: {stream.original_bit_length}")


def cmd_benchmark(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    result = run_benchmark(config, [args.train], [args.test])
    write_benchmark_outputs(args.output, result)
    print(Path(args.output).with_suffix(".md").read_text(encoding="utf-8"))


def cmd_inspect_cube(args: argparse.Namespace) -> None:
    cube = load_cube_from_dir(args.cube_dir)
    print("Cube metadata:")
    for k, v in cube.metadata.__dict__.items():
        print(f"  {k}: {v}")
    print("Regions:")
    for region in cube.regions:
        print(
            f"  region={region.region_id} prefix={region.prefix_bits[:16]}... middle={len(region.middle_variants)} suffix={len(region.suffix_variants)}"
        )


def cmd_generate_corpus(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    freqs = [float(x) for x in args.family_frequencies.split(",")] if args.family_frequencies else None
    manifest = generate_corpus(
        mode=args.mode,
        output_dir=args.output_dir,
        config=config,
        num_families=args.num_families,
        num_variants=args.num_variants,
        train_phrases=args.train_phrases,
        test_phrases=args.test_phrases,
        family_frequencies=freqs,
        seed=args.seed,
    )
    print(json.dumps(manifest, indent=2))


def cmd_benchmark_matrix(args: argparse.Namespace) -> None:
    config = _load_config(args.config)
    result = run_benchmark_matrix(config, args.train, args.test, args.sweep, args.output_dir)
    print(json.dumps(result, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Shared 3D cube route-descriptor prototype codec")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_train = sub.add_parser("train")
    p_train.add_argument("--config", required=True)
    p_train.add_argument("--input", required=True)
    p_train.add_argument("--output-dir", required=True)
    p_train.set_defaults(func=cmd_train)

    p_encode = sub.add_parser("encode")
    p_encode.add_argument("--config", required=True)
    p_encode.add_argument("--cube-dir", required=True)
    p_encode.add_argument("--input", required=True)
    p_encode.add_argument("--output", required=True)
    p_encode.add_argument("--debug-json")
    p_encode.add_argument(
        "--mode",
        default=MODE_LEGACY,
        choices=[MODE_LEGACY, MODE_FIXED, MODE_LOCAL, MODE_ENTROPY],
    )
    p_encode.set_defaults(func=cmd_encode)

    p_decode = sub.add_parser("decode")
    p_decode.add_argument("--cube-dir", required=True)
    p_decode.add_argument("--input", required=True)
    p_decode.add_argument("--output", required=True)
    p_decode.set_defaults(func=cmd_decode)

    p_bench = sub.add_parser("benchmark")
    p_bench.add_argument("--config", required=True)
    p_bench.add_argument("--train", required=True)
    p_bench.add_argument("--test", required=True)
    p_bench.add_argument("--output", required=True)
    p_bench.set_defaults(func=cmd_benchmark)

    p_inspect = sub.add_parser("inspect-cube")
    p_inspect.add_argument("--cube-dir", required=True)
    p_inspect.set_defaults(func=cmd_inspect_cube)

    p_gen = sub.add_parser("generate-corpus")
    p_gen.add_argument("--mode", required=True, choices=["exact-repeat", "prefix-variant", "middle-variant", "family-mixture", "shifted-overlap"])
    p_gen.add_argument("--output-dir", required=True)
    p_gen.add_argument("--config", required=True)
    p_gen.add_argument("--num-families", type=int, default=4)
    p_gen.add_argument("--num-variants", type=int, default=4)
    p_gen.add_argument("--train-phrases", type=int, default=512)
    p_gen.add_argument("--test-phrases", type=int, default=128)
    p_gen.add_argument("--family-frequencies")
    p_gen.add_argument("--seed", type=int)
    p_gen.set_defaults(func=cmd_generate_corpus)

    p_matrix = sub.add_parser("benchmark-matrix")
    p_matrix.add_argument("--config", required=True)
    p_matrix.add_argument("--train", required=True)
    p_matrix.add_argument("--test", required=True)
    p_matrix.add_argument("--sweep", required=True)
    p_matrix.add_argument("--output-dir", required=True)
    p_matrix.set_defaults(func=cmd_benchmark_matrix)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
