import json

from cube_codec.benchmark import REQUIRED_METRIC_KEYS, diagnostics_markdown, markdown_report, run_benchmark, write_benchmark_outputs
from cube_codec.config import CodecConfig


def _write_bits(path, bitstring: str) -> None:
    data = bytearray()
    for i in range(0, len(bitstring), 8):
        chunk = bitstring[i : i + 8]
        if len(chunk) < 8:
            chunk = chunk + ("0" * (8 - len(chunk)))
        data.append(int(chunk, 2))
    path.write_bytes(bytes(data))


def test_benchmark_pipeline(tmp_path) -> None:
    cfg = CodecConfig(phrase_length=16, stride=16, prefix_index_bits=8, max_regions=8, literal_block_bits=4)
    train = tmp_path / "train.bin"
    test = tmp_path / "test.bin"

    train_bits = ("1111000010101010" * 32) + ("1111000011110000" * 16)
    test_bits = ("1111000010101010" * 8) + ("1111000011110000" * 4)

    _write_bits(train, train_bits)
    _write_bits(test, test_bits)

    result = run_benchmark(cfg, [str(train)], [str(test)])
    out = tmp_path / "metrics.json"
    write_benchmark_outputs(str(out), result)

    assert out.exists()
    assert (tmp_path / "diagnostics.json").exists()
    assert (tmp_path / "metrics.md").exists()
    assert (tmp_path / "diagnostics.md").exists()

    loaded = json.loads(out.read_text(encoding="utf-8"))
    for key in REQUIRED_METRIC_KEYS:
        assert key in loaded

    assert result.metrics["quality"]["decode_success"] is True
    assert "cube_modes" in result.diagnostics
    assert "decision" in result.diagnostics
    assert "final_verdict" in result.metrics["decision"]
    assert "real_descriptor_coding_modes" in result.metrics
    assert "cube_fixed_length_actual" in result.metrics["real_descriptor_coding_modes"]
    assert "descriptor_redesign_verdict" in result.metrics["decision"]
    assert "mode_vs_v12_estimate_gap" in result.diagnostics["real_mode_diagnostics"]
    assert "scaling_verdict" in result.metrics["decision"]
    assert "scaling_train_bits" in result.metrics["decision"]
    assert "scaling_diagnostics" in result.diagnostics

    report = markdown_report(result.metrics, result.diagnostics)
    assert "## Cube Descriptor Idealization Table" in report
    assert "## Recommendation" in report

    diag_md = diagnostics_markdown(result.metrics, result.diagnostics)
    assert "## Descriptor-Overhead Diagnosis" in diag_md
    assert "## Cube Viability Decision" in diag_md
