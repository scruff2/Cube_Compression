from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path

from .benchmark import run_benchmark, write_benchmark_outputs
from .config import CodecConfig


ALLOWED_SWEEP_KEYS = [
    "max_training_bytes",
    "phrase_mode",
    "phrase_length",
    "phrase_lengths",
    "stride",
    "max_regions",
    "max_middle_variants",
    "max_suffix_variants",
    "literal_block_bits",
]


REQUIRED_MATRIX_COLUMNS = [
    "cube_actual_bits",
    "cube_fixed_length_optimized_bits",
    "cube_entropy_whole_route_bits",
    "cube_entropy_factorized_bits",
    "cube_family_local_id_bits",
    "cube_oracle_region_local_bits",
    "target_baseline",
    "target_baseline_bits",
    "best_cube_mode",
    "best_cube_bits",
    "best_cube_minus_target",
    "geometry_verdict",
    "cube_fixed_length_actual_bits",
    "cube_family_local_id_actual_bits",
    "cube_entropy_coded_actual_bits",
    "best_real_cube_mode",
    "best_real_cube_minus_target_bits",
    "descriptor_redesign_verdict",
    "scaling_verdict",
]


def _config_from_base(base: CodecConfig, override: dict) -> CodecConfig:
    data = base.to_dict()
    data.update(override)
    return CodecConfig.from_dict(data)


