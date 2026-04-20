
# Evolved Mario Controller
# Fitness: 20216.909399414064


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if (not on_ground):
        action[Mario.KEY_JUMP] = 1
    else:
        if can_jump:
            action[Mario.KEY_JUMP] = 1
    if (((enemies[11+2][11+3] <= 6) and (enemies[11+3][11+1] <= 6)) or (on_ground and (landscape[11+3][11+0] != 16))):
        if (not on_ground):
            action[Mario.KEY_RIGHT] = 1
    else:
        action[Mario.KEY_DOWN] = 0

