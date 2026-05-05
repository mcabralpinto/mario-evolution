#!/usr/bin/env python3
import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def read_summary_csv(path: Path):
    rows = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                {
                    "generation": int(r["generation"]),
                    "mean_height": float(r["mean_height"]),
                    "mean_fitness": float(r["mean_fitness"]),
                    "std_fitness": float(r["std_fitness"]),
                    "max_fitness": float(r["max_fitness"]),
                    "min_fitness": float(r["min_fitness"]),
                }
            )
    rows.sort(key=lambda r: r["generation"])
    return rows


def read_individual_csv(path: Path):
    by_gen = defaultdict(list)
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            g = int(r["generation"])
            by_gen[g].append(float(r["fitness"]))
    return by_gen


def stats_from_individuals(by_gen, generations):
    mean_fit = []
    std_fit = []
    max_fit = []
    min_fit = []
    for g in generations:
        vals = np.array(by_gen.get(int(g), []), dtype=float)
        if vals.size == 0:
            mean_fit.append(np.nan)
            std_fit.append(np.nan)
            max_fit.append(np.nan)
            min_fit.append(np.nan)
            continue
        mean_fit.append(float(np.mean(vals)))
        std_fit.append(float(np.std(vals)))
        max_fit.append(float(np.max(vals)))
        min_fit.append(float(np.min(vals)))
    return (
        np.array(mean_fit, dtype=float),
        np.array(std_fit, dtype=float),
        np.array(max_fit, dtype=float),
        np.array(min_fit, dtype=float),
    )


def elite_std_per_generation(by_gen, generations, top_k=10):
    out = []
    for g in generations:
        vals = sorted(by_gen.get(g, []), reverse=True)
        if not vals:
            out.append(0.0)
            continue
        k = min(top_k, len(vals))
        elite = vals[:k]
        out.append(float(np.std(elite)))
    return np.array(out, dtype=float)


def build_split_scale(values, neg_region=0.55, pos_region=0.45):
    arr = np.asarray(values, dtype=float)
    valid = ~np.isnan(arr)
    has_neg = np.any(valid & (arr < 0))
    has_pos = np.any(valid & (arr > 0))
    if not (has_neg and has_pos):
        return None

    neg_bottom = float(np.nanmin(np.concatenate([arr[arr < 0], np.array([0.0])])))
    pos_top = float(np.nanmax(np.concatenate([arr[arr > 0], np.array([0.0])])))
    neg_span = max(1.0, abs(neg_bottom))
    pos_span = max(1.0, pos_top)

    def transform(y):
        y_arr = np.asarray(y, dtype=float)
        out = np.full_like(y_arr, np.nan, dtype=float)
        mask = ~np.isnan(y_arr)
        neg = mask & (y_arr < 0)
        pos = mask & (y_arr >= 0)
        out[neg] = y_arr[neg] * (neg_region / neg_span)
        out[pos] = y_arr[pos] * (pos_region / pos_span)
        return out

    y_min = -neg_region * 1.08
    y_max = pos_region * 1.08
    neg_ticks = np.linspace(neg_bottom, 0.0, 5)
    pos_ticks = np.linspace(0.0, pos_top, 5)
    tick_values = np.unique(np.concatenate([neg_ticks, pos_ticks]))
    tick_positions = transform(tick_values)
    tick_labels = [f"{v:.2e}" if abs(v) >= 1e4 else f"{v:.0f}" for v in tick_values]
    zero_rel = (0.0 - y_min) / (y_max - y_min)

    return {
        "transform": transform,
        "y_lim": (y_min, y_max),
        "tick_positions": tick_positions,
        "tick_labels": tick_labels,
        "zero_rel": zero_rel,
    }


def apply_split_scale_axis(ax, split_scale):
    ax.set_ylim(*split_scale["y_lim"])
    ax.set_yticks(split_scale["tick_positions"])
    ax.set_yticklabels(split_scale["tick_labels"])
    ax.axhline(0.0, color="black", linestyle="--", linewidth=1.2, alpha=0.8)

    d = 0.012
    y_break = split_scale["zero_rel"]
    kwargs = dict(transform=ax.transAxes, color="k", clip_on=False, linewidth=1.0)
    ax.plot((-d, +d), (y_break - d, y_break + d), **kwargs)
    ax.plot((-d, +d), (y_break - 2 * d, y_break), **kwargs)


