# Evolved Mario Controller
# Win Rate: 0.3987

def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    action[Mario.KEY_SPEED] = 1
    if (not (on_ground and (enemies[11+1][11+1] <= 5))):
        action[Mario.KEY_JUMP] = 1
    if can_jump:
        action[Mario.KEY_JUMP] = 1
    else:
        action[Mario.KEY_RIGHT] = 1
