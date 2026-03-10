from cube_codec.config import CodecConfig
from cube_codec.region_builder import build_regions_from_phrases


def test_region_builder() -> None:
    cfg = CodecConfig(phrase_length=16, stride=16)
    phrases = [
        "0000000011110000",
        "0000000010100000",
        "0000000011111111",
    ]
    regions, stats = build_regions_from_phrases(phrases, cfg)
    assert stats.selected_phrase_count == 3
    assert len(regions) >= 1
    assert regions[0].prefix_length == 8
