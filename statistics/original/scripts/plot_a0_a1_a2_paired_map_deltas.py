#!/usr/bin/env python3
"""Generate the formal A0/A1/A2 paired validation mAP50-95 figure.

The plotted observations are read exclusively from the 15 per-run
``validation_results/*/metrics_summary.json`` files. Documented aggregate
values are used only as rounded consistency controls and never as plot data.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_ROOT = ROOT / "validation_results"
OUTPUT_DIR = ROOT / "figures"
OUTPUT_STEM = OUTPUT_DIR / "a0_a1_a2_paired_map_deltas"

CONDITIONS = ("A0", "A1", "A2")
SEEDS = tuple(range(1, 6))
CONTRASTS = (
    ("A1 − A0", "A1", "A0", "delta_A1_A0"),
    ("A2 − A0", "A2", "A0", "delta_A2_A0"),
    ("A1 − A2", "A1", "A2", "delta_A1_A2"),
)

# Rounded final values are controls only. The tolerance represents rounding to
# six decimal places; plotted points and reported statistics use source values.
CONSISTENCY_CONTROLS = {
    "A1 − A0": {"mean": 0.071849, "ci": (0.055059, 0.088640), "positive": 5},
    "A2 − A0": {"mean": 0.068955, "ci": (0.051324, 0.086585), "positive": 5},
    "A1 − A2": {"mean": 0.002895, "ci": (-0.001720, 0.007509), "positive": 3},
}
ROUNDING_TOLERANCE = 0.00000051


def source_path(condition: str, seed: int) -> Path:
    """Return the explicit per-run source path for one formal run."""
    return VALIDATION_ROOT / f"{condition}_seed{seed:02d}" / "metrics_summary.json"


def load_formal_metrics() -> tuple[dict[str, dict[int, float]], list[Path]]:
    """Load and validate all 15 formal per-run validation metrics."""
    values = {condition: {} for condition in CONDITIONS}
    sources: list[Path] = []

    for condition in CONDITIONS:
        for seed in SEEDS:
            path = source_path(condition, seed)
            if not path.is_file():
                raise FileNotFoundError(f"Missing required per-run source: {path}")

            with path.open("r", encoding="utf-8") as handle:
                record: dict[str, Any] = json.load(handle)

            expected_run = f"{condition}_seed{seed:02d}"
            if record.get("condition") != condition:
                raise ValueError(
                    f"Condition mismatch in {path}: {record.get('condition')!r} != {condition!r}"
                )
            if record.get("seed") != seed:
                raise ValueError(
                    f"Seed mismatch in {path}: {record.get('seed')!r} != {seed}"
                )
            if record.get("run") != expected_run:
                raise ValueError(
                    f"Run mismatch in {path}: {record.get('run')!r} != {expected_run!r}"
                )
            if "mAP50_95" not in record:
                raise KeyError(f"Missing mAP50_95 in {path}")

            value = float(record["mAP50_95"])
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"Invalid mAP50_95 in {path}: {value!r}")

            values[condition][seed] = value
            sources.append(path.resolve())

    for condition in CONDITIONS:
        found = set(values[condition])
        expected = set(SEEDS)
        if found != expected:
            raise ValueError(
                f"Seed set mismatch for {condition}: found {sorted(found)}, "
                f"expected {sorted(expected)}"
            )

    return values, sources


def calculate(
    values: dict[str, dict[int, float]],
) -> tuple[dict[str, np.ndarray], dict[str, dict[str, float | int | tuple[float, float]]]]:
    """Calculate paired deltas and descriptive interval statistics."""
    deltas: dict[str, np.ndarray] = {}
    stats: dict[str, dict[str, float | int | tuple[float, float]]] = {}

    for label, minuend, subtrahend, _ in CONTRASTS:
        paired = np.asarray(
            [values[minuend][seed] - values[subtrahend][seed] for seed in SEEDS],
            dtype=float,
        )
        mean = float(np.mean(paired))
        sd = float(np.std(paired, ddof=1))
        critical_t = float(t.ppf(0.975, df=len(paired) - 1))
        half_width = critical_t * sd / math.sqrt(len(paired))
        ci = (mean - half_width, mean + half_width)

        deltas[label] = paired
        stats[label] = {
            "mean": mean,
            "sd": sd,
            "ci": ci,
            "positive": int(np.count_nonzero(paired > 0.0)),
        }

    return deltas, stats


def validate_controls(
    stats: dict[str, dict[str, float | int | tuple[float, float]]],
) -> None:
    """Abort before output generation if rounded controls do not agree."""
    discrepancies: list[str] = []
    for label, expected in CONSISTENCY_CONTROLS.items():
        observed = stats[label]
        observed_ci = observed["ci"]
        assert isinstance(observed_ci, tuple)

        if abs(float(observed["mean"]) - float(expected["mean"])) > ROUNDING_TOLERANCE:
            discrepancies.append(
                f"{label} mean: observed {float(observed['mean']):.12f}, "
                f"control {float(expected['mean']):.6f}"
            )
        expected_ci = expected["ci"]
        assert isinstance(expected_ci, tuple)
        for side, observed_bound, expected_bound in zip(
            ("lower", "upper"), observed_ci, expected_ci
        ):
            if abs(observed_bound - expected_bound) > ROUNDING_TOLERANCE:
                discrepancies.append(
                    f"{label} CI {side}: observed {observed_bound:.12f}, "
                    f"control {expected_bound:.6f}"
                )
        if int(observed["positive"]) != int(expected["positive"]):
            discrepancies.append(
                f"{label} positives: observed {observed['positive']}, "
                f"control {expected['positive']}"
            )

    if discrepancies:
        details = "\n".join(f"  - {item}" for item in discrepancies)
        raise RuntimeError(
            "Consistency controls failed; no figure or CSV was generated.\n" + details
        )


def print_audit(
    values: dict[str, dict[int, float]],
    sources: list[Path],
    deltas: dict[str, np.ndarray],
    stats: dict[str, dict[str, float | int | tuple[float, float]]],
) -> None:
    """Print source provenance, paired observations, and summary statistics."""
    print("SOURCE FILES (per-run formal validation metrics):")
    for path in sources:
        print(f"  {path}")

    print("\nSOURCE mAP50-95 VALUES (seed order 1..5):")
    for condition in CONDITIONS:
        formatted = ", ".join(f"{values[condition][seed]:.15f}" for seed in SEEDS)
        print(f"  {condition}: [{formatted}]")

    print("\nPAIRED DELTAS (seed order 1..5):")
    for label, _, _, _ in CONTRASTS:
        formatted = ", ".join(f"{value:.15f}" for value in deltas[label])
        console_label = label.replace(" − ", "-")
        print(f"  {console_label}: [{formatted}]")

    print("\nAUDIT TABLE:")
    print(f"{'Contrast':<10} {'Mean':>12} {'Sample SD':>12} {'95% t-CI':>31} {'Positive':>10}")
    for label, _, _, _ in CONTRASTS:
        result = stats[label]
        ci = result["ci"]
        assert isinstance(ci, tuple)
        console_label = label.replace(" − ", "-")
        ci_text = f"[{ci[0]:.12f}, {ci[1]:.12f}]"
        positive_text = f"{result['positive']}/{len(SEEDS)}"
        print(
            f"{console_label:<10} {float(result['mean']):>12.9f} "
            f"{float(result['sd']):>12.9f} {ci_text:>31} {positive_text:>10}"
        )


def write_traceability_csv(
    values: dict[str, dict[int, float]], deltas: dict[str, np.ndarray]
) -> Path:
    """Write the exact plotted observations and their source-level components."""
    path = OUTPUT_STEM.with_name(OUTPUT_STEM.name + "_data.csv")
    columns = [
        "seed",
        "A0_mAP50_95",
        "A1_mAP50_95",
        "A2_mAP50_95",
        "delta_A1_A0",
        "delta_A2_A0",
        "delta_A1_A2",
    ]
    label_by_column = {column: label for label, _, _, column in CONTRASTS}
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for index, seed in enumerate(SEEDS):
            writer.writerow(
                {
                    "seed": seed,
                    "A0_mAP50_95": repr(values["A0"][seed]),
                    "A1_mAP50_95": repr(values["A1"][seed]),
                    "A2_mAP50_95": repr(values["A2"][seed]),
                    **{
                        column: repr(float(deltas[label_by_column[column]][index]))
                        for column in label_by_column
                    },
                }
            )
    return path.resolve()


def plot_figure(
    deltas: dict[str, np.ndarray],
    stats: dict[str, dict[str, float | int | tuple[float, float]]],
) -> list[Path]:
    """Create one compact publication-style panel in PDF, PNG, and SVG."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.0,
            "axes.labelsize": 10.0,
            "xtick.labelsize": 9.0,
            "ytick.labelsize": 8.5,
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )

    fig, ax = plt.subplots(figsize=(6.8, 4.0), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    colors = ("#4F6D8A", "#6B7D5A", "#9A7250")
    offsets = np.linspace(-0.10, 0.10, len(SEEDS))
    all_extrema: list[float] = [0.0]

    for x, ((label, _, _, _), color) in enumerate(zip(CONTRASTS, colors)):
        paired = deltas[label]
        result = stats[label]
        mean = float(result["mean"])
        ci = result["ci"]
        assert isinstance(ci, tuple)

        ax.scatter(
            x + offsets,
            paired,
            s=32,
            facecolors="white",
            edgecolors=color,
            linewidths=1.15,
            zorder=3,
        )
        ax.errorbar(
            x,
            mean,
            yerr=np.asarray([[mean - ci[0]], [ci[1] - mean]]),
            fmt="D",
            markersize=5.5,
            markerfacecolor="#202020",
            markeredgecolor="white",
            markeredgewidth=0.5,
            ecolor="#202020",
            elinewidth=1.35,
            capsize=4.0,
            capthick=1.35,
            zorder=4,
        )
        all_extrema.extend(paired.tolist())
        all_extrema.extend(ci)

    ax.axhline(0.0, color="#555555", linewidth=1.0, linestyle="--", zorder=1)
    ax.set_xticks(range(len(CONTRASTS)))
    ax.set_xticklabels([item[0] for item in CONTRASTS])
    ax.set_ylabel("Paired Δ mAP50–95")
    ax.set_xlim(-0.43, len(CONTRASTS) - 0.57)

    data_min, data_max = min(all_extrema), max(all_extrema)
    span = data_max - data_min
    padding = max(0.008, 0.10 * span)
    ax.set_ylim(data_min - padding, data_max + padding)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.02f"))
    ax.grid(axis="y", color="#D8D8D8", linewidth=0.6, alpha=0.75, zorder=0)
    ax.tick_params(axis="x", length=0, pad=7)
    ax.tick_params(axis="y", direction="out", length=3, width=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#555555")
    ax.spines["bottom"].set_color("#555555")

    outputs = [OUTPUT_STEM.with_suffix(suffix) for suffix in (".pdf", ".png", ".svg")]
    fig.savefig(outputs[0], bbox_inches="tight", facecolor="white")
    fig.savefig(outputs[1], dpi=400, bbox_inches="tight", facecolor="white")
    fig.savefig(outputs[2], bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return [path.resolve() for path in outputs]


def main() -> None:
    values, sources = load_formal_metrics()
    deltas, stats = calculate(values)
    print_audit(values, sources, deltas, stats)
    validate_controls(stats)
    print("\nCONSISTENCY CONTROLS: PASS (agreement at six-decimal rounding).")

    # Output creation occurs only after source and consistency validation pass.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = write_traceability_csv(values, deltas)
    figure_paths = plot_figure(deltas, stats)

    print("\nCREATED FILES:")
    for path in [*figure_paths, csv_path]:
        print(f"  {path}")


if __name__ == "__main__":
    main()
