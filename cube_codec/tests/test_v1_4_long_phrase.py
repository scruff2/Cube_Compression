from cube_codec.benchmark import run_benchmark
from cube_codec.config import CodecConfig


def _write_bits(path, bitstring: str) -> None:
    data = bytearray()
    for i in range(0, len(bitstring), 8):
        chunk = bitstring[i : i + 8]
        if len(chunk) < 8:
            chunk += "0" * (8 - len(chunk))
        data.append(int(chunk, 2))
    path.write_bytes(bytes(data))


def test_variable_length_benchmark_outputs_long_phrase_fields(tmp_path) -> None:
    cfg = CodecConfig(
        phrase_mode="variable",
        phrase_length=32,
        phrase_lengths=[16, 32],
        stride=8,
        prefix_index_bits=8,
        max_regions=8,
        max_selected_phrases=64,
        literal_block_bits=4,
    )
    train = tmp_path / "train.bin"
    test = tmp_path / "test.bin"

    train_bits = ("1111000011110000" * 32) + ("10101010101010101010101010101010" * 16)
    test_bits = ("1111000011110000" * 8) + ("10101010101010101010101010101010" * 4)
    _write_bits(train, train_bits)
    _write_bits(test, test_bits)

    result = run_benchmark(cfg, [str(train)], [str(test)])
    decision = result.metrics["decision"]
    assert "long_phrase_verdict" in decision
    assert "long_phrase_best_length_class" in decision
    assert "long_phrase_best_real_cube_mode" in decision
    assert "selected_phrases_by_length" in result.metrics["training"]
    assert "route_coverage_by_length_class" in result.metrics["coverage"]
