import torch
import torch.nn as nn
import numpy as np
from src.marioai.task import Task

class HunterTask(Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Hunter"

    def compute_reward(self, current_obs, last_obs):
        """
        Computes the reward for the current state of the game based on Mario's actions 
        and the environment changes between the current and last observations.
        This function evaluates Mario's progress, interactions with enemies, and overall 
        performance to calculate a reward value. The reward is used as the fitness function for the evolutionary algorithm.
        Parameters:
        - current_obs: The current observation of the game state;
        - last_obs: The previous observation of the game state;
        Returns:
        - reward (float): The computed reward value based on the game state changes.
        Notes for Students:
        - This function is critical for defining the algorithm behavior. The reward function 
          directly impacts the fitness evaluation of the AI.
        - You are encouraged to edit and experiment with this function to design a reward 
          system that aligns with the objectives of the project.
        - Consider the balance between encouraging progress, rewarding kills, and penalizing 
          undesirable behaviors (e.g., cowardice or reckless actions).

        Computes the reward for Hunter task.
        Reward is based on both distance covered and enemies killed.
        Since we don't have explicit kill counts, we estimate kills by 
        detecting when enemies near Mario disappear.
        """
        # if last_obs is None:
        #     return 0
        
        # reward = 0
        
        # # 1. Base reward for moving forward
        # reward += (current_obs.distance - last_obs.distance)
        # # Small shaping bonus for absolute progress in the level
        # reward += current_obs.distance * 0.001
        
        # # 2. Reward for "killing" enemies
        # last_enemies_count = len(last_obs.enemies)
        # current_enemies_count = len(current_obs.enemies)
        
        # if current_enemies_count < last_enemies_count:
        #     # Check if any enemy from last_obs was "near" Mario
        #     for ex, ey, ek in last_obs.enemies:
        #         # If enemy was within a small radius and is gone
        #         if abs(ex) < 20 and abs(ey) < 20: 
        #             # Verify it's not in current_obs
        #             is_gone = True
        #             for cex, cey, cek in current_obs.enemies:
        #                 # Simple check for same enemy (approximate)
        #                 if abs(cex - ex) < 10 and abs(cey - ey) < 10:
        #                     is_gone = False
        #                     break
        #             if is_gone:
        #                 reward += 100 # Kill bonus
        
        # return reward
