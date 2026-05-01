"""
Run multiple seeded GP training runs followed by best-agent extraction.

Seeds start at 30000. Each run gets the next seed in sequence.

Usage:
    python -m src.final_tests --runs 5
    python -m src.final_tests --runs 3 --hunter
    python -m src.final_tests --runs 3 --thief --gen 200 --pop 100
"""
import argparse
import subprocess
import sys
from pathlib import Path

SEED_START = 30000


def main():
    parser = argparse.ArgumentParser(description="Run N seeded GP training runs + best-agent extraction.")
    parser.add_argument("--runs", type=int, default=1, help="Number of training runs")
    parser.add_argument("--hunter", action="store_true", help="Train and evaluate with HunterTask")
    parser.add_argument("--thief", action="store_true", help="Train and evaluate with ThiefTask")

    # mario_gp pass-through args
    parser.add_argument("--gen", type=int, default=None, help="Number of generations (default: mario_gp default)")
    parser.add_argument("--pop", type=int, default=None, help="Population size (default: mario_gp default)")
    parser.add_argument("--max-height", type=int, default=None)
    parser.add_argument("--seed-pool-size", type=int, default=None)
    parser.add_argument("--seed-rotation", type=int, default=None)
    parser.add_argument("--difficulty-shift", type=int, default=None)
    parser.add_argument("--static-operators", action="store_true")
    parser.add_argument("--mode", choices=["evolution", "random"], default=None)

    args = parser.parse_args()

    if args.hunter and args.thief:
        parser.error("--hunter and --thief are mutually exclusive")

    task_flags = ["--hunter"] if args.hunter else (["--thief"] if args.thief else [])

    for i in range(args.runs):
        seed = SEED_START + i
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
        if args.mode is not None:
            gp_cmd += ["--mode", args.mode]

        print(f"[Training] {' '.join(gp_cmd)}")
        subprocess.run(gp_cmd, check=True)

        gba_cmd = [sys.executable, "-m", "src.get_best_agent", "--seed", str(seed)] + task_flags
        print(f"\n[Best agent] {' '.join(gba_cmd)}")
        subprocess.run(gba_cmd, check=True)

    print(f"\nAll {args.runs} run(s) complete.")


if __name__ == "__main__":
    main()
