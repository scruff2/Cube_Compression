from cube_codec.baselines import decode_flat_dictionary, encode_flat_dictionary, train_flat_dictionary
from cube_codec.config import CodecConfig


def test_flat_dictionary_baseline_roundtrip() -> None:
    bits = "10101010" * 8 + "11110000" * 4
    phrases = {
        "1010101010101010": 10,
        "1111000011110000": 8,
    }
    cfg = CodecConfig(phrase_length=16, literal_block_bits=8)
    model = train_flat_dictionary(phrases, max_phrases=8)
    encoded = encode_flat_dictionary(bits, model, cfg)
    decoded = decode_flat_dictionary(encoded, model)
    assert decoded == bits
