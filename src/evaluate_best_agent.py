import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import torch
import src.marioai as marioai
from src.agents import MLPAgent, CodeAgent
from src.tasks import MoveForwardTask, HunterTask
import pickle as pkl
import inspect
import importlib.util


def load_gp_best_module():
    repo_root = Path(__file__).parent.parent
    candidate_paths = [
        repo_root / "data" / "gp_best_agents" / "gp_mario_best.py",
    ]
    for module_path in candidate_paths:
        if module_path.exists():
            spec = importlib.util.spec_from_file_location("gp_mario_best_dynamic", module_path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise FileNotFoundError("No gp_mario_best.py found in data/gp_best_agents")


def evaluate_code_agent():
    mario_best = load_gp_best_module()
    action = inspect.getsource(mario_best.corre)
    agent = CodeAgent()
    #agent.action_function = "def corre(Mario, Sprite, landscape, enemies, can_jump, on_ground, action):\n  action[Mario.KEY_RIGHT] = 0\n  if landscape[11 + -1][11 + 2] != 21:\n    action[Mario.KEY_JUMP] = 1\n    if can_jump:\n      action[Mario.KEY_DOWN] = 0\n    else:\n      if on_ground:\n        if can_jump:\n          action[Mario.KEY_RIGHT] = 1\n        else:\n          action[Mario.KEY_JUMP] = 0\n        action[Mario.KEY_DOWN] = 1\n    action[Mario.KEY_RIGHT] = 1\n  else:\n    if on_ground:\n      action[Mario.KEY_LEFT] = 1\n    else:\n      if landscape[11 + -2][11 + -2] == Sprite.KIND_GREEN_KOOPA_WINGED:\n        action[Mario.KEY_RIGHT] = 0\n      else:\n        action[Mario.KEY_DOWN] = 1\n      action[Mario.KEY_RIGHT] = 0" #"def corre(Mario, Sprite, landscape, enemies, can_jump, on_ground, action):\n  action[Mario.KEY_RIGHT] = 1\n  if enemies[11 + -1][11 + 0] != Sprite.KIND_RED_KOOPA_WINGED:\n    action[Mario.KEY_JUMP] = 1\n    if can_jump:\n      if enemies[11 + -1][11 + 0] != Sprite.KIND_RED_KOOPA_WINGED:\n        action[Mario.KEY_DOWN] = 1\n    else:\n      if on_ground:\n        action[Mario.KEY_JUMP] = 0\n    action[Mario.KEY_DOWN] = 0\n    if can_jump:\n      action[Mario.KEY_SPEED] = 1" # "def corre(Mario, Sprite, landscape, enemies, can_jump, on_ground, action):\n  if can_jump:\n    action[Mario.KEY_JUMP] = 1\n    if enemies[11 + 1][11 + 1] != Sprite.KIND_GOOMBA_WINGED:\n      if on_ground:\n        action[Mario.KEY_SPEED] = 1\n    else:\n      action[Mario.KEY_JUMP] = 0\n  else:\n    if on_ground:\n      action[Mario.KEY_DOWN] = 0\n    else:\n      action[Mario.KEY_DOWN] = 1\n      action[Mario.KEY_SPEED] = 0\n      if can_jump:\n        if enemies[11 + 0][11 + -1] == Sprite.KIND_BULLET_BILL:\n          action[Mario.KEY_RIGHT] = 0\n          action[Mario.KEY_RIGHT] = 1\n      else:\n        action[Mario.KEY_JUMP] = 1\n    if on_ground:\n      if on_ground:\n        if can_jump:\n          action[Mario.KEY_JUMP] = 1\n        else:\n          action[Mario.KEY_LEFT] = 1\n        action[Mario.KEY_DOWN] = 0\n      else:\n        action[Mario.KEY_DOWN] = 1\n      action[Mario.KEY_SPEED] = 1\n    else:\n      action[Mario.KEY_RIGHT] = 1\n    action[Mario.KEY_SPEED] = 0\n  action[Mario.KEY_RIGHT] = 1" #"def corre(Mario, Sprite, landscape, enemies, can_jump, on_ground, action):\n  if can_jump:\n    action[Mario.KEY_JUMP] = 1\n    if on_ground:\n      if landscape[11 + -1][11 + -1] != 20:\n        action[Mario.KEY_RIGHT] = 0\n      else:\n        action[Mario.KEY_JUMP] = 1\n    else:\n      action[Mario.KEY_LEFT] = 1\n      action[Mario.KEY_JUMP] = 1\n  else:\n    action[Mario.KEY_RIGHT] = 0\n    if can_jump:\n      if can_jump:\n        if enemies[11 + -1][11 + 0] == Sprite.KIND_GREEN_KOOPA_WINGED:\n          if on_ground:\n            if on_ground:\n              action[Mario.KEY_DOWN] = 1\n            else:\n              action[Mario.KEY_RIGHT] = 1\n        else:\n          action[Mario.KEY_SPEED] = 0\n          action[Mario.KEY_DOWN] = 0\n    else:\n      action[Mario.KEY_RIGHT] = 1\n  action[Mario.KEY_SPEED] = 1\n  if landscape[11 + 1][11 + -1] != 21:\n    action[Mario.KEY_DOWN] = 0\n  action[Mario.KEY_SPEED] = 1" #"def corre(Mario, Sprite, landscape, enemies, can_jump, on_ground, action):\n  if on_ground:\n    if can_jump:\n      action[Mario.KEY_JUMP] = 1\n      if enemies[11 + 1][11 + 1] != Sprite.KIND_SPIKY:\n        action[Mario.KEY_RIGHT] = 0\n      else:\n        action[Mario.KEY_JUMP] = 1\n    else:\n      action[Mario.KEY_SPEED] = 1\n      action[Mario.KEY_LEFT] = 1\n    if landscape[11 + 0][11 + -1] != 0:\n      action[Mario.KEY_DOWN] = 0\n      action[Mario.KEY_DOWN] = 0\n    else:\n      if on_ground:\n        action[Mario.KEY_DOWN] = 0\n      action[Mario.KEY_RIGHT] = 1\n  else:\n    action[Mario.KEY_RIGHT] = 1\n    action[Mario.KEY_JUMP] = 1" #def corre(Mario, Sprite, landscape, enemies, can_jump, on_ground, action):\n  if on_ground:\n    if can_jump:\n      action[Mario.KEY_JUMP] = 1\n  else:\n    if landscape[11 + 1][11 + 1] != 20:\n      action[Mario.KEY_LEFT] = 1\n      action[Mario.KEY_LEFT] = 1\n      action[Mario.KEY_LEFT] = 0\n    else:\n      action[Mario.KEY_RIGHT] = 0\n      action[Mario.KEY_DOWN] = 1\n    action[Mario.KEY_JUMP] = 1\n    action[Mario.KEY_SPEED] = 0\n    if can_jump:\n      action[Mario.KEY_RIGHT] = 0\n      action[Mario.KEY_RIGHT] = 0\n    else:\n      action[Mario.KEY_JUMP] = 1\n      action[Mario.KEY_LEFT] = 0\n      if landscape[11 + 1][11 + 0] != 21:\n        action[Mario.KEY_RIGHT] = 1\n      else:\n        action[Mario.KEY_JUMP] = 1\n        action[Mario.KEY_LEFT] = 1\n  action[Mario.KEY_SPEED] = 1\n  if can_jump:\n    if landscape[11 + 1][11 + 0] != -10:\n      action[Mario.KEY_JUMP] = 1\n    else:\n      action[Mario.KEY_SPEED] = 1" #"def corre(Mario, Sprite, landscape, enemies, can_jump, on_ground, action):\n  action[Mario.KEY_RIGHT] = 1\n  if can_jump:\n    action[Mario.KEY_JUMP] = 1\n  else:\n    action[Mario.KEY_SPEED] = 1\n  action[Mario.KEY_LEFT] = 0\n  if on_ground:\n    action[Mario.KEY_LEFT] = 1\n  else:\n    action[Mario.KEY_JUMP] = 1" #"def corre(Mario, Sprite, landscape, enemies, can_jump, on_ground, action):\n  if can_jump:\n    if on_ground:\n      action[Mario.KEY_JUMP] = 1\n      action[Mario.KEY_SPEED] = 0\n      action[Mario.KEY_SPEED] = 0\n    else:\n      action[Mario.KEY_DOWN] = 1\n  else:\n    action[Mario.KEY_SPEED] = 0\n  if on_ground:\n    if can_jump:\n      if can_jump:\n        action[Mario.KEY_DOWN] = 0\n      else:\n        if can_jump:\n          action[Mario.KEY_JUMP] = 1\n        else:\n          action[Mario.KEY_SPEED] = 0\n    if on_ground:\n      action[Mario.KEY_LEFT] = 1\n  else:\n    action[Mario.KEY_RIGHT] = 1\n    if enemies[11 + 0][11 + 0] != Sprite.KIND_GREEN_KOOPA_WINGED:\n      action[Mario.KEY_JUMP] = 1\n    else:\n      if can_jump:\n        action[Mario.KEY_DOWN] = 0\n      else:\n        action[Mario.KEY_RIGHT] = 1\n        if on_ground:\n          action[Mario.KEY_LEFT] = 1"
    agent.action_function = action
    task = HunterTask(visualization=True, port=4243, init_mario_mode=0, level_difficulty=0)
    exp = marioai.Experiment(task, agent)
    exp.max_fps = 60
    task.env.level_type = 0
    rewards = sum(exp.doEpisodes()[0])

    task.level_difficulty += 1
    print(task.level_difficulty)
    exp.max_fps = 60
    task.env.level_type = 0
    rewards += sum(exp.doEpisodes()[0])

    task.level_difficulty += 1
    print(task.level_difficulty)
    exp.max_fps = 60
    task.env.level_type = 0
    rewards += sum(exp.doEpisodes()[0])
    
    
    
    print(rewards)




def evaluate_mlp_agent():
    agent = MLPAgent()
    task = MoveForwardTask(visualization=True, port=4243)
    exp = marioai.Experiment(task, agent)


    with open(f'{sys.argv[1]}', 'rb') as f:
        best_params = pkl.load(f)


    agent.set_param_vector(best_params)
    exp.max_fps = 60
    task.env.level_type = 0
    rewards = exp.doEpisodes()
    print(sum(rewards[0]))


if __name__ == '__main__':
    #evaluate_mlp_agent()
    evaluate_code_agent()
