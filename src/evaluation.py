from src.marioai.experiment import Experiment
from src.marioai.task import Task
from multiprocessing import Pool, Manager, current_process
from itertools import cycle
from src.agents import MLPAgent, CodeAgent
from src.tasks import MoveForwardTask, HunterTask
import numpy as np
import random
from tqdm import tqdm

# Variable that configures the number of parallel processes
N_PROCESSES = 10
# Task Definition
TASK_TO_SOLVE = HunterTask

COIN_WEIGHT = 10
WIN_REWARD = 10000.0
LOSE_PENALTY = -WIN_REWARD / 2


port_list = [4242 + i for i in range(N_PROCESSES)]


def evaluate_agent(agent, task: Task, episodes=5):
    """
    Evaluates the agent on the task for a given number of episodes.
    Returns the average fitness (reward).
    """
    exp = Experiment(task, agent)
    # Speed up simulation for training
    exp.max_fps = -1

    total_reward = 0

    for i in range(episodes):
        episode_reward = 0
        # Randomize level layout so GP does not overfit a single "always right" map.
        # task.env.level_seed = random.randint(1, 5)
        task.env.level_seed = i
        # Try up to 3 levels of increasing difficulty
        for _ in range(3):
            rewards = exp.doEpisodes(1)
            episode_reward += task.cum_reward
            # episode_reward += task.coins * COIN_WEIGHT
            if task.status == 1:
                episode_reward += WIN_REWARD
            else:
                break

        total_reward += episode_reward

    return total_reward / episodes


# --- GLOBAL VARIABLES FOR WORKER PROCESSES ---
# These exist independently inside EACH worker process.
worker_task: Task = None
worker_agent: CodeAgent = None


def init_worker(agent_class):
    """
    This runs ONCE when each worker process starts.
    """
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
        worker_task = TASK_TO_SOLVE(visualization=False, port=port, init_mario_mode=0)


def evaluate_individual(ind_info):
    """
    This runs for every individual in the population.
    It uses the GLOBALLY cached worker_task.
    ind_info is a tuple of (individual, generation).
    """
    global worker_task, worker_agent

    ind, generation = ind_info
    worker_task.generation = generation

    # 1. Update the persistent agent with the new DNA
    if isinstance(worker_agent, MLPAgent):
        worker_agent.set_param_vector(ind)
    elif isinstance(worker_agent, CodeAgent):
        worker_agent.action_function = ind

    # 2. Run evaluation using the EXISTING connection
    # No "with", no "connect", just use the persistent object.
    try:
        reward = evaluate_agent(worker_agent, worker_task)
    except Exception as e:
        print(f"Error in worker: {e}")
        reward = 0

    return reward


def evaluate(agent_class, ind_info, generation=0):
    global worker_agent, worker_task
    if worker_agent is None:
        worker_agent = agent_class()
    if worker_task is None:
        worker_task = TASK_TO_SOLVE(visualization=False, port=port_list[0])
    return evaluate_individual((ind_info, generation))


def evaluate_population(agent, population, generation=0):

    # Match processes to tasks to avoid one worker being idle or double-booking
    n_processes = N_PROCESSES

    # Pair each individual with the current generation number
    population_with_gen = [(ind, generation) for ind in population]

    # We pass 'tasks' to the initializer, so every worker picks one at startup
    with Pool(
        processes=n_processes, initializer=init_worker, initargs=(agent,)
    ) as pool:
        # We only map the POPULATION. The tasks are already fixed in the workers.
        rewards_list = list(
            tqdm(
                pool.imap(evaluate_individual, population_with_gen),
                total=len(population),
                desc="Evaluating",
                unit="ind",
            )
        )

    worker_task = None

    return np.array(rewards_list)
