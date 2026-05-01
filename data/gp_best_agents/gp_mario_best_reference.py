def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):
    if action is None:
        action = [0] * 5

    if landscape[12][12] != -11:
        if can_jump:
            action[Mario.KEY_JUMP] = 1
        elif on_ground:
            action[Mario.KEY_JUMP] = 0
    else:
        action[Mario.KEY_SPEED] = 1

    if landscape[10][10] != 16:
        action[Mario.KEY_SPEED] = 1

    if landscape[10][12] != 21:
        if enemies[11][12] != Sprite.KIND_SPIKY:
            if on_ground:
                if enemies[10][11] != Sprite.KIND_GOOMBA:
                    if enemies[11][10] != Sprite.KIND_SPIKY_WINGED:
                        action[Mario.KEY_RIGHT] = 1
            else:
                if enemies[12][10] != Sprite.KIND_BULLET_BILL:
                    if can_jump:
                        action[Mario.KEY_DOWN] = 0
                else:
                    if can_jump:
                        action[Mario.KEY_SPEED] = 0
    else:
        action[Mario.KEY_DOWN] = 1

    return action