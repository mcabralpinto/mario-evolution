"""
Plot win rate vs generation for a series of GP checkpoints.

Edit CHECKPOINTS below: list of (checkpoint_path, generation_number) tuples.
"""
import sys
import argparse
import pickle
import io
import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
from tqdm import tqdm

from src.mario_gp import compile_individual
from src.evaluate_best_agent import evaluate_from_code
from src.tasks import RunnerTask, HunterTask, ThiefTask


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
SEED_N = 500
DISPLAY_DIFFICULTIES = 3
# ----------------------

DIFF_COLORS = ["green", "yellow", "red"]
DIFF_LABELS = ["Difficulty 0", "Difficulty 1", "Difficulty 2"]


def extract_best_code(checkpoint_path):
    ckpt = _load_checkpoint(checkpoint_path)
    hof = ckpt["hof"]
    best = hof[0]
    return compile_individual(best)


def save_best_to_gp_mario_best(code: str, result, out_path: Path = None):
    if out_path is None:
        out_path = Path("data/gp_best_agents/gp_mario_best.py")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = (f"# Evolved Mario Controller\n"
              f"# Win Rate: {result.win_rate:.4f}\n"
              f"# Avg Progress (unbeaten): {result.avg_progress:.2f}\n"
              f"# Avg Kills: {result.avg_kills:.4f}\n"
              f"# Avg Coins: {result.avg_coins:.4f}\n")
    print(f"Saved best agent to '{out_path}' "
          f"(wr={result.win_rate:.2%}, progress={result.avg_progress:.1f}, "
          f"kills={result.avg_kills:.4f}, coins={result.avg_coins:.4f})")
    out_path.write_text(header + "\n" + code.lstrip())


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
    parser = argparse.ArgumentParser(description="Evaluate GP checkpoints and select the best agent.")
    parser.add_argument("--hunter", action="store_true",
                        help="Hunter mode: select by avg_kills + 0.25*avg_coins, plot kills and coins.")
    parser.add_argument("--thief", action="store_true",
                        help="Thief mode: select by avg_coins, plot coins.")
    parser.add_argument("--seed", type=int, default=None,
                        help="Training seed (used for output file naming).")
    parser.add_argument("--no-show", action="store_true",
                        help="Save chart without displaying it (non-blocking).")
    args = parser.parse_args()
    if args.hunter and args.thief:
        parser.error("--hunter and --thief are mutually exclusive")

    task_name = "hunter" if args.hunter else ("thief" if args.thief else "runner")
    if args.seed is not None:
        chart_path = Path("data/charts") / f"{task_name}_seed_{args.seed}.png"
        agent_out_path = Path("data/agents") / f"{task_name}_seed_{args.seed}.py"
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_path = Path("data/charts") / f"{task_name}_{timestamp}.png"
        agent_out_path = None
    chart_path.parent.mkdir(parents=True, exist_ok=True)

    checkpoints = discover_checkpoints(SEED_CHECKPOINTS_DIR)
    if not checkpoints:
        print(f"No checkpoints found in '{SEED_CHECKPOINTS_DIR}'.")
        return

    print(f"Found {len(checkpoints)} checkpoint(s): generations {[g for _, g in checkpoints]}")

    task_cls = HunterTask if args.hunter else (ThiefTask if args.thief else RunnerTask)
    generations = []
    best_code = None
    best_result = None

    if args.hunter:
        avg_kills_list = []
        win_rates = []
        best_score = -1.0

        for path, gen in tqdm(checkpoints, desc="Checkpoints"):
            print(f"\n--- Evaluating checkpoint gen={gen}: {path} ---")
            code = extract_best_code(path)
            result = evaluate_from_code(code, task_cls=task_cls,
                                        seed_start=SEED_START, seed_n=SEED_N,
                                        display_difficulties=DISPLAY_DIFFICULTIES)
            print(f"  Win rate: {result.win_rate:.2%}  |  avg_kills: {result.avg_kills:.4f}"
                  f"  |  avg_progress: {result.avg_progress:.1f}  |  avg_coins: {result.avg_coins:.4f}")
            generations.append(gen)
            avg_kills_list.append(result.avg_kills)
            win_rates.append(result.win_rate * 100)

            if result.avg_kills > best_score:
                best_score = result.avg_kills
                best_result = result
                best_code = code

        if best_code is not None:
            save_best_to_gp_mario_best(best_code, best_result, out_path=agent_out_path)

        _, ax1 = plt.subplots(figsize=(10, 5))
        ax2 = ax1.twinx()

        ax1.plot(generations, avg_kills_list, marker="o", linewidth=2, color="red", label="Avg Kills")
        ax2.plot(generations, win_rates, marker="o", linewidth=2, color="blue", linestyle="--", label="Win Rate (%)")

        ax1.set_xlabel("Generation")
        ax1.set_ylabel("Avg Kills per Episode", color="red")
        ax1.tick_params(axis="y", labelcolor="red")
        ax2.set_ylabel("Win Rate (%)", color="blue")
        ax2.tick_params(axis="y", labelcolor="blue")
        ax1.grid(True, alpha=0.4)

        lines = ax1.get_lines() + ax2.get_lines()
        ax1.legend(lines, [l.get_label() for l in lines], loc="upper left")

        plt.title("Hunter Mode: Avg Kills & Win Rate vs Generation")
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150)
        print(f"\nPlot saved to {chart_path}")
        if not args.no_show:
            plt.show()

    elif args.thief:
        avg_coins_list = []
        win_rates = []
        best_score = -1.0

        for path, gen in tqdm(checkpoints, desc="Checkpoints"):
            print(f"\n--- Evaluating checkpoint gen={gen}: {path} ---")
            code = extract_best_code(path)
            result = evaluate_from_code(code, task_cls=task_cls,
                                        seed_start=SEED_START, seed_n=SEED_N,
                                        display_difficulties=DISPLAY_DIFFICULTIES)
            print(f"  Win rate: {result.win_rate:.2%}  |  avg_coins: {result.avg_coins:.4f}"
                  f"  |  avg_progress: {result.avg_progress:.1f}  |  avg_kills: {result.avg_kills:.4f}")
            generations.append(gen)
            avg_coins_list.append(result.avg_coins)
            win_rates.append(result.win_rate * 100)

            if result.avg_coins > best_score:
                best_score = result.avg_coins
                best_result = result
                best_code = code

        if best_code is not None:
            save_best_to_gp_mario_best(best_code, best_result, out_path=agent_out_path)

        _, ax1 = plt.subplots(figsize=(10, 5))
        ax2 = ax1.twinx()

        ax1.plot(generations, avg_coins_list, marker="o", linewidth=2, color="gold", label="Avg Coins")
        ax2.plot(generations, win_rates, marker="o", linewidth=2, color="blue", linestyle="--", label="Win Rate (%)")

        ax1.set_xlabel("Generation")
        ax1.set_ylabel("Avg Coins per Episode", color="goldenrod")
        ax1.tick_params(axis="y", labelcolor="goldenrod")
        ax2.set_ylabel("Win Rate (%)", color="blue")
        ax2.tick_params(axis="y", labelcolor="blue")
        ax1.grid(True, alpha=0.4)

        lines = ax1.get_lines() + ax2.get_lines()
        ax1.legend(lines, [l.get_label() for l in lines], loc="upper left")

        plt.title("Thief Mode: Avg Coins & Win Rate vs Generation")
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150)
        print(f"\nPlot saved to {chart_path}")
        if not args.no_show:
            plt.show()

    else:
        win_rates = []
        diff_win_rates = {d: [] for d in range(DISPLAY_DIFFICULTIES)}
        best_score = -1.0

        for path, gen in tqdm(checkpoints, desc="Checkpoints"):
            print(f"\n--- Evaluating checkpoint gen={gen}: {path} ---")
            code = extract_best_code(path)
            result = evaluate_from_code(code, task_cls=task_cls,
                                        seed_start=SEED_START, seed_n=SEED_N,
                                        display_difficulties=DISPLAY_DIFFICULTIES)
            print(f"  Win rate: {result.win_rate:.2%}  |  avg_progress: {result.avg_progress:.1f}"
                  f"  |  " + "  ".join(f"D{d}: {result.win_rate_per_diff[d]:.2%}"
                                       for d in range(DISPLAY_DIFFICULTIES)))
            generations.append(gen)
            win_rates.append(result.win_rate * 100)
            for d in range(DISPLAY_DIFFICULTIES):
                diff_win_rates[d].append(result.win_rate_per_diff.get(d, 0.0) * 100)

            if result.win_rate > best_score:
                best_score = result.win_rate
                best_result = result
                best_code = code

        if best_code is not None:
            save_best_to_gp_mario_best(best_code, best_result, out_path=agent_out_path)

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
        plt.savefig(chart_path, dpi=150)
        print(f"\nPlot saved to {chart_path}")
        if not args.no_show:
            plt.show()


if __name__ == "__main__":
    main()
