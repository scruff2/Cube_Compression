from cube_codec.bitutils import bits_to_bytes, bytes_to_bits, longest_match


def test_bits_roundtrip() -> None:
    bits = "1011001110001"
    packed = bits_to_bytes(bits)
    unpacked = bytes_to_bits(packed)
    assert unpacked.startswith(bits)


def test_longest_match() -> None:
    assert longest_match("101011", "101111") == 3
