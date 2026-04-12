
# Evolved Mario Controller
# Fitness: 18269.676874999983


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    action[Mario.KEY_SPEED] = 1
    action[Mario.KEY_RIGHT] = 1
    action[Mario.KEY_JUMP] = 1
    if (not (landscape[11+3][11+2] < 16)):
        if ((enemies[11+1][11+2] > 4) or (not (landscape[11+3][11+2] > 20))):
            if (enemies[11+1][11+1] > 9):
                action[Mario.KEY_DOWN] = 0
            else:
                if on_ground:
                    if can_jump:
                        if (landscape[11+1][11+1] <= 16):
                            action[Mario.KEY_SPEED] = 1
                        else:
                            if ((((enemies[11+3][11+1] <= 13) and (on_ground or (can_jump or on_ground))) or can_jump) or (landscape[11+3][11+1] > 16)):
                                action[Mario.KEY_RIGHT] = 0
                            else:
                                action[Mario.KEY_JUMP] = 0
                    else:
                        action[Mario.KEY_JUMP] = 0
                else:
                    if (landscape[11+2][11+1] <= -10):
                        action[Mario.KEY_LEFT] = 0
    else:
        if on_ground:
            if can_jump:
                if (landscape[11+1][11+2] <= -10):
                    action[Mario.KEY_SPEED] = 1
                else:
                    if ((((enemies[11+3][11+1] <= 13) and (on_ground or (can_jump or on_ground))) or can_jump) or (landscape[11+3][11+1] >= 16)):
                        action[Mario.KEY_RIGHT] = 0
                    else:
                        action[Mario.KEY_JUMP] = 0
            else:
                action[Mario.KEY_JUMP] = 0
        else:
            if (landscape[11+2][11+1] > -10):
                action[Mario.KEY_LEFT] = 0

