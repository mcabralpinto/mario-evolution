
# Evolved Mario Controller
# Fitness: 740.0


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
            if landscape[i, 12] != 0:
                hole_ahead = False
                break

    # INDIVIDUAL GENERATED CODE vvv

    if ((hole_ahead and hole_ahead) or ((enemy_near and (on_ground and (on_ground or hole_ahead))) or can_jump)):
        action[Mario.KEY_JUMP] = int(True)

