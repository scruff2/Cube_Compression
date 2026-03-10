from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodecConfig:
    phrase_mode: str = "fixed"
    phrase_length: int = 64
    phrase_lengths: list[int] | None = None
    stride: int = 64
    overlap_strategy: str = "none"
    max_training_bytes: int | None = None
    train_sampling_seed: int = 123
    min_frequency: int = 2
    min_frequency_by_length: dict[str, int] | None = None
    max_extracted_phrases: int = 200000
    max_selected_phrases: int = 1024
    max_selected_phrases_by_length: dict[str, int] | None = None
    max_regions: int = 64
    max_middle_variants: int = 8
    max_suffix_variants: int = 4
    prefix_index_bits: int = 16
    literal_block_bits: int = 8
    route_token_overhead_bits: int = 1
    literal_token_overhead_bits: int = 1
    debug: bool = False
    random_seed: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "CodecConfig":
        cfg = cls(**data)
        cfg.validate()
        return cfg

    @classmethod
    def from_file(cls, path: str | Path) -> "CodecConfig":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(payload)

    def to_dict(self) -> dict:
        return {
            "phrase_length": self.phrase_length,
            "phrase_mode": self.phrase_mode,
            "phrase_lengths": self.phrase_lengths,
            "stride": self.stride,
            "overlap_strategy": self.overlap_strategy,
            "max_training_bytes": self.max_training_bytes,
            "train_sampling_seed": self.train_sampling_seed,
            "min_frequency": self.min_frequency,
            "min_frequency_by_length": self.min_frequency_by_length,
            "max_extracted_phrases": self.max_extracted_phrases,
            "max_selected_phrases": self.max_selected_phrases,
            "max_selected_phrases_by_length": self.max_selected_phrases_by_length,
            "max_regions": self.max_regions,
            "max_middle_variants": self.max_middle_variants,
            "max_suffix_variants": self.max_suffix_variants,
            "prefix_index_bits": self.prefix_index_bits,
            "literal_block_bits": self.literal_block_bits,
            "route_token_overhead_bits": self.route_token_overhead_bits,
            "literal_token_overhead_bits": self.literal_token_overhead_bits,
            "debug": self.debug,
            "random_seed": self.random_seed,
        }

    def validate(self) -> None:
        positive_fields = [
            "phrase_length",
            "stride",
            "min_frequency",
            "max_extracted_phrases",
            "max_selected_phrases",
            "max_regions",
            "max_middle_variants",
            "max_suffix_variants",
            "prefix_index_bits",
            "literal_block_bits",
            "route_token_overhead_bits",
            "literal_token_overhead_bits",
            "train_sampling_seed",
        ]
        for name in positive_fields:
            value = getattr(self, name)
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.max_training_bytes is not None and (not isinstance(self.max_training_bytes, int) or self.max_training_bytes <= 0):
            raise ValueError("max_training_bytes must be a positive integer or null")

        if self.prefix_index_bits > self.phrase_length:
            if self.phrase_mode == "fixed":
                raise ValueError("prefix_index_bits must be <= phrase_length in fixed mode")

        if self.phrase_mode not in {"fixed", "variable"}:
            raise ValueError("phrase_mode must be 'fixed' or 'variable'")
        if self.phrase_mode == "variable":
            if not self.phrase_lengths:
                self.phrase_lengths = [64, 128, 192, 256]
            for n in self.phrase_lengths:
                if not isinstance(n, int) or n <= 0:
                    raise ValueError("phrase_lengths must contain positive integers")
            if self.prefix_index_bits > min(self.phrase_lengths):
                raise ValueError("prefix_index_bits must be <= min(phrase_lengths) in variable mode")


def save_config(path: str | Path, config: CodecConfig) -> None:
    Path(path).write_text(json.dumps(config.to_dict(), indent=2), encoding="utf-8")
