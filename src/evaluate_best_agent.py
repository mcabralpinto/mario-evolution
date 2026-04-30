import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import torch
from tqdm import tqdm
import src.marioai as marioai
from src.agents import MLPAgent, CodeAgent
from src.tasks import MoveForwardTask, HunterTask
import pickle as pkl
import inspect
import importlib.util

SEED_START = 20000
SEED_N = 1000
DISPLAY_SEED_N = 5
DISPLAY_DIFFICULTIES = 3


def load_gp_best_module(suffix=""):
    repo_root = Path(__file__).parent.parent
    filename = f"gp_mario_best{('_' + suffix) if suffix else ''}.py"
    candidate_paths = [
        repo_root / "data" / "gp_best_agents" / filename,
    ]
    for module_path in candidate_paths:
        if module_path.exists():
            spec = importlib.util.spec_from_file_location("gp_mario_best_dynamic", module_path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise FileNotFoundError(f"No {filename} found in data/gp_best_agents")


def evaluate_from_code(code_str, seed_start=SEED_START, seed_n=SEED_N,
                       display_difficulties=DISPLAY_DIFFICULTIES):
    """Evaluate a raw code string. Returns (overall_win_rate, {diff: win_rate})."""
    agent = CodeAgent()
    agent.action_function = code_str

    task = HunterTask(
        visualization=False,
        port=4243,
        init_mario_mode=0,
        level_difficulty=0,
        is_best_eval=True,
    )
    exp = marioai.Experiment(task, agent)
    task.env.level_type = 0

    seeds = range(seed_start, seed_start + seed_n)
    difficulties = range(display_difficulties)
    episodes = [(s, d) for s in seeds for d in difficulties]

    total_wins = 0
    n_episodes = 0
    wins_per_diff = {d: 0 for d in difficulties}
    counts_per_diff = {d: 0 for d in difficulties}
    for seed, diff in tqdm(episodes, desc="Evaluating", unit="ep"):
        task.env.level_seed = seed
        task.level_difficulty = diff
        exp.max_fps = 0
        exp.doEpisodes()
        if task.status == 1:
            total_wins += 1
            wins_per_diff[diff] += 1
        counts_per_diff[diff] += 1
        n_episodes += 1

    overall = total_wins / n_episodes if n_episodes else 0
    per_diff = {d: wins_per_diff[d] / counts_per_diff[d] if counts_per_diff[d] else 0
                for d in difficulties}
    return overall, per_diff


def evaluate_code_agent(suffix="", display=False, seed_start=SEED_START, seed_n=SEED_N,
                        display_seed_n=DISPLAY_SEED_N, display_difficulties=DISPLAY_DIFFICULTIES):
    mario_best = load_gp_best_module(suffix)
    action = inspect.getsource(mario_best.corre)
    agent = CodeAgent()
    agent.action_function = action

    if display:
        seeds = range(seed_start, seed_start + display_seed_n)
        difficulties = range(display_difficulties)
        viz = True
        max_fps = 60
    else:
        seeds = range(seed_start, seed_start + seed_n)
        difficulties = range(display_difficulties)
        viz = False
        max_fps = 0

    task = HunterTask(
        visualization=viz,
        port=4243,
        init_mario_mode=0,
        level_difficulty=0,
        is_best_eval=True,
    )
    exp = marioai.Experiment(task, agent)
    task.env.level_type = 0

    total_rewards = 0
    total_wins = 0
    n_episodes = 0
    wins_per_diff = {d: 0 for d in difficulties}
    counts_per_diff = {d: 0 for d in difficulties}
    episodes = [(s, d) for s in seeds for d in difficulties]

    for seed, diff in tqdm(episodes, desc="Evaluating", unit="ep", disable=display):
        task.env.level_seed = seed
        task.level_difficulty = diff
        exp.max_fps = max_fps
        ep_reward = sum(exp.doEpisodes()[0])
        won = task.status == 1
        if won:
            total_wins += 1
            wins_per_diff[diff] += 1
        counts_per_diff[diff] += 1
        total_rewards += ep_reward
        n_episodes += 1
        if display:
            print(f"seed={seed} diff={diff}: {ep_reward}" + (" + 10000 (win)" if won else ""), flush=True)

    avg_reward = total_rewards / n_episodes if n_episodes else 0
    win_rate = total_wins / n_episodes if n_episodes else 0
    print(f"Episodes: {n_episodes} | Avg reward: {avg_reward:.2f} | Win rate: {win_rate:.2%} ({total_wins}/{n_episodes})")
    for d in difficulties:
        n = counts_per_diff[d]
        w = wins_per_diff[d]
        print(f"  Diff {d}: {w}/{n} wins ({w/n:.2%})")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--suffix", type=str, default="", help="Suffix for gp_mario_best_<suffix>.py")
    parser.add_argument("--display", action="store_true", help="Visualize across a small set of seeds/difficulties")
    parser.add_argument("--seed-start", type=int, default=SEED_START)
    parser.add_argument("--seed-n", type=int, default=SEED_N, help="Seeds to evaluate in silent mode")
    parser.add_argument("--display-seed-n", type=int, default=DISPLAY_SEED_N, help="Seeds to show in display mode")
    parser.add_argument("--display-difficulties", type=int, default=DISPLAY_DIFFICULTIES, help="Difficulties in display mode")
    args = parser.parse_args()

    evaluate_code_agent(
        suffix=args.suffix,
        display=args.display,
        seed_start=args.seed_start,
        seed_n=args.seed_n,
        display_seed_n=args.display_seed_n,
        display_difficulties=args.display_difficulties,
    )
