import sys
import argparse
from pathlib import Path
from typing import NamedTuple
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import torch
from tqdm import tqdm
import src.marioai as marioai
from src.agents import MLPAgent, CodeAgent
from src.tasks import RunnerTask, HunterTask, ThiefTask
import pickle as pkl
import inspect
import importlib.util


class EvalResult(NamedTuple):
    win_rate: float
    avg_progress: float        # mean Mario distance in episodes that weren't won
    avg_kills: float
    avg_coins: float
    win_rate_per_diff: dict    # {diff: win_rate} for per-difficulty charts

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


def evaluate_from_code(code_str, task_cls=None, seed_start=SEED_START, seed_n=SEED_N,
                       display_difficulties=DISPLAY_DIFFICULTIES):
    """Evaluate a code string for any task. Returns an EvalResult with win_rate, avg_progress
    (mean distance in unbeaten episodes), avg_kills, avg_coins, and per-difficulty win rates."""
    if task_cls is None:
        task_cls = RunnerTask

    agent = CodeAgent()
    agent.action_function = code_str
    task = task_cls(
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
    total_kills = 0
    total_coins = 0
    total_progress = 0.0
    n_unbeaten = 0
    n_episodes = 0
    wins_per_diff = {d: 0 for d in difficulties}
    counts_per_diff = {d: 0 for d in difficulties}

    for seed, diff in tqdm(episodes, desc=f"Evaluating ({task_cls.__name__})", unit="ep"):
        task.env.level_seed = seed
        task.level_difficulty = diff
        exp.max_fps = 0
        exp.doEpisodes()

        won = task.status == 1
        if won:
            total_wins += 1
            wins_per_diff[diff] += 1
        else:
            total_progress += task.distance
            n_unbeaten += 1
        counts_per_diff[diff] += 1
        total_kills += getattr(task, "kills", 0)
        total_coins += task.coins
        n_episodes += 1

    win_rate = total_wins / n_episodes if n_episodes else 0.0
    avg_progress = total_progress / n_unbeaten if n_unbeaten else 0.0
    avg_kills = total_kills / n_episodes if n_episodes else 0.0
    avg_coins = total_coins / n_episodes if n_episodes else 0.0
    win_rate_per_diff = {d: wins_per_diff[d] / counts_per_diff[d] if counts_per_diff[d] else 0.0
                         for d in difficulties}
    return EvalResult(win_rate, avg_progress, avg_kills, avg_coins, win_rate_per_diff)


def evaluate_code_agent(suffix="", display=False, task_cls=None, seed_start=SEED_START, seed_n=SEED_N,
                        display_seed_n=DISPLAY_SEED_N, display_difficulties=DISPLAY_DIFFICULTIES):
    if task_cls is None:
        task_cls = RunnerTask

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

    task = task_cls(
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
    total_kills = 0
    total_coins = 0
    total_progress = 0.0
    n_unbeaten = 0
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
        else:
            total_progress += task.distance
            n_unbeaten += 1
        counts_per_diff[diff] += 1
        total_rewards += ep_reward
        total_kills += getattr(task, "kills", 0)
        total_coins += task.coins
        n_episodes += 1
        if display:
            line = f"seed={seed} diff={diff}: {ep_reward}" + (" + win" if won else f" | progress={task.distance:.0f}")
            kills = getattr(task, "kills", 0)
            if kills or task.coins:
                line += f" | kills={kills} coins={task.coins}"
            print(line, flush=True)

    avg_reward = total_rewards / n_episodes if n_episodes else 0
    win_rate = total_wins / n_episodes if n_episodes else 0
    avg_progress = total_progress / n_unbeaten if n_unbeaten else 0.0
    avg_kills = total_kills / n_episodes if n_episodes else 0.0
    avg_coins = total_coins / n_episodes if n_episodes else 0.0
    print(
        f"Episodes: {n_episodes} | Avg reward: {avg_reward:.2f} | Win rate: {win_rate:.2%} ({total_wins}/{n_episodes})"
        f" | Avg progress (unbeaten): {avg_progress:.1f} | Avg kills: {avg_kills:.4f} | Avg coins: {avg_coins:.4f}"
    )
    for d in difficulties:
        n = counts_per_diff[d]
        w = wins_per_diff[d]
        print(f"  Diff {d}: {w}/{n} wins ({w/n:.2%})")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--suffix", type=str, default="", help="Suffix for gp_mario_best_<suffix>.py")
    parser.add_argument("--display", action="store_true", help="Visualize across a small set of seeds/difficulties")
    parser.add_argument("--hunter", action="store_true", help="Evaluate as HunterTask (kills + coins)")
    parser.add_argument("--thief", action="store_true", help="Evaluate as ThiefTask (coins)")
    parser.add_argument("--seed-start", type=int, default=SEED_START)
    parser.add_argument("--seed-n", type=int, default=SEED_N, help="Seeds to evaluate in silent mode")
    parser.add_argument("--display-seed-n", type=int, default=DISPLAY_SEED_N, help="Seeds to show in display mode")
    parser.add_argument("--display-difficulties", type=int, default=DISPLAY_DIFFICULTIES, help="Difficulties in display mode")
    args = parser.parse_args()

    if args.hunter and args.thief:
        parser.error("--hunter and --thief are mutually exclusive")
    task_cls = HunterTask if args.hunter else (ThiefTask if args.thief else RunnerTask)

    evaluate_code_agent(
        suffix=args.suffix,
        display=args.display,
        task_cls=task_cls,
        seed_start=args.seed_start,
        seed_n=args.seed_n,
        display_seed_n=args.display_seed_n,
        display_difficulties=args.display_difficulties,
    )
