from numpy import rint

from src.marioai.task import Task

_KOOPA_TYPES = frozenset({3, 4, 5, 6})
_SHELL_TYPES = frozenset({7, 8})
_PIRANHA_TYPE = 9
_SCROLL_DISTANCE = 160   # 10 blocks * 16px
_PIT_Y_THRESHOLD = 240   # bottom border is 256

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
        self.kills = 0
        self.last_enemy_count = 0
        self.previous_vy = 0.0
        
    def reset(self):
        super().reset()
        self.no_progress_steps = 0
        self.total_reward = 0
        self.kills = 0
        self.steps = 0
        self.last_enemy_count = 0
    
    def detect_kills(self, current_obs, last_obs):
            if last_obs is None:
                return 0

            mx = current_obs.mario_pos[0]
            kills = 0
            piranha_pipe_cols = set()

            def group_by_type(enemies):
                d = {}
                for e in enemies:
                    d.setdefault(e[0], []).append(e)
                return d

            last_by_type = group_by_type(last_obs.enemies)
            curr_by_type = group_by_type(current_obs.enemies)

            # Koopa stomped into shell: koopa count drops and shell count rises
            last_koopas = sum(len(last_by_type.get(t, [])) for t in _KOOPA_TYPES)
            curr_koopas = sum(len(curr_by_type.get(t, [])) for t in _KOOPA_TYPES)
            last_shells = sum(len(last_by_type.get(t, [])) for t in _SHELL_TYPES)
            curr_shells = sum(len(curr_by_type.get(t, [])) for t in _SHELL_TYPES)

            koopa_stomp_kills = min(max(last_koopas - curr_koopas, 0), max(curr_shells - last_shells, 0))
            kills += koopa_stomp_kills
            koopa_stomp_remaining = koopa_stomp_kills

            for etype, last_list in last_by_type.items():
                curr_count = len(curr_by_type.get(etype, []))
                missing = len(last_list) - curr_count
                if missing <= 0:
                    continue

                # Deduct koopa->shell transitions already counted above
                if etype in _KOOPA_TYPES:
                    take = min(missing, koopa_stomp_remaining)
                    missing -= take
                    koopa_stomp_remaining -= take
                    if missing <= 0:
                        continue

                # Prioritise pit-death candidates (highest y first)
                candidates = sorted(last_list, key=lambda e: -e[2])

                for _ in range(missing):
                    if not candidates:
                        break
                    enemy = candidates.pop(0)

                    # Fell into a pit
                    if enemy[2] > _PIT_Y_THRESHOLD:
                        continue

                    # Scrolled off screen edge
                    if abs(enemy[1] - mx) > _SCROLL_DISTANCE:
                        continue

                    # Piranha retracted into pipe (one pass per pipe column per frame)
                    if etype == _PIRANHA_TYPE:
                        pipe_col = int(enemy[1] / 16)
                        if pipe_col not in piranha_pipe_cols:
                            piranha_pipe_cols.add(pipe_col)
                            continue

                    vy_curr = current_obs.mario_pos[1] - last_obs.mario_pos[1]
                    bounced = (self.previous_vy > 0 and vy_curr > 0) or (self.previous_vy == 0 and vy_curr < 0)
                    if bounced:
                        # print("BOUNCE DETECTED")
                        kills += 1

            # print(self.previous_vy, current_obs.mario_pos[1] - last_obs.mario_pos[1])
            self.previous_vy = current_obs.mario_pos[1] - last_obs.mario_pos[1]
            self.kills += kills
            
            return kills

    def compute_reward(self, current_obs, last_obs):
        self.steps += 1
        mx, my = current_obs.mario_pos
        last_mx, last_my = last_obs.mario_pos if last_obs else (mx, my)
        # MOVING REWARD
        delta_x = int(mx - last_mx >= 0.61)
        # STUCK PENALTY - maybe overhaul to only include cases where he is clearly stuck on a wall
        stuck_penalty = 0.0
        if delta_x == 0:
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
        
        kill_reward = self.detect_kills(current_obs, last_obs) * 10000

        # print(self.kills)
        # DEBUG PRINT
        if (self.steps % 5 == 0 and self.debug):     
            for row in current_obs.level_scene:
                print(" ".join(f"{int(cell):>3}" for cell in row))
            print()

        return delta_x + stuck_penalty + kill_reward