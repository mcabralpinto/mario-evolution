
# Evolved Mario Controller
# Fitness: 3164.7183713629433


def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
    # INDIVIDUAL GENERATED CODE vvv

    if (landscape is not None and landscape.shape[0] > 11 and landscape.shape[1] > 12 and landscape[11, 12] == 0):
        if any((ek == 13) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies):
            action[Mario.KEY_RIGHT] = 1
            pass
        else:
            pass
            if (landscape is not None and 0 <= 14 < landscape.shape[0] and 0 <= 14 < landscape.shape[1] and landscape[14, 14] != 16):
                pass
                if (not (on_ground and (not (can_jump or can_jump)))):
                    pass
                    action[Mario.KEY_RIGHT] = 1
                    pass
                    pass
                else:
                    pass
            else:
                pass
                pass
    else:
        if any((ek == 13) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies):
            action[Mario.KEY_RIGHT] = 1
        else:
            action[Mario.KEY_JUMP] = 1

