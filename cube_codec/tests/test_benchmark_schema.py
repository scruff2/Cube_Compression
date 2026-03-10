import json

from cube_codec.benchmark import run_benchmark
from cube_codec.config import CodecConfig


def _write_bits(path, bitstring: str) -> None:
    data = bytearray()
    for i in range(0, len(bitstring), 8):
        chunk = bitstring[i : i + 8]
        if len(chunk) < 8:
            chunk = chunk + ("0" * (8 - len(chunk)))
        data.append(int(chunk, 2))
    path.write_bytes(bytes(data))


def _build_fixture(tmp_path):
    cfg = CodecConfig(
        phrase_mode="variable",
        phrase_length=32,
        phrase_lengths=[16, 32],
        stride=8,
        prefix_index_bits=8,
        max_regions=8,
        max_selected_phrases=64,
        literal_block_bits=4,
        random_seed=11,
        train_sampling_seed=11,
    )
    train = tmp_path / "train.bin"
    test = tmp_path / "test.bin"
    train_bits = ("1111000011110000" * 32) + ("10101010101010101010101010101010" * 16)
    test_bits = ("1111000011110000" * 8) + ("10101010101010101010101010101010" * 4)
    _write_bits(train, train_bits)
    _write_bits(test, test_bits)
    return cfg, str(train), str(test)


def test_benchmark_schema_required_keys(tmp_path) -> None:
    cfg, train, test = _build_fixture(tmp_path)
    result = run_benchmark(cfg, [train], [test])

    metrics = result.metrics
    diagnostics = result.diagnostics

    required_metrics = {
        "config",
        "corpus_split",
        "compression",
        "coverage",
        "search",
        "training",
        "runtime",
        "quality",
        "baselines",
        "real_descriptor_coding_modes",
        "cube_descriptor_idealization",
        "decision",
    }
    required_diag = {
        "cube_modes",
        "descriptor_overhead_diagnosis",
        "real_mode_diagnostics",
        "length_aware_diagnostics",
        "larger_cube_utilization",
        "scaling_diagnostics",
        "training_diagnostics",
        "decision",
    }

    assert required_metrics.issubset(metrics.keys())
    assert required_diag.issubset(diagnostics.keys())


def test_benchmark_reproducibility_deterministic_fields(tmp_path) -> None:
    cfg, train, test = _build_fixture(tmp_path)
    r1 = run_benchmark(cfg, [train], [test])
    r2 = run_benchmark(cfg, [train], [test])

    m1 = r1.metrics
    m2 = r2.metrics

    assert m1["compression"]["compressed_bits"] == m2["compression"]["compressed_bits"]
    assert m1["baselines"]["family_aware"]["compressed_bits"] == m2["baselines"]["family_aware"]["compressed_bits"]
    assert m1["baselines"]["flat_dictionary"]["compressed_bits"] == m2["baselines"]["flat_dictionary"]["compressed_bits"]
    assert m1["decision"] == m2["decision"]
    assert m1["real_descriptor_coding_modes"] == m2["real_descriptor_coding_modes"]
    assert m1["training"]["cube_size_bits"] == m2["training"]["cube_size_bits"]
