
# Evolved Mario Controller
# Fitness: 3403.9740162434837


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

    if can_jump:
        action[Mario.KEY_JUMP] = int(True)
    action[1] = int(True)
    action[Mario.KEY_SPEED] = int(True)

