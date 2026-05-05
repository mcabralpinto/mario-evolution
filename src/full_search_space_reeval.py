#!/usr/bin/env python3
import csv
import hashlib
import io
import itertools
import math
import pickle
import random
import sys
import warnings
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT_DIR = REPO_ROOT / "data" / "seed_checkpoints"
OUTPUT_DIR = REPO_ROOT / "data" / "search_space_analysis_full_reeval"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

warnings.filterwarnings("ignore")

from src.agents import CodeAgent
from src.evaluation import (
    evaluate_population,
    set_task_class,
    set_total_generations,
    terminate_evaluation_pool,
)
from src.mario_gp import compile_individual
from src.tasks import HunterTask, RunnerTask, ThiefTask


class _CheckpointUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "__main__":
            module = "src.mario_gp"
        return super().find_class(module, name)


def load_checkpoint(path: Path):
    raw = path.read_bytes()
    try:
        return pickle.loads(raw)
    except Exception:
        return _CheckpointUnpickler(io.BytesIO(raw)).load()


def discover_checkpoints(directory: Path):
    pairs = []
    for p in directory.glob("checkpoint_gen_*.pkl"):
        try:
            g = int(p.stem.split("_")[-1])
            pairs.append((g, p))
        except ValueError:
            continue
    return [p for _, p in sorted(pairs, key=lambda x: x[0])]


def get_task_class(args):
    if getattr(args, "hunter", False):
        return HunterTask, "hunter"
    if getattr(args, "thief", False):
        return ThiefTask, "thief"
    return RunnerTask, "runner"


def token_sequence(individual):
    seq = []
    for node in individual:
        name = getattr(node, "name", None)
        seq.append(name if name is not None else str(node))
    return tuple(seq)


def estimate_pairwise_token_diversity(token_sequences, max_pairs=1000, seed=42):
    n = len(token_sequences)
    if n < 2:
        return 0.0

    pairs = list(itertools.combinations(range(n), 2))
    if len(pairs) > max_pairs:
        rng = random.Random(seed)
        pairs = rng.sample(pairs, max_pairs)

    distances = []
    for i, j in pairs:
        s1 = " ".join(token_sequences[i])
        s2 = " ".join(token_sequences[j])
        sim = SequenceMatcher(None, s1, s2).ratio()
        distances.append(1.0 - sim)
    return float(np.mean(distances)) if distances else 0.0


