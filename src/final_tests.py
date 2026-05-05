"""
Run multiple seeded GP training runs followed by best-agent extraction.

Seeds start at 30000 by default. Each run gets the next seed in sequence.

Usage:
    python -m src.final_tests --runs 5
    python -m src.final_tests --runs 3 --hunter
    python -m src.final_tests --runs 3 --thief --gen 200 --pop 100
    python -m src.final_tests --runs 3 --start-seed 40000
    python -m src.final_tests --eval --thief          # evaluate existing agents only
    python -m src.final_tests --runs 3 --thief --eval # train then evaluate
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

DEFAULT_SEED_START = 30000


def _read_agent_code(path: Path) -> str:
    lines = path.read_text().splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.strip().startswith("def "):
            return "".join(lines[i:])
    return path.read_text()


def _eval_agents(task_name: str, task_cls, data_dir: Path = Path("data")):
    from src.evaluate_best_agent import evaluate_from_code

    agents_dir = data_dir / "agents"
    agent_files = sorted(
        agents_dir.glob(f"{task_name}_seed_*.py"),
        key=lambda p: int(re.search(r"_seed_(\d+)", p.stem).group(1)),
    )

    if not agent_files:
        print(f"No agents found matching '{task_name}_seed_*.py' in '{agents_dir}'")
        return

    print(f"\nEvaluating {len(agent_files)} {task_name} agent(s)...")

    agents_data = {}
    for path in agent_files:
        print(f"\n--- {path.name} ---")
        code = _read_agent_code(path)
        result = evaluate_from_code(code, task_cls=task_cls)
        agents_data[path.stem] = {
            "win_rate": result.win_rate,
            "avg_progress": result.avg_progress,
            "avg_kills": result.avg_kills,
            "avg_coins": result.avg_coins,
            "win_rate_per_diff": {str(k): v for k, v in result.win_rate_per_diff.items()},
            "conditional_win_rate_per_diff": {str(k): v for k, v in result.conditional_win_rate_per_diff.items()},
        }
        print(f"  win_rate={result.win_rate:.4f}  avg_progress={result.avg_progress:.2f}"
              f"  avg_kills={result.avg_kills:.4f}  avg_coins={result.avg_coins:.4f}")

    stat_keys = ["win_rate", "avg_progress", "avg_kills", "avg_coins"]
    summary = {
        k: {
            "mean": float(np.mean([r[k] for r in agents_data.values()])),
            "std":  float(np.std( [r[k] for r in agents_data.values()])),
        }
        for k in stat_keys
    }

    print("\n--- Summary ---")
    for k, v in summary.items():
        print(f"  {k}: mean={v['mean']:.4f}  std={v['std']:.4f}")

    run_entry = {
        "task": task_name,
        "timestamp": datetime.datetime.now().isoformat(),
        "agents": agents_data,
        "summary": summary,
    }

    out_path = data_dir / "results.json"
    existing = {"runs": []}
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text())
        except json.JSONDecodeError:
            pass
    existing.setdefault("runs", []).append(run_entry)
    out_path.write_text(json.dumps(existing, indent=2))
    print(f"\nResults appended to '{out_path}'")


def main():
    parser = argparse.ArgumentParser(description="Run N seeded GP training runs + best-agent extraction.")
    parser.add_argument("--runs", type=int, default=1, help="Number of training runs")
    parser.add_argument("--start-seed", type=int, default=DEFAULT_SEED_START,
                        help=f"Seed for the first run (default: {DEFAULT_SEED_START})")
    parser.add_argument("--eval", action="store_true",
                        help="After training, evaluate all matching agents in data/agents/ and write data/results.json")
    parser.add_argument("--hunter", action="store_true", help="Train and evaluate with HunterTask")
    parser.add_argument("--thief", action="store_true", help="Train and evaluate with ThiefTask")
    parser.add_argument("--random", action="store_true",
                        help="Use random search instead of GP evolution; outputs saved as random_seed_N.py")

    # mario_gp pass-through args
    parser.add_argument("--gen", type=int, default=300, help="Number of generations (default: mario_gp default)")
    parser.add_argument("--pop", type=int, default=100, help="Population size (default: mario_gp default)")
    parser.add_argument("--max-height", type=int, default=None)
    parser.add_argument("--seed-pool-size", type=int, default=None)
    parser.add_argument("--seed-rotation", type=int, default=None)
    parser.add_argument("--difficulty-shift", type=int, default=None)
    parser.add_argument("--static-operators", action="store_true")
    parser.add_argument("--mode", choices=["evolution", "random"], default=None)

    args = parser.parse_args()

    if args.hunter and args.thief:
        parser.error("--hunter and --thief are mutually exclusive")
    if args.random and args.mode is not None:
        parser.error("--random and --mode are mutually exclusive")

    task_flags = ["--hunter"] if args.hunter else (["--thief"] if args.thief else [])

    for i in range(args.runs):
        seed = args.start_seed + i
        print(f"\n{'='*60}")
        print(f"Run {i + 1}/{args.runs}  |  seed={seed}")
        print(f"{'='*60}\n")

        gp_cmd = [sys.executable, "-m", "src.mario_gp", "--seed", str(seed)] + task_flags
        if args.gen is not None:
            gp_cmd += ["--gen", str(args.gen)]
        if args.pop is not None:
            gp_cmd += ["--pop", str(args.pop)]
        if args.max_height is not None:
            gp_cmd += ["--max_height", str(args.max_height)]
        if args.seed_pool_size is not None:
            gp_cmd += ["--seed-pool-size", str(args.seed_pool_size)]
        if args.seed_rotation is not None:
            gp_cmd += ["--seed-rotation", str(args.seed_rotation)]
        if args.difficulty_shift is not None:
            gp_cmd += ["--difficulty-shift", str(args.difficulty_shift)]
        if args.static_operators:
            gp_cmd.append("--static-operators")
        if args.random:
            gp_cmd += ["--mode", "random-checkpoint"]
        elif args.mode is not None:
            gp_cmd += ["--mode", args.mode]

        print(f"[Training] {' '.join(gp_cmd)}")
        subprocess.run(gp_cmd, check=True)

        gba_flags = task_flags + (["--random"] if args.random else [])
        gba_cmd = [sys.executable, "-m", "src.get_best_agent", "--seed", str(seed), "--no-show"] + gba_flags
        print(f"\n[Best agent] {' '.join(gba_cmd)}")
        subprocess.run(gba_cmd, check=True)

    if args.runs > 0:
        print(f"\nAll {args.runs} run(s) complete.")

    if args.eval:
        from src.tasks import HunterTask, RunnerTask, ThiefTask
        task_name = "random" if args.random else ("hunter" if args.hunter else ("thief" if args.thief else "runner"))
        task_cls = HunterTask if args.hunter else (ThiefTask if args.thief else RunnerTask)
        _eval_agents(task_name, task_cls)


if __name__ == "__main__":
    main()
