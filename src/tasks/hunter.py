from numpy import rint

from src.marioai.task import Task

class HunterTask(Task):
    def __init__(self, *args, **kwargs):
        self.is_best_eval = bool(kwargs.pop("is_best_eval", False))
        super().__init__(*args, **kwargs)
        self.name = "Hunter"
        self.total_reward = 0
        self.no_progress_steps = 0
        self.steps = 0

        self.stall_progress_eps = 0.61
        self.stall_penalty_step = -0.1
        
        self.obstacles = [-11, -10, 16, 20]
        self.enemy_types = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13]
        
        self.debug = False
        self.beta = False
        
    def reset(self):
        super().reset()
        self.no_progress_steps = 0
        self.total_reward = 0
        self.steps = 0
    
    def compute_reward(self, current_obs, last_obs):
        self.steps += 1
        mx, my = current_obs.mario_pos
        last_mx, last_my = last_obs.mario_pos if last_obs else (mx, my)

        # MOVING REWARD
        delta_x = int(mx - last_mx >= 0.61)
        # STUCK PENALTY - maybe overhaul to only include cases where he is clearly stuck on a wall
        stuck_penalty = 0.0
        if delta_x == 0 or last_mx > mx:
            self.no_progress_steps += 1
        else:
            self.no_progress_steps = 0
        if (
            self.no_progress_steps > 10 and 
            current_obs.level_scene[11][12] in self.obstacles and
            not any(current_obs.level_scene[i][j] == 12 for i in range(0, 12) for j in range(12, 14)) # piranha above
        ): 
            # if mario is stuck for 10 steps and there is an obstacle in front of him, penalize
            stuck_penalty = -10 * (self.no_progress_steps - 10)
            # print(f"PENALTY FOR STALLING: {stuck_penalty} (no progress for {self.no_progress_steps} steps)")


        # AIR TIME PENALTY
        airtime_penalty = 0.0
        if not current_obs.on_ground:
            # mario going up
            airtime_penalty -= int(my < last_my) * 200

        # ENEMY PENALTY
        enemy_penalty = 0.0
        if any(current_obs.level_scene[12][j] in self.enemy_types for i in range(10, 12) for j in range(12, 15)): 
            # if there is an enemy in the 3x2 area in front of mario, penalize
            enemy_penalty = -10
        
        # piranha wait reward - if there is a piranha above, reward waiting (not moving forward)
        if any(current_obs.level_scene[x][y] == 12 for x in range(8, 11) for y in range(12, 15)):
            # penalize moving forward if there is a piranha above
            delta_x -= int(delta_x > 0) * 10000
            
        
        # DEBUG PRINT
        if (self.steps % 5 == 0 and self.debug):     
            for row in current_obs.level_scene:
                print(" ".join(f"{int(cell):>3}" for cell in row))
            print()

        return delta_x + stuck_penalty + airtime_penalty + enemy_penalty 