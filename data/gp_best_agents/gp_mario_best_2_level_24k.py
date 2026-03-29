
# Evolved Mario Controller
# Fitness: 24637.803914596356


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if ((landscape is not None and 0 <= 13 < landscape.shape[1] and all(landscape[y, 13] == 0 for y in range(11, landscape.shape[0]))) or ((landscape is not None and 0 <= 9 < landscape.shape[0] and 0 <= 14 < landscape.shape[1] and landscape[9, 14] > -11) and (on_ground and enemies and any((ek > 7) and (abs(ex - 11) <= 3) and (abs(ey - 11) <= 3) for ex, ey, ek in enemies)))):
        action[Mario.KEY_JUMP] = 0
    else:
        action[Mario.KEY_RIGHT] = 1
    action[Mario.KEY_SPEED] = 1
    action[Mario.KEY_JUMP] = 1
    action[Mario.KEY_JUMP] = 1
    if can_jump:
        if ((landscape is not None and 0 <= 9 < landscape.shape[1] and all(landscape[y, 9] == 0 for y in range(11, landscape.shape[0]))) or (landscape is not None and 0 <= 9 < landscape.shape[0] and 0 <= 14 < landscape.shape[1] and landscape[9, 14] > -11)):
            action[Mario.KEY_LEFT] = 0
        else:
            action[Mario.KEY_SPEED] = 0
    else:
        if on_ground:
            if on_ground:
                action[Mario.KEY_JUMP] = 0
            else:
                action[Mario.KEY_JUMP] = 0
        else:
            if ((landscape is not None and 0 <= 9 < landscape.shape[1] and all(landscape[y, 9] == 0 for y in range(11, landscape.shape[0]))) and ((landscape is not None and 0 <= 9 < landscape.shape[1] and all(landscape[y, 9] == 0 for y in range(11, landscape.shape[0]))) or can_jump)):
                action[Mario.KEY_JUMP] = 1

