
# Evolved Mario Controller
# Fitness: 51114.17004699707


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if (enemies[11+-1][11+1] < 8):
        if (not (landscape[11+1][11+3] > 16)):
            if (enemies[11+-1][11+1] < 12):
                if (not (on_ground or on_ground)):
                    action[Mario.KEY_RIGHT] = 1
                else:
                    action[Mario.KEY_SPEED] = 1
        else:
            action[Mario.KEY_SPEED] = 1
    if ((not (on_ground or ((enemies[11+0][11+2] < 13) and ((enemies[11+0][11+-3] == 13) or on_ground)))) or can_jump):
        action[Mario.KEY_JUMP] = 1
    else:
        if (landscape[11+0][11+3] < 16):
            if (not (enemies[11+-2][11+0] == 8)):
                if can_jump:
                    if (enemies[11+3][11+0] == 8):
                        if can_jump:
                            action[Mario.KEY_SPEED] = 0
                        else:
                            if on_ground:
                                action[Mario.KEY_LEFT] = 1
                    else:
                        if (can_jump and on_ground):
                            if on_ground:
                                action[Mario.KEY_RIGHT] = 1
                        else:
                            if can_jump:
                                action[Mario.KEY_LEFT] = 1
                            else:
                                action[Mario.KEY_RIGHT] = 1
            else:
                if can_jump:
                    if (enemies[11+3][11+3] < 8):
                        if can_jump:
                            if can_jump:
                                action[Mario.KEY_DOWN] = 0
                            else:
                                action[Mario.KEY_LEFT] = 0
        else:
            if can_jump:
                action[Mario.KEY_JUMP] = 0

