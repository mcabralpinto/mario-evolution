# Evolved Mario Controller
# Hunter Score: 1.0667 (avg_kills=1.0667)
# Win Rate: 0.2000

def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if (enemies[11+-1][11+3] < 7):
        if on_ground:
            action[Mario.KEY_SPEED] = 0
        else:
            action[Mario.KEY_JUMP] = 1
    action[Mario.KEY_LEFT] = 0
    if (enemies[11+2][11+3] >= 8):
        action[Mario.KEY_DOWN] = 0
    else:
        if (on_ground or can_jump):
            action[Mario.KEY_DOWN] = 1
        else:
            if ((landscape[11+-3][11+1] <= 16) or (not (enemies[11+2][11+0] != 2))):
                if on_ground:
                    action[Mario.KEY_SPEED] = 1
            else:
                action[Mario.KEY_SPEED] = 0
    if (enemies[11+1][11+-2] < 8):
        if can_jump:
            action[Mario.KEY_JUMP] = 1
        else:
            action[Mario.KEY_DOWN] = 0
    if (enemies[11+1][11+-2] == 10):
        action[Mario.KEY_JUMP] = 1
    else:
        if (((enemies[11+2][11+-3] >= 4) or (landscape[11+1][11+0] >= -10)) or (not (enemies[11+0][11+3] < 4))):
            if (landscape[11+0][11+3] > -10):
                if (landscape[11+0][11+-3] < 16):
                    if (not (landscape[11+-2][11+2] <= 16)):
                        if can_jump:
                            if can_jump:
                                action[Mario.KEY_RIGHT] = 1
                    else:
                        if (enemies[11+0][11+3] > 10):
                            action[Mario.KEY_SPEED] = 1
                        else:
                            if (not (can_jump and (landscape[11+0][11+0] >= -10))):
                                action[Mario.KEY_LEFT] = 0
                            else:
                                action[Mario.KEY_SPEED] = 0
        else:
            if (not (enemies[11+0][11+-3] > 4)):
                action[Mario.KEY_LEFT] = 0
            else:
                action[Mario.KEY_SPEED] = 1
    action[Mario.KEY_RIGHT] = 0
    action[Mario.KEY_RIGHT] = 1
