
# Evolved Mario Controller
# Fitness: 17713.29935546875


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    action[Mario.KEY_RIGHT] = 1
    if (enemies[11+2][11+1] < 3):
        if (landscape[11+2][11+2] > -11):
            action[Mario.KEY_SPEED] = 1
    if ((on_ground and (can_jump and (((on_ground and (enemies[11+2][11+3] != 13)) and (enemies[11+3][11+2] < 13)) and ((landscape[11+3][11+2] >= 16) and on_ground)))) or ((enemies[11+3][11+1] < 5) and ((landscape[11+3][11+3] == -11) or can_jump))):
        action[Mario.KEY_JUMP] = 1
    else:
        if (((can_jump and (landscape[11+3][11+3] >= -11)) or (not (on_ground and on_ground))) or ((enemies[11+3][11+1] > 10) or (enemies[11+2][11+2] == 9))):
            if can_jump:
                if on_ground:
                    action[Mario.KEY_JUMP] = 1
            else:
                action[Mario.KEY_JUMP] = 1

