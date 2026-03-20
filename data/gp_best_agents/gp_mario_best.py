
# Evolved Mario Controller
# Fitness: 2965.152734228478


def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
    # Process sensors (Heuristics)
    enemy_near = any(abs(ex) < 30 and abs(ey) < 30 for ex, ey, ek in enemies)
    obstacle_ahead = False
    if landscape is not None:
        # Check a few cells in front of Mario (11,11)
        obstacle_ahead = (landscape[11, 12] != 0 or landscape[11, 13] != 0 or landscape[10, 12] != 0)

    hole_ahead = False
    if landscape is not None:
        # Check for floor gap
        hole_ahead = True
        for i in range(12, 16):
            if landscape[12, i] != 0 or landscape[13, i] != 0:
                hole_ahead = False
                break

    # INDIVIDUAL GENERATED CODE vvv

    if enemy_near:
        if (not (landscape is not None and 0 <= 9 < landscape.shape[0] and 0 <= 13 < landscape.shape[1] and landscape[9, 13] == -10)):
            pass
            pass
            if (enemy_near and on_ground):
                pass
        if (landscape is not None and 0 <= 11 < landscape.shape[0] and 0 <= 11 < landscape.shape[1] and landscape[11, 11] != 20):
            pass
            if (landscape is not None and 0 <= 13 < landscape.shape[0] and 0 <= 11 < landscape.shape[1] and landscape[13, 11] != 21):
                pass
    action[Mario.KEY_RIGHT] = 1
    if (not ((any((ek < 8) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies) or (any((ek == 6) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies) or (not can_jump))) and (landscape is not None and 0 <= 13 < landscape.shape[0] and 0 <= 9 < landscape.shape[1] and landscape[13, 9] != 21))):
        action[Mario.KEY_JUMP] = 1

