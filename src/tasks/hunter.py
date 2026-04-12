from src.marioai.task import Task

class HunterTask(Task):
    def __init__(self, *args, **kwargs):
        self.is_best_eval = bool(kwargs.pop("is_best_eval", False))
        super().__init__(*args, **kwargs)
        self.name = "Hunter"
        self.total_reward = 0
        self.no_progress_steps = 0

        self.stall_progress_eps = 0.61
        self.stall_penalty_step = -0.1

    def reset(self):
        super().reset()
        self.no_progress_steps = 0
        self.total_reward = 0

    
    def compute_reward(self, current_obs, last_obs):

        mx, my = current_obs.mario_pos
        last_mx, last_my = last_obs.mario_pos if last_obs else (mx, my)

        delta_x = int(mx > last_mx)*0.1

        stuck_penalty = 0.0
        if delta_x == 0 and current_obs.may_jump:
            self.no_progress_steps += 1
            stuck_penalty = -10 * self.no_progress_steps
        else:
            self.no_progress_steps = 0

        airtime_penalty = 0.0
        if not current_obs.on_ground:
            airtime_penalty = -50

        enemy_penalty = 0.0
        for ex, ey, _ in current_obs.enemies:

            rel_x = ex - mx
            rel_y = ey - my

            if -8 < rel_x <= 48 and -16 <= rel_y <= 16:

                dist = max(1.0, (rel_x**2 + rel_y**2)**0.5)
                enemy_penalty -= (5 / dist)

        return delta_x + stuck_penalty + airtime_penalty + enemy_penalty