# Evolved Mario Controller
# Win Rate: 0.1333
# Avg Progress (unbeaten): 1035.06
# Avg Kills: 0.0000
# Avg Coins: 8.5333

def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    action[Mario.KEY_RIGHT] = 1
    if (landscape[11+0][11+3] >= 16):
        if (enemies[11+-2][11+-1] > 13):
            if (landscape[11+0][11+0] >= 16):
                if (landscape[11+3][11+2] < 20):
                    if (landscape[11+-2][11+1] >= 20):
                        action[Mario.KEY_LEFT] = 0
                    else:
                        if on_ground:
                            if (landscape[11+1][11+-3] >= -10):
                                action[Mario.KEY_LEFT] = 0
                            else:
                                if on_ground:
                                    action[Mario.KEY_JUMP] = 0
                                else:
                                    action[Mario.KEY_DOWN] = 0
                else:
                    if ((landscape[11+3][11+0] == 20) or (landscape[11+3][11+1] == 20)):
                        if (not on_ground):
                            action[Mario.KEY_LEFT] = 1
                        else:
                            action[Mario.KEY_DOWN] = 0
                    else:
                        if (can_jump or on_ground):
                            if on_ground:
                                if on_ground:
                                    action[Mario.KEY_SPEED] = 1
                            else:
                                if can_jump:
                                    action[Mario.KEY_LEFT] = 0
                                else:
                                    action[Mario.KEY_SPEED] = 1
                        else:
                            if (not can_jump):
                                if on_ground:
                                    action[Mario.KEY_LEFT] = 0
                                else:
                                    action[Mario.KEY_JUMP] = 0
    else:
        if (landscape[11+-2][11+3] >= 16):
            if (enemies[11+3][11+-1] > 4):
                action[Mario.KEY_RIGHT] = 0
        else:
            if (not ((not can_jump) and on_ground)):
                action[Mario.KEY_JUMP] = 1
            else:
                action[Mario.KEY_LEFT] = 1
