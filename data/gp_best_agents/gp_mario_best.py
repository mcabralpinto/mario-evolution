
# Evolved Mario Controller
# Fitness: 14509.744338378903


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if ((enemies[11+3][11+2] > 10) or (can_jump and on_ground)):
        action[Mario.KEY_JUMP] = 1
    else:
        if (((not ((not on_ground) or on_ground)) or (landscape[11+1][11+2] >= -10)) and (not (landscape[11+3][11+1] == 16))):
            if (not ((((enemies[11+2][11+1] == 9) or can_jump) or (can_jump or on_ground)) or (not (enemies[11+2][11+1] <= 4)))):
                action[Mario.KEY_JUMP] = 1
            else:
                action[Mario.KEY_DOWN] = 1
    action[Mario.KEY_RIGHT] = 1

