
# Evolved Mario Controller
# Fitness: 873.3806559235171


def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):

    action[Mario.KEY_RIGHT] = 1
    if can_jump:
        action[Mario.KEY_JUMP] = 1
    else:
        action[Mario.KEY_LEFT] = 0
    if on_ground:
        pass
    else:
        pass
    if (not on_ground):
        pass
    else:
        action[Mario.KEY_RIGHT] = 1
    pass

