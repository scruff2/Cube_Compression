import csv
import json

from cube_codec.config import CodecConfig
from cube_codec.matrix import REQUIRED_MATRIX_COLUMNS, run_benchmark_matrix


def _write_bits(path, bitstring: str) -> None:
    data = bytearray()
    for i in range(0, len(bitstring), 8):
        chunk = bitstring[i : i + 8]
        if len(chunk) < 8:
            chunk = chunk + ("0" * (8 - len(chunk)))
        data.append(int(chunk, 2))
    path.write_bytes(bytes(data))


def test_benchmark_matrix_outputs(tmp_path) -> None:
    cfg = CodecConfig(phrase_length=16, stride=16, prefix_index_bits=8, max_regions=4, literal_block_bits=4)
    train = tmp_path / "train.bin"
    test = tmp_path / "test.bin"
    sweep = tmp_path / "sweep.json"

    _write_bits(train, "1111000011110000" * 64)
    _write_bits(test, "1111000011110000" * 16)
    sweep.write_text(json.dumps({"stride": [16], "max_regions": [4, 8]}), encoding="utf-8")

    out_dir = tmp_path / "matrix"
    result = run_benchmark_matrix(cfg, str(train), str(test), str(sweep), str(out_dir))
    assert result["runs"] == 2
    assert (out_dir / "summary.csv").exists()
    assert (out_dir / "summary.md").exists()

    rows = list(csv.DictReader((out_dir / "summary.csv").open("r", encoding="utf-8")))
    assert rows
    for col in REQUIRED_MATRIX_COLUMNS:
        assert col in rows[0]

    md = (out_dir / "summary.md").read_text(encoding="utf-8")
    assert "## Runs Where Cube Idealization Beats Family-Aware" in md
    assert "## Runs Where Larger Cubes Increased Route Span But Still Lost" in md
    assert "## Runs Where Scaling Mostly Created Unused Capacity" in md
    assert "## Final Scaling Interpretation" in md