def plot_mean_max_with_bounds(summary_rows, by_gen, out_path: Path, top_k=10):
    gens = np.array([r["generation"] for r in summary_rows], dtype=int)
    mean_fit, mean_std, max_fit, min_fit = stats_from_individuals(by_gen, gens)
    max_std = elite_std_per_generation(by_gen, gens, top_k=top_k)

    # Clip spread bands to observed fitness range for each generation.
    mean_low = np.maximum(mean_fit - mean_std, min_fit)
    mean_high = np.minimum(mean_fit + mean_std, max_fit)
    max_low = np.maximum(max_fit - max_std, min_fit)

    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.plot(gens, mean_fit, color="tab:blue", marker="o", linewidth=2.5, label="Mean fitness", zorder=3)
    ax.fill_between(gens, mean_low, mean_high, color="tab:blue", alpha=0.15, label="Mean ±std (clipped to min/max)", zorder=1)

    ax.plot(gens, max_fit, color="tab:red", marker="s", linewidth=2.5, label="Max fitness", zorder=3)
    ax.fill_between(gens, max_low, max_fit, color="tab:red", alpha=0.15, label=f"Max spread (top-{top_k} elite std, downward)", zorder=1)

    ax.set_xlabel("Generation", fontsize=11)
    ax.set_ylabel("Fitness", fontsize=11)
    ax.set_title(f"Mean vs max fitness across generations with std bounds", fontsize=12, fontweight="bold")
    ax.grid(alpha=0.3, linestyle="--")
    ax.legend(loc="best", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def plot_mean_max_dual_axis(summary_rows, by_gen, out_path: Path, top_k=10):
    gens = np.array([r["generation"] for r in summary_rows], dtype=int)
    mean_fit, mean_std, max_fit, min_fit = stats_from_individuals(by_gen, gens)
    max_std = elite_std_per_generation(by_gen, gens, top_k=top_k)

    mean_low = np.maximum(mean_fit - mean_std, min_fit)
    mean_high = np.minimum(mean_fit + mean_std, max_fit)
    max_low = np.maximum(max_fit - max_std, np.nanpercentile(max_fit, 5))

    fig, ax1 = plt.subplots(figsize=(12, 6.5))
    ax2 = ax1.twinx()

    l1 = ax1.plot(gens, mean_fit, color="tab:blue", marker="o", linewidth=2.2, label="Mean fitness", zorder=3)
    ax1.fill_between(gens, mean_low, mean_high, color="tab:blue", alpha=0.14, zorder=1)
    l2 = ax2.plot(gens, max_fit, color="tab:red", marker="s", linewidth=2.2, label="Max fitness", zorder=3)
    ax2.fill_between(gens, max_low, max_fit, color="tab:red", alpha=0.14, zorder=1)

    ax1.set_xlabel("Generation", fontsize=11)
    ax1.set_ylabel("Mean fitness", fontsize=11, color="tab:blue")
    ax2.set_ylabel("Max fitness", fontsize=11, color="tab:red")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax2.tick_params(axis="y", labelcolor="tab:red")
    ax1.set_title("Mean and max fitness across generations (dual-axis view)", fontsize=12, fontweight="bold")
    ax1.grid(alpha=0.3, linestyle="--")

    lines = l1 + l2
    ax1.legend(lines, [l.get_label() for l in lines], loc="best")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def plot_max_fitness_line(summary_rows, by_gen, out_path: Path, top_k=10):
    gens = np.array([r["generation"] for r in summary_rows], dtype=int)
    mean_fit, mean_std, max_fit, min_fit = stats_from_individuals(by_gen, gens)
    max_std = elite_std_per_generation(by_gen, gens, top_k=top_k)
    mean_low = np.maximum(mean_fit - mean_std, min_fit)
    mean_high = np.minimum(mean_fit + mean_std, max_fit)
    max_low = np.maximum(max_fit - max_std, min_fit)

    fig, ax = plt.subplots(figsize=(11, 6.8))
    split_values = np.concatenate([mean_low, mean_high, max_low, max_fit])
    split_scale = build_split_scale(split_values)

    if split_scale is not None:
        t = split_scale["transform"]
        ax.plot(gens, t(mean_fit), color="tab:blue", marker="o", linewidth=2.4, label="Mean fitness", zorder=3)
        ax.fill_between(gens, t(mean_low), t(mean_high), color="tab:blue", alpha=0.15, label="Mean ±std (clipped to min/max)", zorder=1)
        ax.plot(gens, t(max_fit), color="tab:red", marker="s", linewidth=2.4, label="Max fitness", zorder=3)
        ax.fill_between(gens, t(max_low), t(max_fit), color="tab:red", alpha=0.15, label=f"Max spread (top-{top_k} elite std, downward)", zorder=1)
        apply_split_scale_axis(ax, split_scale)
        fig.suptitle(
            f"Mean and max fitness per generation (single plot with split y-scale at 0)\nStd bounds shown for both mean and max",
            fontsize=12,
            fontweight="bold",
        )
    else:
        ax.plot(gens, mean_fit, color="tab:blue", marker="o", linewidth=2.4, label="Mean fitness", zorder=3)
        ax.fill_between(gens, mean_low, mean_high, color="tab:blue", alpha=0.15, label="Mean ±std (clipped to min/max)", zorder=1)
        ax.plot(gens, max_fit, color="tab:red", marker="s", linewidth=2.4, label="Max fitness", zorder=3)
        ax.fill_between(gens, max_low, max_fit, color="tab:red", alpha=0.15, label=f"Max spread (top-{top_k} elite std, downward)", zorder=1)
        ax.axhline(0.0, color="black", linestyle="--", linewidth=1.2, alpha=0.8)
        fig.suptitle(
            f"Mean and max fitness per generation\nStd bounds shown for both mean and max",
            fontsize=12,
            fontweight="bold",
        )

    ax.set_xlabel("Generation")
    ax.set_ylabel("Fitness")
    ax.grid(alpha=0.25, linestyle="--")
    ax.legend(loc="best")
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.95])
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def plot_colored_height_relationship(summary_rows, out_path: Path):
    gens = np.array([r["generation"] for r in summary_rows], dtype=int)
    mean_h = np.array([r["mean_height"] for r in summary_rows], dtype=float)
    # Keep mean/max from summary here only for this color-comparison view.
    mean_fit = np.array([r["mean_fitness"] for r in summary_rows], dtype=float)
    max_fit = np.array([r["max_fitness"] for r in summary_rows], dtype=float)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))

    # Left: Mean fitness across generations (colored by height) with split y-scale if needed.
    split_mean = build_split_scale(mean_fit)
    y_mean = split_mean["transform"](mean_fit) if split_mean is not None else mean_fit
    ax1.plot(gens, y_mean, color="tab:blue", linewidth=2.5, marker="o", markersize=6, label="Mean fitness", zorder=2)
    scatter1 = ax1.scatter(gens, y_mean, c=mean_h, cmap="viridis", s=100, edgecolors="black", linewidth=0.5, zorder=3)
    ax1.set_xlabel("Generation", fontsize=11)
    ax1.set_ylabel("Mean fitness (split scale)" if split_mean is not None else "Mean fitness", fontsize=11)
    ax1.set_title("Mean fitness across generations\n(colored by tree height)", fontsize=12, fontweight="bold")
    ax1.grid(alpha=0.3, linestyle="--")
    if split_mean is not None:
        apply_split_scale_axis(ax1, split_mean)
    cbar1 = fig.colorbar(scatter1, ax=ax1)
    cbar1.set_label("Mean tree height", fontsize=10)

    # Right: Max fitness across generations (colored by height) with split y-scale if needed.
    split_max = build_split_scale(max_fit)
    y_max = split_max["transform"](max_fit) if split_max is not None else max_fit
    ax2.plot(gens, y_max, color="tab:red", linewidth=2.5, marker="s", markersize=6, label="Max fitness", zorder=2)
    scatter2 = ax2.scatter(gens, y_max, c=mean_h, cmap="plasma", s=100, edgecolors="black", linewidth=0.5, zorder=3)
    ax2.set_xlabel("Generation", fontsize=11)
    ax2.set_ylabel("Max fitness (split scale)" if split_max is not None else "Max fitness", fontsize=11)
    ax2.set_title("Max fitness across generations\n(colored by tree height)", fontsize=12, fontweight="bold")
    ax2.grid(alpha=0.3, linestyle="--")
    if split_max is not None:
        apply_split_scale_axis(ax2, split_max)
    cbar2 = fig.colorbar(scatter2, ax=ax2)
    cbar2.set_label("Mean tree height", fontsize=10)

    fig.suptitle("Fitness progression with tree height relationship", y=1.01, fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Plot requested charts from reevaluation CSVs.")
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=Path("data/search_space_analysis_full_reeval/generation_summary_full_reeval.csv"),
    )
    parser.add_argument(
        "--individual-csv",
        type=Path,
        default=Path("data/search_space_analysis_full_reeval/individual_metrics_full_reeval.csv"),
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("data/search_space_analysis_full_reeval"),
    )
    parser.add_argument(
        "--elite-k",
        type=int,
        default=10,
        help="Top-k individuals per generation used to estimate max-fitness std bound.",
    )
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    summary_rows = read_summary_csv(args.summary_csv)
    by_gen = read_individual_csv(args.individual_csv)

    plot1 = args.outdir / "line_mean_vs_max_fitness_with_std_bounds.png"
    plot2 = args.outdir / "colored_comparison_height_vs_mean_and_max_fitness.png"
    plot3 = args.outdir / "line_mean_vs_max_fitness_dual_axis.png"
    plot4 = args.outdir / "line_max_fitness_from_individual_csv.png"

    plot_mean_max_with_bounds(summary_rows, by_gen, plot1, top_k=args.elite_k)
    plot_colored_height_relationship(summary_rows, plot2)
    plot_mean_max_dual_axis(summary_rows, by_gen, plot3, top_k=args.elite_k)
    plot_max_fitness_line(summary_rows, by_gen, plot4, top_k=args.elite_k)

    print(f"Saved: {plot1}")
    print(f"Saved: {plot2}")
    print(f"Saved: {plot3}")
    print(f"Saved: {plot4}")


if __name__ == "__main__":
    main()