def run_benchmark_matrix(
    base_config: CodecConfig,
    train_file: str,
    test_file: str,
    sweep_json: str,
    output_dir: str,
) -> dict:
    sweep = json.loads(Path(sweep_json).read_text(encoding="utf-8"))
    for key in sweep:
        if key not in ALLOWED_SWEEP_KEYS:
            raise ValueError(f"unsupported sweep dimension: {key}")

    keys = [k for k in ALLOWED_SWEEP_KEYS if k in sweep]
    value_lists = [sweep[k] for k in keys]

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    real_winning_runs: list[str] = []
    ideal_target_runs: list[str] = []
    ideal_only_runs: list[str] = []
    longer_but_lost_runs: list[str] = []
    unused_capacity_runs: list[str] = []
    for idx, combo in enumerate(itertools.product(*value_lists)):
        override = dict(zip(keys, combo))
        cfg = _config_from_base(base_config, override)
        result = run_benchmark(cfg, [train_file], [test_file])

        run_name = f"run_{idx:03d}"
        metrics_path = out / f"{run_name}_metrics.json"
        write_benchmark_outputs(str(metrics_path), result)

        modes = result.metrics["cube_descriptor_idealization"]
        target_bits = result.metrics["decision"]["target_baseline_bits"]
        best_real_delta = result.metrics["decision"]["best_real_cube_minus_target_bits"]
        if result.metrics["decision"]["best_cube_bits"] < target_bits:
            ideal_target_runs.append(run_name)
        if best_real_delta is not None and best_real_delta < 0:
            real_winning_runs.append(run_name)
        elif result.metrics["decision"]["best_cube_bits"] < target_bits:
            ideal_only_runs.append(run_name)
        if result.metrics["coverage"]["average_route_emitted_length"] >= 128 and (best_real_delta is None or best_real_delta >= 0):
            longer_but_lost_runs.append(run_name)
        frac_used = result.diagnostics.get("scaling_diagnostics", {}).get("larger_cube_utilization_diagnostics", {}).get("fraction_regions_used", 1.0)
        if frac_used < 0.2:
            unused_capacity_runs.append(run_name)

        row = {
            "run": run_name,
            **override,
            "original_bits": result.metrics["compression"]["original_bits"],
            "cube_size_bits": result.metrics["training"]["cube_size_bits"],
            "cube_size_bytes": result.metrics["training"]["cube_size_bytes"],
            "metadata_size": result.metrics["training"]["metadata_size_bytes"],
            "selected_phrases_by_length": result.metrics["training"].get("selected_phrases_by_length"),
            "regions_by_length": result.metrics["training"].get("regions_by_length"),
            "average_emitted_bits_per_route": result.metrics["coverage"]["average_route_emitted_length"],
            "route_coverage_fraction": result.metrics["coverage"]["route_bit_fraction"],
            "cube_actual_bits": modes["cube_actual"]["total_estimated_compressed_bits"],
            "cube_fixed_length_optimized_bits": modes["cube_fixed_length_optimized"]["total_estimated_compressed_bits"],
            "cube_entropy_whole_route_bits": modes["cube_entropy_estimated.whole_route"]["total_estimated_compressed_bits"],
            "cube_entropy_factorized_bits": modes["cube_entropy_estimated.factorized"]["total_estimated_compressed_bits"],
            "cube_family_local_id_bits": modes["cube_family_local_id"]["total_estimated_compressed_bits"],
            "cube_oracle_region_local_bits": modes["cube_oracle_region_local"]["total_estimated_compressed_bits"],
            "target_baseline": result.metrics["decision"]["target_baseline"],
            "target_baseline_bits": target_bits,
            "best_cube_mode": result.metrics["decision"]["best_cube_mode"],
            "best_cube_bits": result.metrics["decision"]["best_cube_bits"],
            "best_cube_minus_target": result.metrics["decision"]["best_cube_bits"] - target_bits,
            "geometry_verdict": result.metrics["decision"]["final_verdict"],
            "cube_fixed_length_actual_bits": result.metrics["real_descriptor_coding_modes"].get("cube_fixed_length_actual", {}).get("compressed_bits"),
            "cube_family_local_id_actual_bits": result.metrics["real_descriptor_coding_modes"].get("cube_family_local_id_actual", {}).get("compressed_bits"),
            "cube_entropy_coded_actual_bits": result.metrics["real_descriptor_coding_modes"].get("cube_entropy_coded_actual", {}).get("compressed_bits"),
            "best_real_cube_mode": result.metrics["decision"]["best_real_cube_mode"],
            "best_real_cube_minus_target_bits": best_real_delta,
            "descriptor_redesign_verdict": result.metrics["decision"]["descriptor_redesign_verdict"],
            "long_phrase_verdict": result.metrics["decision"].get("long_phrase_verdict"),
            "scaling_verdict": result.metrics["decision"].get("scaling_verdict"),
            "target_baseline": result.metrics["decision"].get("target_baseline"),
            "decode_ok": result.metrics["quality"]["decode_success"],
        }
        rows.append(row)

    csv_path = out / "summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["run"])
        writer.writeheader()
        writer.writerows(rows)

    md_lines = [
        "# Benchmark Matrix Summary",
        "",
        "| run | cube_actual_bits | target_baseline | target_baseline_bits | best_cube_mode | best_cube_bits | best_cube_minus_target | geometry_verdict |",
        "|---|---:|---|---:|---|---:|---:|---|",
    ]
    for row in rows:
        md_lines.append(
            f"| {row['run']} | {row['cube_actual_bits']:.2f} | {row['target_baseline']} | {row['target_baseline_bits']:.2f} | {row['best_cube_mode']} | {row['best_cube_bits']:.2f} | {row['best_cube_minus_target']:.2f} | {row['geometry_verdict']} |"
        )

    md_lines.append("")
    md_lines.append("## Runs Where Cube Idealization Beats Target Baseline")
    if ideal_target_runs:
        for run in ideal_target_runs:
            md_lines.append(f"- {run}")
    else:
        md_lines.append("- none")

    md_lines.append("")
    md_lines.append("## Runs Where Any Real Cube Mode Beats Target Baseline")
    if real_winning_runs:
        for run in real_winning_runs:
            md_lines.append(f"- {run}")
    else:
        md_lines.append("- none")

    md_lines.append("")
    md_lines.append("## Runs Where Only Idealized Cube Modes Beat Target Baseline")
    if ideal_only_runs:
        for run in ideal_only_runs:
            md_lines.append(f"- {run}")
    else:
        md_lines.append("- none")

    md_lines.append("")
    md_lines.append("## Runs Where Larger Cubes Increased Route Span But Still Lost")
    if longer_but_lost_runs:
        for run in longer_but_lost_runs:
            md_lines.append(f"- {run}")
    else:
        md_lines.append("- none")

    md_lines.append("")
    md_lines.append("## Runs Where Scaling Mostly Created Unused Capacity")
    if unused_capacity_runs:
        for run in unused_capacity_runs:
            md_lines.append(f"- {run}")
    else:
        md_lines.append("- none")

    md_lines.append("")
    md_lines.append("## Final Scaling Interpretation")
    if real_winning_runs:
        md_lines.append("- scaling appears promising in at least some real-mode runs against target baseline")
    elif longer_but_lost_runs:
        md_lines.append("- scaling increases route span but still does not beat target baseline")
    else:
        md_lines.append("- scaling is not helping enough to justify continued cube investment")

    (out / "summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    return {"runs": len(rows), "summary_csv": str(csv_path), "summary_md": str(out / "summary.md")}
