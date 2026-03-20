
# Evolved Mario Controller
# Fitness: 7248.467157108621


def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
    # Always start by moving right
    action[Mario.KEY_RIGHT] = 1
    # INDIVIDUAL GENERATED CODE vvv

    if can_jump:
        action[Mario.KEY_JUMP] = 1
        action[Mario.KEY_SPEED] = 1
        if can_jump:
            pass
        if any((ek == 8) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies):
            action[Mario.KEY_LEFT] = 1
        if (landscape is not None and 0 <= 11 < landscape.shape[0] and 0 <= 11 < landscape.shape[1] and landscape[11, 11] != 20):
            pass
            if any((ek == 8) and (abs(ex) <= 16) and (abs(ey) <= 16) for ex, ey, ek in enemies):
                pass
    action[Mario.KEY_RIGHT] = 1
    if (not (on_ground and (landscape is not None and 0 <= 10 < landscape.shape[0] and 0 <= 10 < landscape.shape[1] and landscape[10, 10] != -10))):
        action[Mario.KEY_JUMP] = 1

