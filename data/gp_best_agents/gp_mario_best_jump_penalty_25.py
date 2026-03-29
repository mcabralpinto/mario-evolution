
# Evolved Mario Controller
# Fitness: 44380.56


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if (landscape is not None and 0 <= 10 < landscape.shape[0] and 0 <= 9 < landscape.shape[1] and landscape[10, 9] > -10):
        action[Mario.KEY_RIGHT] = 1
    if (enemies and any((int(ek) in list(range(2, 14))) and (ex - mario_pos[0] <= 30.0) for ek, ex, ey in enemies)):
        if (not (not (landscape is not None and 0 <= 13 < landscape.shape[1] and all(landscape[y, 13] == 0 for y in range(11, landscape.shape[0]))))):
            action[Mario.KEY_LEFT] = 1
    if can_jump:
        action[Mario.KEY_JUMP] = 1
    else:
        if on_ground:
            action[Mario.KEY_JUMP] = 0
        else:
            if (landscape is not None and 0 <= 9 < landscape.shape[0] and 0 <= 12 < landscape.shape[1] and landscape[9, 12] != -11):
                action[Mario.KEY_JUMP] = 1

