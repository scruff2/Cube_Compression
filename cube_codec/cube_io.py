from __future__ import annotations

import json
from pathlib import Path

from .cube_model import CubeModel


def _cube_payload(cube: CubeModel) -> bytes:
    bit_chunks: list[str] = []
    for region in cube.regions:
        bit_chunks.append(region.prefix_bits)
        bit_chunks.extend(region.middle_variants)
        bit_chunks.extend(region.suffix_variants)
    joined = "|".join(bit_chunks)
    return joined.encode("ascii")


def save_cube(cube: CubeModel, output_dir: str | Path, save_debug: bool = True) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    (out / "cube.bin").write_bytes(_cube_payload(cube))
    (out / "cube_metadata.json").write_text(json.dumps(cube.metadata.__dict__, indent=2), encoding="utf-8")
    (out / "cube_regions.json").write_text(
        json.dumps([region.__dict__ for region in cube.regions], indent=2), encoding="utf-8"
    )
    if save_debug:
        (out / "cube_debug.json").write_text(json.dumps(cube.to_dict(), indent=2), encoding="utf-8")


def load_cube(cube_dir: str | Path) -> CubeModel:
    root = Path(cube_dir)
    data = {
        "metadata": json.loads((root / "cube_metadata.json").read_text(encoding="utf-8")),
        "regions": json.loads((root / "cube_regions.json").read_text(encoding="utf-8")),
    }
    return CubeModel.from_dict(data)
