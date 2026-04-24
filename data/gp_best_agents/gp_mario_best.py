
# Evolved Mario Controller
# Fitness: 0.0


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if (enemies[11+-2][11+1] <= 2):
        if can_jump:
            action[Mario.KEY_DOWN] = 0
        else:
            action[Mario.KEY_RIGHT] = 1
    else:
        action[Mario.KEY_RIGHT] = 0

