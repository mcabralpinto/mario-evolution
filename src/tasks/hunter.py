from src.marioai.task import Task

class HunterTask(Task):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Hunter"
        self.no_progress_steps = 0
        self.total_reward = 0

        self.kill_reward = 10.0
        self.kill_radius_x = 40
        self.kill_radius_y = 40
        self.match_radius_x = 20
        self.match_radius_y = 20

    def compute_reward(self, current_obs, last_obs):
        if last_obs is None:
            return 0.0

        reward = 0.0

        # ---------- Forward progress ----------
        delta_distance = current_obs.distance - last_obs.distance
        forward_progress = max(delta_distance, 0.0)

        reward += (forward_progress ** 1.2) * 0.1

        if forward_progress < 1.0:
            self.no_progress_steps += 1
            if self.no_progress_steps >= 5:
                reward -= 5.0
        else:
            self.no_progress_steps = 0

        walk_reward = reward
        # ---------- Enemy kill reward ----------
        kill_reward = 0.0

        for ex, ey, ek in last_obs.enemies:

            # enemy must have been near Mario previously
            if abs(ex) > 40 or abs(ey) > 40:
                continue

            still_visible = False

            for cex, cey, cek in current_obs.enemies:

                if (
                    ek == cek
                    and abs(cex - ex) < 20
                    and abs(cey - ey) < 20
                ):
                    still_visible = True
                    break

            # only reward if enemy disappeared AND mario didn't outrun it
            if not still_visible and delta_distance < 15:
                kill_reward += 100.0

        kill_reward = kill_reward * (3*walk_reward/kill_reward) if kill_reward > 0 and  walk_reward > kill_reward else -0.5 * walk_reward
        reward += kill_reward
        self.total_reward += reward
        return reward