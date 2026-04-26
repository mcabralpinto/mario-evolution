"""
Plot win rate vs generation for a series of GP checkpoints.

Edit CHECKPOINTS below: list of (checkpoint_path, generation_number) tuples.
"""
import sys
import pickle
import io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
from tqdm import tqdm

from src.mario_gp import compile_individual
from src.evaluate_best_agent import evaluate_from_code


class _CheckpointUnpickler(pickle.Unpickler):
    """Compatibility loader for checkpoints pickled from mario_gp.py as __main__."""

    def find_class(self, module, name):
        if module == "__main__":
            module = "src.mario_gp"
        return super().find_class(module, name)


def _load_checkpoint(path):
    with open(path, "rb") as f:
        data = f.read()

    try:
        return pickle.loads(data)
    except AttributeError:
        # Older checkpoints reference symbols as __main__.* from mario_gp.py.
        return _CheckpointUnpickler(io.BytesIO(data)).load()

# --- configure here ---
SEED_CHECKPOINTS_DIR = Path("data/seed_checkpoints")
SEED_START = 10000
SEED_N = 100
DISPLAY_DIFFICULTIES = 3
# ----------------------

DIFF_COLORS = ["green", "yellow", "red"]
DIFF_LABELS = ["Difficulty 0", "Difficulty 1", "Difficulty 2"]


def extract_best_code(checkpoint_path):
    ckpt = _load_checkpoint(checkpoint_path)
    hof = ckpt["hof"]
    best = hof[0]
    return compile_individual(best)


def save_best_to_gp_mario_best(code: str, overall_wr: float):
    out_path = Path("data/gp_best_agents/gp_mario_best.py")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = f"# Evolved Mario Controller\n# Win Rate: {overall_wr:.4f}\n"
    out_path.write_text(header + "\n" + code.lstrip())
    print(f"Saved best agent (win rate {overall_wr:.2%}) to '{out_path}'")


def discover_checkpoints(directory: Path):
    """Return (path, generation) pairs from checkpoint_gen_N.pkl files, sorted by N."""
    pairs = []
    for p in directory.glob("checkpoint_gen_*.pkl"):
        try:
            gen = int(p.stem.split("_")[-1])
            pairs.append((str(p), gen))
        except ValueError:
            pass
    return sorted(pairs, key=lambda x: x[1])


def main():
    checkpoints = discover_checkpoints(SEED_CHECKPOINTS_DIR)
    if not checkpoints:
        print(f"No checkpoints found in '{SEED_CHECKPOINTS_DIR}'.")
        return

    print(f"Found {len(checkpoints)} checkpoint(s): generations {[g for _, g in checkpoints]}")

    generations = []
    win_rates = []
    diff_win_rates = {d: [] for d in range(DISPLAY_DIFFICULTIES)}
    best_overall = -1.0
    best_code = None

    for path, gen in tqdm(checkpoints, desc="Checkpoints"):
        print(f"\n--- Evaluating checkpoint gen={gen}: {path} ---")
        code = extract_best_code(path)
        overall_wr, per_diff = evaluate_from_code(code, seed_start=SEED_START, seed_n=SEED_N,
                                                  display_difficulties=DISPLAY_DIFFICULTIES)
        print(f"  Win rate: {overall_wr:.2%}  |  " +
              "  ".join(f"D{d}: {per_diff[d]:.2%}" for d in range(DISPLAY_DIFFICULTIES)))
        generations.append(gen)
        win_rates.append(overall_wr * 100)
        for d in range(DISPLAY_DIFFICULTIES):
            diff_win_rates[d].append(per_diff.get(d, 0.0) * 100)

        if overall_wr > best_overall:
            best_overall = overall_wr
            best_code = code

    if best_code is not None:
        save_best_to_gp_mario_best(best_code, best_overall)

    plt.figure(figsize=(10, 6))
    plt.plot(generations, win_rates, marker="o", linewidth=2, label="Overall", color="blue")
    for d in range(DISPLAY_DIFFICULTIES):
        plt.plot(generations, diff_win_rates[d], marker="o", linewidth=1.5, linestyle="--",
                 label=DIFF_LABELS[d], color=DIFF_COLORS[d])
    plt.xlabel("Generation")
    plt.ylabel("Win Rate (%)")
    plt.title("Best Agent Win Rate vs Generation")
    plt.legend()
    plt.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.savefig("data/winrate_vs_gen.png", dpi=150)
    print("\nPlot saved to data/winrate_vs_gen.png")
    plt.show()


if __name__ == "__main__":
    main()
