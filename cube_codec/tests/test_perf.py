from cube_codec.config import CodecConfig
from cube_codec.perf import run_perf


def _write_bits(path, bitstring: str) -> None:
    data = bytearray()
    for i in range(0, len(bitstring), 8):
        chunk = bitstring[i : i + 8]
        if len(chunk) < 8:
            chunk += "0" * (8 - len(chunk))
        data.append(int(chunk, 2))
    path.write_bytes(bytes(data))


def test_perf_output_schema(tmp_path) -> None:
    cfg = CodecConfig(phrase_length=16, stride=16, prefix_index_bits=8, max_regions=8, literal_block_bits=4)
    train = tmp_path / "train.bin"
    test = tmp_path / "test.bin"
    _write_bits(train, "1111000011110000" * 64)
    _write_bits(test, "1111000011110000" * 16)

    out = run_perf(cfg, str(train), str(test), repeats=1)
    assert "peak_memory_bytes" in out
    assert "mode_results" in out
    for mode in ["cube_actual_legacy", "cube_fixed_length_actual", "cube_family_local_id_actual", "cube_entropy_coded_actual"]:
        assert mode in out["mode_results"]
        assert out["mode_results"][mode]["compressed_bits"] > 0
