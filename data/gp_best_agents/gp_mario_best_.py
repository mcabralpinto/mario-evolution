
# Evolved Mario Controller
# Fitness: 20522.953521728516


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    action[Mario.KEY_SPEED] = 1
    if ((not can_jump) or on_ground):
        action[Mario.KEY_RIGHT] = 1
    else:
        action[Mario.KEY_DOWN] = 1
    if can_jump:
        if (landscape[11+1][11+1] != 20):
            action[Mario.KEY_JUMP] = 1
    else:
        if (not (not ((landscape[11+0][11+1] != 20) or on_ground))):
            action[Mario.KEY_SPEED] = 0
        else:
            action[Mario.KEY_JUMP] = 1
    if (not on_ground):
        action[Mario.KEY_JUMP] = 1

