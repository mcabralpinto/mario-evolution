
# Evolved Mario Controller
# Fitness: 150212.00643920898


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    action[Mario.KEY_RIGHT] = 1
    if ((not (on_ground and on_ground)) or can_jump):
        if ((landscape[11+-1][11+3] < 16) or (not ((not can_jump) and (enemies[11+2][11+1] < 2)))):
            action[Mario.KEY_JUMP] = 1
        else:
            action[Mario.KEY_SPEED] = 1
    else:
        if (landscape[11+3][11+1] < 16):
            action[Mario.KEY_SPEED] = 1

