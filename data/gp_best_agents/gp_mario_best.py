
# Evolved Mario Controller
# Fitness: 8415.052568546038


def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
    # INDIVIDUAL GENERATED CODE vvv

    if can_jump:
        action[Mario.KEY_JUMP] = 1
        action[Mario.KEY_SPEED] = 1
    action[Mario.KEY_RIGHT] = 1
    if (not on_ground):
        action[Mario.KEY_JUMP] = 1
        if (landscape is not None and 0 <= 14 < landscape.shape[0] and 0 <= 14 < landscape.shape[1] and landscape[14, 14] != -10):
            action[Mario.KEY_SPEED] = 1
        action[Mario.KEY_DOWN] = 1

