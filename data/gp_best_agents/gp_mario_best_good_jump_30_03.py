
# Evolved Mario Controller
# Fitness: 5985.320676757813


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
        action[Mario.KEY_JUMP] = 1
    else:
        if (enemies and any((int(ek) in list(range(2, 14))) and (ex - mario_pos[0] <= 30.0) for ek, ex, ey in enemies)):
            if can_jump:
                if (landscape is not None and 0 <= 13 < landscape.shape[1] and all(landscape[y, 13] == 0 for y in range(11, landscape.shape[0]))):
                    if can_jump:
                        if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                            action[Mario.KEY_LEFT] = 0
                else:
                    if (landscape is not None and 0 <= 12 < landscape.shape[0] and 0 <= 12 < landscape.shape[1] and landscape[12, 12] > -10):
                        if (not (all(landscape[y, 12] == 0 for y in range(12, 22)) or all(landscape[y, 13] == 0 for y in range(12, 22)))):
                            action[Mario.KEY_LEFT] = 1
                    else:
                        action[Mario.KEY_RIGHT] = 1
            else:
                if (on_ground or ((landscape is not None and 0 <= 9 < landscape.shape[0] and 0 <= 14 < landscape.shape[1] and landscape[9, 14] > -10) and (landscape is not None and 0 <= 10 < landscape.shape[1] and all(landscape[y, 10] == 0 for y in range(11, landscape.shape[0]))))):
                    action[Mario.KEY_RIGHT] = 1
        else:
            action[Mario.KEY_RIGHT] = 1

