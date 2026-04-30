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
        self.steps += 1
        mx, my = current_obs.mario_pos
        last_mx, _ = last_obs.mario_pos if last_obs else (mx, my)  
        
        # MOVING REWARD
        delta_x = int(mx - last_mx >= 0.61)
    
        
        # STUCK PENALTY
        stuck_penalty = 0.0
        if delta_x == 0:
            self.no_progress_steps += 1
        else:
            self.no_progress_steps = 0
        if self.no_progress_steps > 10: 
            # if mario is stuck for 10 steps and there is an obstacle in front of him, penalize
            stuck_penalty = -10 * (self.no_progress_steps - 10)

        # DEBUG PRINT
        if (self.steps % 5 == 0 and self.debug):     
            for row in current_obs.level_scene:
                print(" ".join(f"{int(cell):>3}" for cell in row))
            print()

        return delta_x + stuck_penalty