
# Evolved Mario Controller
# Fitness: 30601.5594465625


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if (can_jump or on_ground):
        if ((landscape[12, 12] == 0 and any(landscape[y, 12] != 0 for y in range(13, 22))) or can_jump):
            action[Mario.KEY_DOWN] = 1
        else:
            if (all(landscape[y, 12] == 0 for y in range(12, 22))):
                if on_ground:
                    if can_jump:
                        action[Mario.KEY_JUMP] = 1
                    else:
                        action[Mario.KEY_SPEED] = 1
    else:
        if can_jump:
            if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                action[Mario.KEY_JUMP] = 1
            else:
                action[Mario.KEY_DOWN] = 1
        else:
            action[Mario.KEY_JUMP] = 1
    if on_ground:
        if can_jump:
            action[Mario.KEY_JUMP] = 1
        else:
            action[Mario.KEY_DOWN] = 1
    else:
        action[Mario.KEY_JUMP] = 1
    action[Mario.KEY_SPEED] = 1
    action[Mario.KEY_RIGHT] = 1

