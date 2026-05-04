
# Evolved Mario Controller
# Fitness: 50372.028212890626


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    action[Mario.KEY_RIGHT] = 0
    if on_ground:
        if (on_ground or on_ground):
            action[Mario.KEY_RIGHT] = 1
        else:
            action[Mario.KEY_JUMP] = 1
    else:
        action[Mario.KEY_JUMP] = 1
    if (not can_jump):
        if ((landscape[11+3][11+1] > -10) or on_ground):
            action[Mario.KEY_RIGHT] = 1
    else:
        action[Mario.KEY_JUMP] = 1

