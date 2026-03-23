
# Evolved Mario Controller
# Fitness: 7307.747157108621


def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
    # INDIVIDUAL GENERATED CODE vvv

    if can_jump:
        action[Mario.KEY_JUMP] = 1
        action[Mario.KEY_SPEED] = 1
        action[Mario.KEY_JUMP] = 1
    action[Mario.KEY_RIGHT] = 1
    if (not (on_ground and (landscape is not None and 0 <= 14 < landscape.shape[0] and 0 <= 8 < landscape.shape[1] and landscape[14, 8] != 16))):
        action[Mario.KEY_JUMP] = 1

