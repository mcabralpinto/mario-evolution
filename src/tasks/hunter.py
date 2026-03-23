import torch
import torch.nn as nn
import numpy as np
from src.marioai.task import Task

class HunterTask(Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Hunter"
        self.no_progress_steps = 0
        self.total_reward = 0

    def compute_reward(self, current_obs, last_obs):
        if last_obs is None:
            return 0
        
        reward = 0
        
        # 1 Reward for forward progress
        # 1.1 basic forward progress reward
        delta_distance = current_obs.distance - last_obs.distance
        forward_progress = max(delta_distance, 0)

        reward += (forward_progress ** 1.2) * 0.1
        # 1.2 penalize lack of progress
        if forward_progress < 1.0:
            self.no_progress_steps += 1
            if self.no_progress_steps >= 5:
                reward -= 5.0
        else:
            self.no_progress_steps = 0

        self.total_reward += reward
        # 2. Reward for "killing" enemies
        last_enemies = last_obs.enemies
        current_enemies = current_obs.enemies

        for ex, ey, ek in last_enemies: 
            num_of_existing_enemies = 0
            if abs(ex) < 10 and abs(ey) < 10:
                for cex, cey, cek in current_enemies:
                    if abs(cex - ex) < 20 and abs(cey - ey) < 20:
                      num_of_existing_enemies += 1

            reward += num_of_existing_enemies * 10.0                        


                
        return reward