def make_heatmap_generation_feature_fitness(
    rows,
    feature_key,
    feature_label,
    out_path,
    bins=24,
    cmap="magma",
):
    gens = sorted({int(r["generation"]) for r in rows})
    features = np.array([float(r[feature_key]) for r in rows], dtype=float)
    fitness = np.array([float(r["fitness"]) for r in rows], dtype=float)
    generations = np.array([int(r["generation"]) for r in rows], dtype=int)

    f_min, f_max = float(np.min(features)), float(np.max(features))
    if math.isclose(f_min, f_max):
        f_max = f_min + 1.0
    edges = np.linspace(f_min, f_max, bins + 1)
    centers = (edges[:-1] + edges[1:]) / 2.0

    z = np.full((bins, len(gens)), np.nan, dtype=float)
    for gx, g in enumerate(gens):
        mask_g = generations == g
        g_features = features[mask_g]
        g_fitness = fitness[mask_g]
        if g_features.size == 0:
            continue
        bidx = np.digitize(g_features, edges, right=False) - 1
        bidx = np.clip(bidx, 0, bins - 1)
        for by in range(bins):
            m = bidx == by
            if np.any(m):
                z[by, gx] = float(np.mean(g_fitness[m]))

    fig, ax = plt.subplots(figsize=(12, 6))
    mesh = ax.pcolormesh(gens, centers, z, shading="nearest", cmap=cmap)
    fig.colorbar(mesh, ax=ax, label="Mean fitness")
    ax.set_xlabel("Generation")
    ax.set_ylabel(feature_label)
    ax.set_title(f"Fitness heatmap: generation vs {feature_label.lower()}")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=170)
    plt.close(fig)


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ckpts = discover_checkpoints(CHECKPOINT_DIR)
    if not ckpts:
        raise SystemExit(f"No checkpoints found in {CHECKPOINT_DIR}")

    print(f"Found {len(ckpts)} checkpoints")

    all_rows = []
    gen_rows = []
    cumulative_unique = set()
    current_task_name = None

    try:
        for idx, ckpt_path in enumerate(ckpts, start=1):
            ckpt = load_checkpoint(ckpt_path)
            gen = int(ckpt["gen"])
            args = ckpt["args"]
            pop = ckpt["pop"]
            seed_pool = ckpt.get("seed_pool", None)

            task_cls, task_name = get_task_class(args)
            if task_name != current_task_name:
                terminate_evaluation_pool()
                set_task_class(task_cls)
                current_task_name = task_name

            ngen = int(getattr(args, "gen", 300))
            difficulty_shift = int(getattr(args, "difficulty_shift", 1))
            base_difficulty = int((gen / max(ngen - 1, 1)) * difficulty_shift)
            set_total_generations(ngen)

            compiled = [compile_individual(ind) for ind in pop]
            fitnesses = evaluate_population(
                CodeAgent,
                compiled,
                generation=gen,
                seed_pool=seed_pool,
                base_difficulty=base_difficulty,
            )
            fitnesses = list(map(float, fitnesses.tolist()))
            if len(fitnesses) != len(pop):
                raise RuntimeError(
                    f"Unexpected fitness length at gen {gen}: {len(fitnesses)} != {len(pop)}"
                )

            token_seqs = [token_sequence(ind) for ind in pop]
            token_div = estimate_pairwise_token_diversity(token_seqs, max_pairs=1000, seed=gen)

            tree_strs = [str(ind) for ind in pop]
            unique_count = len(set(tree_strs))
            sizes = [len(ind) for ind in pop]
            heights = [ind.height for ind in pop]

            for ind_idx, (ind, fit, tree_str) in enumerate(zip(pop, fitnesses, tree_strs)):
                tree_hash = hashlib.sha1(tree_str.encode("utf-8")).hexdigest()[:16]
                cumulative_unique.add(tree_hash)
                all_rows.append(
                    {
                        "checkpoint_file": ckpt_path.name,
                        "generation": gen,
                        "individual_index": ind_idx,
                        "tree_size": len(ind),
                        "tree_height": ind.height,
                        "fitness": float(fit),
                        "tree_hash": tree_hash,
                    }
                )

            gen_rows.append(
                {
                    "checkpoint_file": ckpt_path.name,
                    "generation": gen,
                    "population_size": len(pop),
                    "unique_individuals": unique_count,
                    "uniqueness_ratio": unique_count / len(pop),
                    "cumulative_unique_individuals": len(cumulative_unique),
                    "mean_size": float(np.mean(sizes)),
                    "std_size": float(np.std(sizes)),
                    "mean_height": float(np.mean(heights)),
                    "std_height": float(np.std(heights)),
                    "mean_fitness": float(np.mean(fitnesses)),
                    "std_fitness": float(np.std(fitnesses)),
                    "max_fitness": float(np.max(fitnesses)),
                    "min_fitness": float(np.min(fitnesses)),
                    "token_diversity": token_div,
                    "task": task_name,
                    "base_difficulty": base_difficulty,
                }
            )
            print(
                f"[{idx:02d}/{len(ckpts)}] gen={gen:3d} "
                f"uniq={unique_count:3d}/{len(pop)} "
                f"fit_mean={np.mean(fitnesses):.1f} fit_max={np.max(fitnesses):.1f}"
            )
    finally:
        terminate_evaluation_pool()

    all_rows.sort(key=lambda r: (int(r["generation"]), int(r["individual_index"])))
    gen_rows.sort(key=lambda r: int(r["generation"]))

    write_csv(
        OUTPUT_DIR / "individual_metrics_full_reeval.csv",
        all_rows,
        [
            "checkpoint_file",
            "generation",
            "individual_index",
            "tree_size",
            "tree_height",
            "fitness",
            "tree_hash",
        ],
    )
    write_csv(
        OUTPUT_DIR / "generation_summary_full_reeval.csv",
        gen_rows,
        [
            "checkpoint_file",
            "generation",
            "population_size",
            "unique_individuals",
            "uniqueness_ratio",
            "cumulative_unique_individuals",
            "mean_size",
            "std_size",
            "mean_height",
            "std_height",
            "mean_fitness",
            "std_fitness",
            "max_fitness",
            "min_fitness",
            "token_diversity",
            "task",
            "base_difficulty",
        ],
    )

    gens = np.array([int(r["generation"]) for r in all_rows], dtype=int)
    sizes = np.array([float(r["tree_size"]) for r in all_rows], dtype=float)
    heights = np.array([float(r["tree_height"]) for r in all_rows], dtype=float)
    fitness = np.array([float(r["fitness"]) for r in all_rows], dtype=float)

    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(sizes, fitness, c=gens, cmap="viridis", s=14, alpha=0.6)
    fig.colorbar(sc, ax=ax, label="Generation")
    ax.set_xlabel("Tree size (nodes)")
    ax.set_ylabel("Fitness")
    ax.set_title("Scatter: fitness vs tree size (all reevaluated individuals)")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "scatter_fitness_vs_tree_size_full.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(heights, fitness, c=gens, cmap="plasma", s=14, alpha=0.6)
    fig.colorbar(sc, ax=ax, label="Generation")
    ax.set_xlabel("Tree height")
    ax.set_ylabel("Fitness")
    ax.set_title("Scatter: fitness vs tree height (all reevaluated individuals)")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "scatter_fitness_vs_tree_height_full.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6))
    hb = ax.hexbin(
        sizes,
        heights,
        C=fitness,
        gridsize=26,
        reduce_C_function=np.mean,
        cmap="inferno",
        mincnt=3,
    )
    fig.colorbar(hb, ax=ax, label="Mean fitness")
    ax.set_xlabel("Tree size (nodes)")
    ax.set_ylabel("Tree height")
    ax.set_title("Hexbin: mean fitness over tree-size/tree-height space")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "hexbin_size_height_mean_fitness_full.png", dpi=170)
    plt.close(fig)

    make_heatmap_generation_feature_fitness(
        all_rows,
        feature_key="tree_size",
        feature_label="Tree size (nodes)",
        out_path=OUTPUT_DIR / "heatmap_generation_vs_tree_size_mean_fitness.png",
        bins=24,
        cmap="magma",
    )
    make_heatmap_generation_feature_fitness(
        all_rows,
        feature_key="tree_height",
        feature_label="Tree height",
        out_path=OUTPUT_DIR / "heatmap_generation_vs_tree_height_mean_fitness.png",
        bins=18,
        cmap="cividis",
    )

    g = np.array([int(r["generation"]) for r in gen_rows], dtype=int)
    uniq = np.array([float(r["uniqueness_ratio"]) for r in gen_rows], dtype=float)
    mean_fit = np.array([float(r["mean_fitness"]) for r in gen_rows], dtype=float)
    max_fit = np.array([float(r["max_fitness"]) for r in gen_rows], dtype=float)
    token_div = np.array([float(r["token_diversity"]) for r in gen_rows], dtype=float)
    cum_unique = np.array(
        [int(r["cumulative_unique_individuals"]) for r in gen_rows], dtype=int
    )

    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    ax2 = ax1.twinx()
    l1 = ax1.plot(g, uniq * 100.0, color="teal", marker="o", label="Uniqueness ratio (%)")
    l2 = ax2.plot(g, max_fit, color="crimson", marker="s", label="Max fitness")
    l3 = ax2.plot(g, mean_fit, color="orange", marker="^", label="Mean fitness")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Uniqueness ratio (%)", color="teal")
    ax2.set_ylabel("Fitness", color="crimson")
    ax1.set_title("Generation profile: uniqueness and fitness (full reevaluation)")
    ax1.grid(alpha=0.25)
    lines = l1 + l2 + l3
    ax1.legend(lines, [l.get_label() for l in lines], loc="best")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "line_uniqueness_and_fitness_full.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(g, cum_unique, color="royalblue", marker="o")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Cumulative unique tree hashes")
    ax.set_title("Cumulative explored structural space")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "line_cumulative_unique_trees_full.png", dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(uniq * 100.0, max_fit, c=g, cmap="viridis", s=90 * np.clip(token_div, 0.1, None), alpha=0.8)
    fig.colorbar(sc, ax=ax, label="Generation")
    ax.set_xlabel("Structural uniqueness ratio (%)")
    ax.set_ylabel("Max fitness")
    ax.set_title("Scatter: max fitness vs structural diversity\n(point size ∝ token diversity)")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "scatter_max_fitness_vs_diversity_full.png", dpi=170)
    plt.close(fig)

    summary_txt = OUTPUT_DIR / "summary_full_reeval.txt"
    with summary_txt.open("w") as f:
        f.write("Full reevaluation summary (all individuals, all seed checkpoints)\n")
        f.write("=" * 72 + "\n")
        f.write(f"checkpoints: {len(ckpts)}\n")
        f.write(f"individuals: {len(all_rows)}\n")
        f.write(f"generations: {min(g)}..{max(g)}\n")
        f.write(f"fitness min/max/mean: {fitness.min():.3f} / {fitness.max():.3f} / {fitness.mean():.3f}\n")
        f.write(f"size min/max/mean: {sizes.min():.1f} / {sizes.max():.1f} / {sizes.mean():.1f}\n")
        f.write(f"height min/max/mean: {heights.min():.1f} / {heights.max():.1f} / {heights.mean():.1f}\n")
        f.write(f"uniqueness ratio min/max/mean: {(uniq.min()*100):.2f}% / {(uniq.max()*100):.2f}% / {(uniq.mean()*100):.2f}%\n")
        f.write(f"token diversity min/max/mean: {token_div.min():.4f} / {token_div.max():.4f} / {token_div.mean():.4f}\n")
        f.write(f"cumulative unique trees at end: {cum_unique[-1]}\n")
        f.write("\nGenerated files:\n")
        for p in sorted(OUTPUT_DIR.glob("*")):
            f.write(f"- {p.name}\n")

    print("\nDone.")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Summary file: {summary_txt}")


if __name__ == "__main__":
    main()
