# Evolved Mario Controller
# Win Rate: 0.0093
# Avg Progress (unbeaten): 508.57
# Avg Kills: 0.0000
# Avg Coins: 2.9960

def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    action[Mario.KEY_SPEED] = 0
    action[Mario.KEY_JUMP] = 0
    if can_jump:
        if on_ground:
            if on_ground:
                action[Mario.KEY_JUMP] = 1
        else:
            action[Mario.KEY_RIGHT] = 1
    else:
        action[Mario.KEY_JUMP] = 0
    if (not can_jump):
        if can_jump:
            action[Mario.KEY_LEFT] = 0
        else:
            action[Mario.KEY_SPEED] = 1
    else:
        action[Mario.KEY_JUMP] = 1
    if on_ground:
        action[Mario.KEY_DOWN] = 1
    else:
        action[Mario.KEY_RIGHT] = 1
