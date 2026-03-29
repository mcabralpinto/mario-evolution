from src.marioai.task import Task

class HunterTask(Task):
    def __init__(self, *args, **kwargs):
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
        current_x  = current_obs.mario_pos[0] if current_obs is not None else 0
        last_x = last_obs.mario_pos[0] if last_obs is not None else current_x
        delta_x = current_x - last_x

        stuck_penalty = 0.0
        if abs(delta_x) <= 0.61 and current_obs.may_jump:
            self.no_progress_steps += 1
            stuck_penalty = self.stall_penalty_step * self.no_progress_steps
        else:
            self.no_progress_steps = 0

        airtime_penalty = 0.0
        if not current_obs.on_ground and self.generation > 24:
            airtime_penalty = -5
            #print(f"Airtime penalty applied at generation {self.generation}")
        return delta_x + stuck_penalty + airtime_penalty