# Evolved Mario Controller
# Win Rate: 0.4053

def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    action[Mario.KEY_RIGHT] = 1
    if (can_jump or (on_ground or can_jump)):
        if can_jump:
            action[Mario.KEY_JUMP] = 1
        else:
            action[Mario.KEY_RIGHT] = 0
    else:
        action[Mario.KEY_JUMP] = 1
    if ((enemies[11+-3][11+-1] <= 3) and (landscape[11+-3][11+2] != -10)):
        action[Mario.KEY_SPEED] = 1
