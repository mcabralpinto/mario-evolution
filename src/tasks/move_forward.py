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
        pass_obstacles = 0
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
                pass_obstacles -= 1
            elif wall_ahead or hole_ahead:
                pass_obstacles += 1
            if (wall_ahead or hole_ahead) and (not current_obs.on_ground):
                pass_obstacles += 1
            if (wall_ahead or hole_ahead) and current_obs.on_ground and dist_moved <= 0:
                pass_obstacles -= 1

        dont_fall_into_holes = 0
        if current_obs.on_ground and not last_obs.on_ground:
            dont_fall_into_holes += 1
        elif not current_obs.on_ground and last_obs.on_ground:
            dont_fall_into_holes -= 1

        print("Reward weights: dist_moved =", dist_moved, ", pass_obstacles =", pass_obstacles, ", dont_fall_into_holes =", dont_fall_into_holes)
        reward = dist_moved + pass_obstacles + dont_fall_into_holes
        return reward
