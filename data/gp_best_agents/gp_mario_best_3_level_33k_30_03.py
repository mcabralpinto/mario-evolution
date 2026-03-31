
# Evolved Mario Controller
# Fitness: 33816.94703108724


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):    

    action[Mario.KEY_SPEED] = 1
    if ((enemies and any((int(ek) in list(range(2, 14))) and ((-5 <= ey - mario_pos[1] <= 30) and (-5 <= ex - mario_pos[0] <= 30.0)) for ek, ex, ey in enemies)) and (landscape is not None and 0 <= 14 < landscape.shape[1] and all(landscape[y, 14] == 0 for y in range(11, landscape.shape[0])))):
        action[Mario.KEY_LEFT] = 1
    action[Mario.KEY_JUMP] = 1
    if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
        action[Mario.KEY_RIGHT] = 1
    else:
        if can_jump:
            action[Mario.KEY_DOWN] = 0
    if ((enemies and any((ek != 7) and (abs(ex - 11) <= 3) and (abs(ey - 11) <= 3) for ex, ey, ek in enemies) or (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12)))) and (landscape is not None and 0 <= 8 < landscape.shape[1] and all(landscape[y, 8] == 0 for y in range(11, landscape.shape[0])))):
        action[Mario.KEY_LEFT] = 1
    action[Mario.KEY_JUMP] = 1
    if ((enemies and any((int(ek) in list(range(2, 14))) and ((-5 <= ey - mario_pos[1] <= 30) and (-5 <= ex - mario_pos[0] <= 30.0)) for ek, ex, ey in enemies)) and (((any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))) or (not can_jump)) and (landscape is not None and 0 <= 9 < landscape.shape[0] and 0 <= 13 < landscape.shape[1] and landscape[9, 13] < -10))):
        if (((not (landscape is not None and 0 <= 11 < landscape.shape[0] and 0 <= 8 < landscape.shape[1] and landscape[11, 8] > -11)) or ((not (not can_jump)) and enemies and any((ek == 10) and (abs(ex - 11) <= 3) and (abs(ey - 11) <= 3) for ex, ey, ek in enemies))) or (enemies and any((int(ek) in list(range(2, 14))) and ((-5 <= ey - mario_pos[1] <= 30) and (-5 <= ex - mario_pos[0] <= 30.0)) for ek, ex, ey in enemies))):
            action[Mario.KEY_JUMP] = 0
        else:
            action[Mario.KEY_RIGHT] = 1
    if can_jump:
        if (landscape is not None and 0 <= 9 < landscape.shape[1] and all(landscape[y, 9] == 0 for y in range(11, landscape.shape[0]))):
            if (not (landscape is not None and 0 <= 8 < landscape.shape[1] and all(landscape[y, 8] == 0 for y in range(11, landscape.shape[0])))):
                if (landscape is not None and 0 <= 10 < landscape.shape[0] and 0 <= 14 < landscape.shape[1] and landscape[10, 14] != 16):
                    if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                        action[Mario.KEY_RIGHT] = 0
                    else:
                        if on_ground:
                            if (landscape is not None and 0 <= 11 < landscape.shape[0] and 0 <= 14 < landscape.shape[1] and landscape[11, 14] != 20):
                                if can_jump:
                                    action[Mario.KEY_LEFT] = 1
                                else:
                                    if (all(landscape[y, 12] == 0 for y in range(12, 22)) or all(landscape[y, 13] == 0 for y in range(12, 22))):
                                        if (not (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12)))):
                                            action[Mario.KEY_LEFT] = 1
                                        else:
                                            action[Mario.KEY_JUMP] = 1
                else:
                    if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                        if enemies and any((ek < 7) and (abs(ex - 11) <= 3) and (abs(ey - 11) <= 3) for ex, ey, ek in enemies):
                            if on_ground:
                                action[Mario.KEY_LEFT] = 1
                    else:
                        action[Mario.KEY_LEFT] = 0
        else:
            action[Mario.KEY_SPEED] = 1
    else:
        if (((not (landscape is not None and 0 <= 14 < landscape.shape[0] and 0 <= 14 < landscape.shape[1] and landscape[14, 14] != 16)) or on_ground) or (can_jump and (not (landscape is not None and 0 <= 13 < landscape.shape[0] and 0 <= 11 < landscape.shape[1] and landscape[13, 11] > 16)))):
            action[Mario.KEY_JUMP] = 0
        else:
            action[Mario.KEY_RIGHT] = 1

