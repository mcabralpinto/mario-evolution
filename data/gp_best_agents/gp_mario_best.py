
# Evolved Mario Controller
# Fitness: 26582.01479746094


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if ((landscape[11+3][11+1] < -10) or can_jump):
        if (((landscape[11+1][11+2] == -11) or (landscape[11+3][11+2] <= -11)) or (can_jump or can_jump)):
            if on_ground:
                action[Mario.KEY_RIGHT] = 1
    else:
        action[Mario.KEY_RIGHT] = 1
    action[Mario.KEY_JUMP] = 1
    if on_ground:
        if ((landscape[11+1][11+0] == -10) and (can_jump and can_jump)):
            if can_jump:
                action[Mario.KEY_RIGHT] = 1
            else:
                action[Mario.KEY_SPEED] = 1
        else:
            if (on_ground and ((((landscape[11+1][11+2] != -10) or (can_jump and can_jump)) and can_jump) or ((landscape[11+2][11+1] <= -11) or can_jump))):
                action[Mario.KEY_SPEED] = 1
            else:
                if (on_ground or on_ground):
                    action[Mario.KEY_JUMP] = 0
                else:
                    action[Mario.KEY_SPEED] = 0
    else:
        if (landscape[11+1][11+3] == 20):
            action[Mario.KEY_SPEED] = 1
        else:
            action[Mario.KEY_SPEED] = 1

