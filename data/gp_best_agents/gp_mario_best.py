
# Evolved Mario Controller
# Fitness: 1829.2399999999993


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if on_ground:
        action[Mario.KEY_DOWN] = 1
    if (landscape is not None and 0 <= 9 < landscape.shape[0] and 0 <= 11 < landscape.shape[1] and landscape[9, 11] == 20):
        if (all(landscape[y, 12] == 0 for y in range(12, 22)) or all(landscape[y, 13] == 0 for y in range(12, 22))):
            if enemies and any((ek != 3) and (abs(ex - 11) <= 3) and (abs(ey - 11) <= 3) for ex, ey, ek in enemies):
                if can_jump:
                    action[Mario.KEY_RIGHT] = 0
            else:
                if on_ground:
                    action[Mario.KEY_JUMP] = 0
    else:
        if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
            action[Mario.KEY_SPEED] = 0
        else:
            if (landscape is not None and 0 <= 10 < landscape.shape[0] and 0 <= 14 < landscape.shape[1] and landscape[10, 14] != -11):
                action[Mario.KEY_RIGHT] = 1
    if can_jump:
        if (can_jump and on_ground):
            if can_jump:
                action[Mario.KEY_JUMP] = 1
            else:
                action[Mario.KEY_SPEED] = 0
    if can_jump:
        if on_ground:
            action[Mario.KEY_SPEED] = 1
    else:
        if can_jump:
            action[Mario.KEY_LEFT] = 1

