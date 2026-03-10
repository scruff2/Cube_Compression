import json

from cube_codec.config import CodecConfig
from cube_codec.synthetic import generate_corpus


def test_generate_corpus_prefix_variant(tmp_path) -> None:
    cfg = CodecConfig(phrase_length=32, stride=32, random_seed=7)
    manifest = generate_corpus(
        mode="prefix-variant",
        output_dir=str(tmp_path),
        config=cfg,
        num_families=3,
        num_variants=3,
        train_phrases=64,
        test_phrases=16,
        seed=7,
    )
    assert (tmp_path / "train.bin").exists()
    assert (tmp_path / "test.bin").exists()
    assert json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))["mode"] == "prefix-variant"
    assert manifest["num_families"] == 3


def test_generate_corpus_variable_lengths(tmp_path) -> None:
    cfg = CodecConfig(phrase_mode="variable", phrase_length=32, phrase_lengths=[16, 32], stride=8, random_seed=3)
    manifest = generate_corpus(
        mode="family-mixture",
        output_dir=str(tmp_path / "var"),
        config=cfg,
        num_families=2,
        num_variants=2,
        train_phrases=32,
        test_phrases=8,
        seed=3,
    )
    assert manifest["phrase_mode"] == "variable"
    assert manifest["phrase_lengths"] == [16, 32]
