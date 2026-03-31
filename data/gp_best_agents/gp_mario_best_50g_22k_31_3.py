
# Evolved Mario Controller
# Fitness: 21843.018832919923


def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):

    if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
        action[Mario.KEY_JUMP] = 1
    if (enemies and any((int(ek) in list(range(2, 14))) and ((-16 <= mario_pos[1] - ey <= 32) and (-32 <= ex - mario_pos[0] <= 48)) for ek, ex, ey in enemies)):
        if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
            action[Mario.KEY_DOWN] = 0
    else:
        if (on_ground and (all(landscape[y, 12] == 0 for y in range(12, 22)) or all(landscape[y, 13] == 0 for y in range(12, 22)))):
            if ((not on_ground) or (not ((not can_jump) or ((not can_jump) and (all(landscape[y, 12] == 0 for y in range(12, 22)) or all(landscape[y, 13] == 0 for y in range(12, 22))))))):
                action[Mario.KEY_JUMP] = 1
        else:
            if can_jump:
                if ((enemies and any((int(ek) in list(range(2, 14))) and ((-16 <= mario_pos[1] - ey <= 32) and (-32 <= ex - mario_pos[0] <= 48)) for ek, ex, ey in enemies)) or (all(landscape[y, 12] == 0 for y in range(12, 22)) or all(landscape[y, 13] == 0 for y in range(12, 22)))):
                    action[Mario.KEY_SPEED] = 0
                else:
                    if ((not on_ground) and on_ground):
                        action[Mario.KEY_DOWN] = 0
            else:
                if (enemies and any((int(ek) in list(range(2, 14))) and ((-16 <= mario_pos[1] - ey <= 32) and (-32 <= ex - mario_pos[0] <= 48)) for ek, ex, ey in enemies)):
                    if can_jump:
                        action[Mario.KEY_DOWN] = 1
    if (not on_ground):
        if (can_jump or can_jump):
            action[Mario.KEY_LEFT] = 1
        else:
            if on_ground:
                if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                    if can_jump:
                        action[Mario.KEY_LEFT] = 0
                    else:
                        if on_ground:
                            if on_ground:
                                action[Mario.KEY_LEFT] = 0
                            else:
                                action[Mario.KEY_JUMP] = 0
                else:
                    if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                        if (not on_ground):
                            if can_jump:
                                action[Mario.KEY_DOWN] = 0
                            else:
                                action[Mario.KEY_RIGHT] = 1
    if on_ground:
        if (not ((not (enemies and any((int(ek) in list(range(2, 14))) and ((-16 <= mario_pos[1] - ey <= 32) and (-32 <= ex - mario_pos[0] <= 48)) for ek, ex, ey in enemies))) and on_ground)):
            action[Mario.KEY_SPEED] = 1
    else:
        if can_jump:
            action[Mario.KEY_DOWN] = 0
    if (enemies and any((int(ek) in list(range(2, 14))) and ((-16 <= mario_pos[1] - ey <= 32) and (-32 <= ex - mario_pos[0] <= 48)) for ek, ex, ey in enemies)):
        if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
            action[Mario.KEY_DOWN] = 0
    else:
        if (can_jump and (all(landscape[y, 12] == 0 for y in range(12, 22)) or all(landscape[y, 13] == 0 for y in range(12, 22)))):
            if ((not on_ground) or (not ((not can_jump) or ((not can_jump) and (all(landscape[y, 12] == 0 for y in range(12, 22)) or all(landscape[y, 13] == 0 for y in range(12, 22))))))):
                action[Mario.KEY_JUMP] = 1
        else:
            if can_jump:
                if can_jump:
                    if (can_jump or (enemies and any((int(ek) in list(range(2, 14))) and ((-16 <= mario_pos[1] - ey <= 32) and (-32 <= ex - mario_pos[0] <= 48)) for ek, ex, ey in enemies))):
                        action[Mario.KEY_SPEED] = 1
            else:
                if (on_ground or on_ground):
                    action[Mario.KEY_JUMP] = 0
    if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
        if (can_jump or can_jump):
            action[Mario.KEY_LEFT] = 1
        else:
            if on_ground:
                if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                    if (enemies and any((int(ek) in list(range(2, 14))) and ((-16 <= mario_pos[1] - ey <= 32) and (-32 <= ex - mario_pos[0] <= 48)) for ek, ex, ey in enemies)):
                        action[Mario.KEY_DOWN] = 0
                    else:
                        if on_ground:
                            if on_ground:
                                action[Mario.KEY_SPEED] = 0
                            else:
                                action[Mario.KEY_JUMP] = 0
                else:
                    if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                        if (not on_ground):
                            if can_jump:
                                action[Mario.KEY_DOWN] = 0
                            else:
                                action[Mario.KEY_RIGHT] = 0
    if on_ground:
        if ((enemies and any((int(ek) in list(range(2, 14))) and ((-16 <= mario_pos[1] - ey <= 32) and (-32 <= ex - mario_pos[0] <= 48)) for ek, ex, ey in enemies)) or (not (on_ground or can_jump))):
            action[Mario.KEY_RIGHT] = 0
    else:
        if can_jump:
            action[Mario.KEY_DOWN] = 0
    if on_ground:
        action[Mario.KEY_RIGHT] = 1
    else:
        if (on_ground and (not can_jump)):
            action[Mario.KEY_RIGHT] = 0
        else:
            if (on_ground and can_jump):
                if (on_ground and (can_jump and can_jump)):
                    if can_jump:
                        if on_ground:
                            action[Mario.KEY_RIGHT] = 1
                    else:
                        action[Mario.KEY_JUMP] = 1
    if can_jump:
        action[Mario.KEY_DOWN] = 1
    if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
        if (on_ground or (enemies and any((int(ek) in list(range(2, 14))) and ((-16 <= mario_pos[1] - ey <= 32) and (-32 <= ex - mario_pos[0] <= 48)) for ek, ex, ey in enemies))):
            if on_ground:
                if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                    if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                        if on_ground:
                            if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                                action[Mario.KEY_RIGHT] = 0
                    else:
                        if ((all(landscape[y, 12] == 0 for y in range(12, 22)) or all(landscape[y, 13] == 0 for y in range(12, 22))) and ((on_ground and on_ground) and on_ground)):
                            if on_ground:
                                if on_ground:
                                    action[Mario.KEY_LEFT] = 1
            else:
                if (any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12))):
                    action[Mario.KEY_DOWN] = 0
    else:
        if can_jump:
            if ((on_ground and can_jump) and (enemies and any((int(ek) in list(range(2, 14))) and ((-16 <= mario_pos[1] - ey <= 32) and (-32 <= ex - mario_pos[0] <= 48)) for ek, ex, ey in enemies))):
                action[Mario.KEY_JUMP] = 1
        else:
            action[Mario.KEY_RIGHT] = 1

