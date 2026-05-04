from src.marioai.experiment import Experiment
from src.marioai.task import Task
from multiprocessing import Pool
from src.agents import MLPAgent, CodeAgent
from src.tasks import RunnerTask, HunterTask, ThiefTask
import numpy as np
import random
from tqdm import tqdm
import atexit

# Variable that configures the number of parallel processes
N_PROCESSES = 5
# Task Definition
TASK_TO_SOLVE = HunterTask

WIN_REWARD = 10000.0
#LOSE_PENALTY = -WIN_REWARD / 2
N_EVAL_SEEDS = 3
MAX_EVAL_DIFFICULTIES = 3  # window size; base shifts upward over training
TOTAL_GENERATIONS = 0


port_list = [4242 + i for i in range(N_PROCESSES)]


def set_total_generations(ngen):
    global TOTAL_GENERATIONS
    TOTAL_GENERATIONS = int(ngen)


def set_task_class(cls):
    global TASK_TO_SOLVE
    TASK_TO_SOLVE = cls


def evaluate_agent(agent, task: Task, seed_pool=None, base_difficulty=0):
    """
    Evaluates the agent on the task for each seed in seed_pool.
    Returns the average fitness (reward) across all seeds.
    Evaluates at difficulties [base_difficulty, base_difficulty + MAX_EVAL_DIFFICULTIES).
    """
    exp = Experiment(task, agent)
    # Speed up simulation for training
    exp.max_fps = -1

    seeds = seed_pool if seed_pool is not None else list(range(1, N_EVAL_SEEDS + 1))
    total_reward = 0.0

    for seed in seeds:
        seed_reward = 0.0
        task.env.level_seed = seed

        for difficulty in range(MAX_EVAL_DIFFICULTIES):
            task.level_difficulty = base_difficulty + difficulty
            exp.doEpisodes(1)
            seed_reward += task.cum_reward

            if isinstance(task, RunnerTask) and task.status == 1:
                # Add win reward for RunnerTask
                seed_reward += WIN_REWARD
                
            if isinstance(task, HunterTask):
                # Add kill reward for HunterTask
                seed_reward += task.kill_reward * task.kills
                
            if isinstance(task, ThiefTask):
                # Add coin reward for ThiefTask
                seed_reward += task.coin_reward * task.coins

        total_reward += seed_reward

    return total_reward / len(seeds)


# --- GLOBAL VARIABLES FOR WORKER PROCESSES ---
# These exist independently inside EACH worker process.
worker_task: Task = None
worker_agent: CodeAgent = None

# Reused in the parent process to avoid re-spawning workers every generation.
_pool = None
_pool_agent_class = None


def init_worker(agent_class):
    """
    This runs ONCE when each worker process starts.
    """
    import signal
    # Workers must ignore SIGINT so only the main process handles Ctrl+C.
    # Without this, every worker also throws KeyboardInterrupt and the pool
    # enters a broken state that keeps propagating errors.
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    global worker_agent, worker_task

    # Each worker needs to pick a port. Since we have 10 workers
    # and 10 ports, we can use a trick to assign them.
    import multiprocessing

    # Get the index of the current worker (0 through 9)
    # Note: This is a hacky way to get a unique index;
    # alternatively, use a shared Counter/Queue.
    worker_idx = int(multiprocessing.current_process().name.split("-")[-1]) - 1
    port = port_list[worker_idx % len(port_list)]

    # print(f"Worker initialized: Connecting once to port {port}...")

    worker_agent = agent_class()
    if worker_task is None:
        worker_task = TASK_TO_SOLVE(
            visualization=False,
            port=port,
            init_mario_mode=0,
            is_best_eval=False,
            ngen=TOTAL_GENERATIONS,
        )


def evaluate_individual(ind_info):
    """
    This runs for every individual in the population.
    It uses the GLOBALLY cached worker_task.
    ind_info is a tuple of (individual, generation, seed_pool, base_difficulty).
    """
    global worker_task, worker_agent

    ind, generation, seed_pool, base_difficulty = ind_info
    worker_task.generation = generation

    # 1. Update the persistent agent with the new DNA
    if isinstance(worker_agent, MLPAgent):
        worker_agent.set_param_vector(ind)
    elif isinstance(worker_agent, CodeAgent):
        worker_agent.action_function = ind

    # 2. Run evaluation using the EXISTING connection
    # No "with", no "connect", just use the persistent object.
    try:
        reward = evaluate_agent(worker_agent, worker_task, seed_pool=seed_pool, base_difficulty=base_difficulty)
    except Exception as e:
        print(f"Error in worker: {e}")
        reward = 0

    return reward


def evaluate(agent_class, ind_info, generation=0, seed_pool=None, base_difficulty=0):
    global worker_agent, worker_task
    if worker_agent is None:
        worker_agent = agent_class()
    if worker_task is None:
        worker_task = TASK_TO_SOLVE(
            visualization=False,
            port=port_list[0],
            is_best_eval=False,
            ngen=TOTAL_GENERATIONS,
        )
    return evaluate_individual((ind_info, generation, seed_pool, base_difficulty))


def _ensure_pool(agent):
    """Creates a pool once and reuses it across evaluations."""
    global _pool, _pool_agent_class
    if _pool is None or _pool_agent_class is not agent:
        close_evaluation_pool()
        _pool = Pool(processes=N_PROCESSES, initializer=init_worker, initargs=(agent,))
        _pool_agent_class = agent
    return _pool


def close_evaluation_pool():
    """Closes the shared pool and releases worker resources."""
    global _pool, _pool_agent_class
    if _pool is not None:
        _pool.close()
        _pool.join()
        _pool = None
        _pool_agent_class = None


def terminate_evaluation_pool():
    """Terminates the pool immediately (use on interrupt to unblock imap)."""
    global _pool, _pool_agent_class
    if _pool is not None:
        _pool.terminate()
        _pool.join()
        _pool = None
        _pool_agent_class = None


atexit.register(close_evaluation_pool)


def evaluate_population(agent, population, generation=0, seed_pool=None, base_difficulty=0):
    # Pair each individual with the current generation number, seed pool, and difficulty
    population_with_gen = [(ind, generation, seed_pool, base_difficulty) for ind in population]

    if not population_with_gen:
        return np.array([])

    pool = _ensure_pool(agent)

    # We only map the POPULATION. The tasks are already fixed in the workers.
    try:
        rewards_list = list(
            tqdm(
                pool.imap(evaluate_individual, population_with_gen),
                total=len(population),
                desc="Evaluating",
                unit="ind",
            )
        )
    except Exception:
        # Pool was terminated (e.g. by the interrupt handler) — return empty
        # so the caller can check the interrupt flag and exit cleanly.
        return np.array([])

    return np.array(rewards_list)
