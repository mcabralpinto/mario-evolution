
# Evolved Mario Controller
# Fitness: 2356.111981445278


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

    action[Mario.KEY_RIGHT] = 1
    action[Mario.KEY_JUMP] = 1
    if ((any((ek == 9) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies) and ((on_ground and (not hole_ahead)) and (can_jump and (enemy_near and any((ek == 12) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies))))) and any((ek == 2) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies)):
        action[Mario.KEY_SPEED] = 1

