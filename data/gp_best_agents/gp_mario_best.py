
# Evolved Mario Controller
# Fitness: 27248.176012695312


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    action[Mario.KEY_SPEED] = 1
    action[Mario.KEY_JUMP] = 1
    if (not can_jump):
        if on_ground:
            action[Mario.KEY_JUMP] = 0
    else:
        action[Mario.KEY_DOWN] = 0
    if (can_jump or (landscape[11+1][11+1] > 16)):
        action[Mario.KEY_SPEED] = 0
    else:
        action[Mario.KEY_RIGHT] = 1
    action[Mario.KEY_DOWN] = 1

