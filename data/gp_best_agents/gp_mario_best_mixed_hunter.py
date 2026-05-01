# Evolved Mario Controller
# Hunter Score: 3.4765 (avg_kills=0.8313, avg_coins=10.5807)
# Win Rate: 0.2840

def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if (enemies[11+-1][11+3] < 4):
        if on_ground:
            action[Mario.KEY_DOWN] = 0
        else:
            action[Mario.KEY_JUMP] = 1
    if (enemies[11+-2][11+-2] < 6):
        if can_jump:
            action[Mario.KEY_JUMP] = 1
        else:
            if (enemies[11+-3][11+0] >= 12):
                action[Mario.KEY_DOWN] = 1
    if (enemies[11+1][11+0] > 6):
        action[Mario.KEY_LEFT] = 1
    else:
        if (((not can_jump) and (not on_ground)) or ((enemies[11+3][11+1] < 12) and on_ground)):
            if on_ground:
                if (on_ground and (landscape[11+2][11+-2] != 16)):
                    action[Mario.KEY_LEFT] = 1
                else:
                    action[Mario.KEY_DOWN] = 1
            else:
                if on_ground:
                    if can_jump:
                        action[Mario.KEY_DOWN] = 1
    if ((((can_jump and can_jump) and (not on_ground)) or on_ground) and (not (enemies[11+3][11+1] < 10))):
        action[Mario.KEY_RIGHT] = 1
    if (enemies[11+-2][11+-2] < 6):
        if can_jump:
            action[Mario.KEY_JUMP] = 1
        else:
            if (enemies[11+-3][11+0] >= 12):
                action[Mario.KEY_DOWN] = 1
    if (enemies[11+0][11+-2] == 6):
        action[Mario.KEY_LEFT] = 1
    else:
        if (((not can_jump) and (not on_ground)) or ((enemies[11+3][11+1] < 12) and on_ground)):
            if (on_ground or (landscape[11+1][11+2] == 20)):
                if (landscape[11+0][11+1] == -10):
                    if on_ground:
                        if can_jump:
                            if can_jump:
                                action[Mario.KEY_RIGHT] = 1
                        else:
                            if (on_ground or on_ground):
                                if can_jump:
                                    action[Mario.KEY_RIGHT] = 0
            else:
                if can_jump:
                    if can_jump:
                        if can_jump:
                            action[Mario.KEY_JUMP] = 1
                    else:
                        if on_ground:
                            if on_ground:
                                if can_jump:
                                    action[Mario.KEY_RIGHT] = 0
                        else:
                            action[Mario.KEY_RIGHT] = 0
    if ((((can_jump and can_jump) and (not on_ground)) or (landscape[11+1][11+-2] < -10)) and (not (enemies[11+3][11+1] < 10))):
        action[Mario.KEY_RIGHT] = 0
    if (not (on_ground and can_jump)):
        action[Mario.KEY_RIGHT] = 1
    if can_jump:
        if can_jump:
            if (not ((not on_ground) or can_jump)):
                if can_jump:
                    if (enemies[11+-1][11+1] > 13):
                        action[Mario.KEY_SPEED] = 1
            else:
                if can_jump:
                    if (on_ground or ((can_jump or on_ground) and (not on_ground))):
                        action[Mario.KEY_SPEED] = 0
    if (enemies[11+-2][11+-2] >= 12):
        if on_ground:
            action[Mario.KEY_RIGHT] = 0
        else:
            if can_jump:
                if (on_ground and on_ground):
                    action[Mario.KEY_RIGHT] = 0
            else:
                action[Mario.KEY_RIGHT] = 1
    else:
        if can_jump:
            if (landscape[11+2][11+2] != 20):
                if (not on_ground):
                    if on_ground:
                        action[Mario.KEY_DOWN] = 0
                    else:
                        action[Mario.KEY_RIGHT] = 1
            else:
                if (landscape[11+2][11+2] != -10):
                    action[Mario.KEY_DOWN] = 0
