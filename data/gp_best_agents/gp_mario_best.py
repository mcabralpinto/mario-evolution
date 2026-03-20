
# Evolved Mario Controller
# Fitness: 1577.9071766601419


def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
    # INDIVIDUAL GENERATED CODE vvv

    if (not (any((ek == 6) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies) and (landscape is not None and 0 <= 13 < landscape.shape[0] and 0 <= 9 < landscape.shape[1] and landscape[13, 9] != 21))):
        action[Mario.KEY_RIGHT] = 1

