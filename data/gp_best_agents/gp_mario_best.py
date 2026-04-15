
# Evolved Mario Controller
# Fitness: 23994.40866699219


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if (enemies[11+2][11+2] >= 3):
        action[Mario.KEY_RIGHT] = 0
    else:
        if on_ground:
            if (not (enemies[11+1][11+3] >= 3)):
                if on_ground:
                    if can_jump:
                        action[Mario.KEY_JUMP] = 1
                else:
                    action[Mario.KEY_LEFT] = 1
            else:
                action[Mario.KEY_JUMP] = 1
        else:
            action[Mario.KEY_JUMP] = 1
    if (landscape[11+2][11+0] != 16):
        action[Mario.KEY_RIGHT] = 1
    else:
        action[Mario.KEY_RIGHT] = 0
    action[Mario.KEY_SPEED] = 1

