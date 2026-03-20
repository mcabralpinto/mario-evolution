from src.marioai.task import Task

class MoveForwardTask(Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "MoveForward"
        self.no_progress_steps = 0
        self.total_reward = 0

    def reset(self):
        super().reset()
        self.no_progress_steps = 0
        self.total_reward = 0

    def compute_reward(self, current_obs, last_obs):
        if last_obs is None:
            return 0.0

        reward = 0.0

        # Reward only forward progress, not backward movement
        delta_distance = current_obs.distance - last_obs.distance
        forward_progress = max(delta_distance, 0)

        reward += (forward_progress ** 1.2) * 0.1

        # Small time penalty to encourage finishing quickly
        reward -= 0.05

        # Penalize repeated lack of progress
        if forward_progress < 1.0:
            self.no_progress_steps += 1
            if self.no_progress_steps >= 5:
                reward -= 5.0
        else:
            self.no_progress_steps = 0

        # Bonus for winning, if your observation exposes it
        if hasattr(current_obs, "did_win") and current_obs.did_win:
            reward += 1000.0

        # Penalty for dying, if exposed
        if hasattr(current_obs, "dead") and current_obs.dead:
            reward -= 500.0

        self.total_reward += reward
        return reward