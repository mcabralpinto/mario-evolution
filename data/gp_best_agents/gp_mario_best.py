
# Evolved Mario Controller
# Fitness: 9272.816172390503


def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
    # INDIVIDUAL GENERATED CODE vvv

    if (not can_jump):
        pass
        pass
    else:
        if (can_jump or can_jump):
            action[Mario.KEY_JUMP] = 1
            action[Mario.KEY_JUMP] = 1
        else:
            pass
    if (any((ek == 8) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies) and (landscape is not None and 0 <= 11 < landscape.shape[0] and 0 <= 11 < landscape.shape[1] and landscape[11, 11] == -10)):
        action[Mario.KEY_DOWN] = 1
    else:
        action[Mario.KEY_RIGHT] = 1
        if on_ground:
            if landscape[11,12] == 0 and landscape[12,12] == 0:
                if on_ground:
                    pass
                else:
                    if on_ground:
                        pass
                        if ((landscape is not None and 0 <= 8 < landscape.shape[0] and 0 <= 8 < landscape.shape[1] and landscape[8, 8] < 20) or on_ground):
                            if (can_jump or can_jump):
                                pass
                            else:
                                if on_ground:
                                    pass
                                else:
                                    pass
                            pass
                            action[Mario.KEY_SPEED] = 1
                            action[Mario.KEY_JUMP] = 1
                        else:
                            pass
                            pass
                    else:
                        pass
                    if landscape[11,12] == 0 and landscape[12,12] == 0:
                        pass
                    else:
                        pass
            else:
                action[Mario.KEY_DOWN] = 1
                if any((ek == 3) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies):
                    pass
                else:
                    if can_jump:
                        pass
                    else:
                        action[Mario.KEY_LEFT] = 1
            pass
        else:
            if landscape[11,12] == 0 and landscape[12,12] == 0:
                pass
            else:
                if can_jump:
                    if can_jump:
                        action[Mario.KEY_SPEED] = 1
                    else:
                        if (any((ek == 13) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies) and can_jump):
                            if can_jump:
                                pass
                            else:
                                pass
                        else:
                            action[Mario.KEY_RIGHT] = 1
                            if can_jump:
                                if can_jump:
                                    action[Mario.KEY_JUMP] = 1
                                else:
                                    if any((ek == 2) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies):
                                        if landscape[11,12] == 0 and landscape[12,12] == 0:
                                            if (any((ek == 13) and (abs(ex) <= 16) and (abs(ey) <= 16) for ex, ey, ek in enemies) and on_ground):
                                                action[Mario.KEY_SPEED] = 1
                                                action[Mario.KEY_SPEED] = 1
                                            else:
                                                pass
                                        else:
                                            if (not can_jump):
                                                if (can_jump or can_jump):
                                                    pass
                                                else:
                                                    pass
                                                action[Mario.KEY_JUMP] = 1
                                                if any((ek == 8) and (abs(ex) <= 32) and (abs(ey) <= 32) for ex, ey, ek in enemies):
                                                    pass
                                                else:
                                                    pass
                                            else:
                                                pass
                                    else:
                                        pass
                                    if can_jump:
                                        pass
                                    else:
                                        if can_jump:
                                            pass
                                        else:
                                            action[Mario.KEY_LEFT] = 1
                                        pass
                            else:
                                action[Mario.KEY_SPEED] = 1
                else:
                    action[Mario.KEY_SPEED] = 1
            action[Mario.KEY_SPEED] = 1
            pass
            pass
            action[Mario.KEY_JUMP] = 1

