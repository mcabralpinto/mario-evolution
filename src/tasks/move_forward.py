from src.marioai.task import Task

class MoveForwardTask(Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "MoveForward"
        self.no_progress_steps = 0

    def reset(self):
        super().reset()
        self.no_progress_steps = 0

    def compute_reward(self, current_obs, last_obs):
        if last_obs is None:
            return 0
        reward = 0
        # calculate distance in any direction
        dist_moved = abs(current_obs.distance - last_obs.distance)  
        reward = dist_moved
        # jump walls reward
        if dist_moved == 0:
            self.no_progress_steps += 1
            if self.no_progress_steps > 5:  
                reward -= 100
        else:
            self.no_progress_steps = 0  # reset counter if progress is made

        return reward
