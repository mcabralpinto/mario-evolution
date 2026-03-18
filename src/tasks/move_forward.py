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
        
        dist_moved = current_obs.distance - last_obs.distance
        reward = dist_moved * 2.0
        reward += current_obs.distance * 0.002

        # Strongly punish getting stuck at obstacles to break "always right" behavior.
        if last_obs.level_scene is not None:
            wall_ahead = (
                last_obs.level_scene[11, 12] != 0
                or last_obs.level_scene[11, 13] != 0
                or last_obs.level_scene[10, 12] != 0
            )
            hole_ahead = True
            for i in range(12, 16):
                if last_obs.level_scene[12, i] != 0 or last_obs.level_scene[13, i] != 0:
                    hole_ahead = False
                    break
            if (wall_ahead or hole_ahead) and dist_moved <= 0:
                reward -= 1.5
            elif wall_ahead or hole_ahead:
                reward += 0.5
            if (wall_ahead or hole_ahead) and (not current_obs.on_ground):
                reward += 1.0
            if (wall_ahead or hole_ahead) and current_obs.on_ground and dist_moved <= 0:
                reward -= 0.8

        if current_obs.on_ground and not last_obs.on_ground:
            reward += 0.3

        return reward
