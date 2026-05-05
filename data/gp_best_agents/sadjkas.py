
# Evolved Mario Controller
# Fitness: 69350.17384033203


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if ((can_jump or on_ground) or (can_jump and can_jump)):
        if (landscape[11+3][11+0] > -10):
            action[Mario.KEY_LEFT] = 1
        else:
            if on_ground:
                action[Mario.KEY_LEFT] = 1
            else:
                action[Mario.KEY_JUMP] = 1
    else:
        action[Mario.KEY_RIGHT] = 1
    if can_jump:
        action[Mario.KEY_JUMP] = 1
    else:
        if (landscape[11+3][11+1] > 20):
            action[Mario.KEY_LEFT] = 1
        else:
            if on_ground:
                action[Mario.KEY_LEFT] = 1
            else:
                action[Mario.KEY_JUMP] = 1

